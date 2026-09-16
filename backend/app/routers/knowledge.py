from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc, delete
import subprocess
import os
import uuid
import asyncio
from pathlib import Path
from typing import List
from pydantic import BaseModel
from datetime import datetime

from app.db import get_db
from app.models.episode import Episode
from app.models.transcript_chunk import TranscriptChunk
from app.ai.factory import AIProviderFactory
from app.config import settings

router = APIRouter(prefix="/knowledge", tags=["knowledge"])

# Temp upload directory
UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

class EpisodeResponse(BaseModel):
    id: str
    title: str
    guest_name: str
    summary: str
    created_at: str
    metadata_json: dict
    key_frameworks: list
    expertise_tags: list

    class Config:
        from_attributes = True

def run_ingestion_script():
    """Runs the ingestion script as a subprocess"""
    script_path = Path(__file__).resolve().parent.parent / "scripts" / "ingest.py"
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    try:
        subprocess.run(
            ["python", str(script_path)],
            check=True,
            capture_output=True,
            text=True,
            env=env
        )
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Ingestion failed: {e.stderr}")


async def ingest_uploaded_file(file_path: str, title: str, guest_name: str, db: AsyncSession):
    """Ingest an uploaded text file into the vector database."""
    from app.rag.file_upload import extract_text_from_file, chunk_text

    try:
        text = extract_text_from_file(file_path)
    except Exception as e:
        raise ValueError(f"Failed to extract text: {str(e)}")

    if not text or not text.strip():
        raise ValueError("No text content found in file")

    # Create episode record
    episode = Episode(
        title=title,
        guest_name=guest_name,
        summary=f"Uploaded document: {title}",
        metadata_json={"source": "file_upload", "file_path": file_path},
        key_frameworks=[],
        expertise_tags=[]
    )
    db.add(episode)
    await db.flush()

    # Chunk the text
    chunks = chunk_text(text, chunk_size=1500, overlap=200)

    if not chunks:
        raise ValueError("Failed to create chunks from text")

    # Generate embeddings
    try:
        embedder = AIProviderFactory.get_embedding_provider()
        embeddings = await embedder.embed(chunks)
    except Exception as e:
        await db.rollback()
        raise ValueError(f"Embedding failed; the source was not indexed: {e}")

    # Save chunks
    for i, (chunk_text_str, embedding) in enumerate(zip(chunks, embeddings)):
        tc = TranscriptChunk(
            episode_id=episode.id,
            chunk_text=chunk_text_str,
            chunk_index=i,
            chapter_title=f"Section {i + 1}",
            embedding=embedding
        )
        db.add(tc)

    await db.commit()
    return len(chunks)


@router.get("/episodes")
async def get_episodes(db: AsyncSession = Depends(get_db)):
    """List all ingested episodes"""
    result = await db.execute(select(Episode).order_by(desc(Episode.created_at)))
    episodes = result.scalars().all()

    response = []
    for ep in episodes:
        # Count chunks for this episode
        chunk_count = await db.execute(
            select(TranscriptChunk).where(TranscriptChunk.episode_id == ep.id)
        )
        chunk_total = len(chunk_count.scalars().all())

        response.append({
            "id": str(ep.id),
            "title": ep.title,
            "guest_name": ep.guest_name,
            "summary": ep.summary or "",
            "created_at": ep.created_at.isoformat(),
            "metadata_json": ep.metadata_json or {},
            "key_frameworks": ep.key_frameworks or [],
            "expertise_tags": ep.expertise_tags or [],
            "chunk_count": chunk_total
        })
    return response


@router.get("/episodes/{episode_id}")
async def get_episode(episode_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Episode).where(Episode.id == episode_id))
    episode = result.scalar_one_or_none()
    if not episode:
        raise HTTPException(status_code=404, detail="Knowledge source not found")
    chunks = await db.execute(
        select(TranscriptChunk).where(TranscriptChunk.episode_id == episode.id).order_by(TranscriptChunk.chunk_index)
    )
    return {
        "id": str(episode.id),
        "title": episode.title,
        "guest_name": episode.guest_name,
        "summary": episode.summary or "",
        "created_at": episode.created_at.isoformat(),
        "metadata_json": episode.metadata_json or {},
        "chunk_count": len(chunks.scalars().all()),
    }


@router.delete("/episodes/{episode_id}")
async def delete_episode(episode_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Episode).where(Episode.id == episode_id))
    episode = result.scalar_one_or_none()
    if not episode:
        raise HTTPException(status_code=404, detail="Knowledge source not found")
    source_path = (episode.metadata_json or {}).get("file_path")
    await db.delete(episode)
    await db.commit()
    if source_path:
        try:
            Path(source_path).unlink(missing_ok=True)
        except OSError:
            pass
    return {"status": "deleted", "id": str(episode_id)}


@router.post("/ingest")
async def trigger_ingestion(background_tasks: BackgroundTasks):
    """Trigger the Lenny transcript ingestion process"""
    background_tasks.add_task(run_ingestion_script)
    return {
        "status": "ingestion_started",
        "message": "Ingestion of Lenny podcast transcripts has been started in the background."
    }


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    title: str = "",
    guest_name: str = "",
    db: AsyncSession = Depends(get_db)
):
    """Upload a document (.txt, .md, .pdf, .docx) and ingest it into the knowledge base."""
    # Validate file type
    allowed_extensions = {'.txt', '.md', '.pdf', '.docx'}
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_ext}. Allowed: {', '.join(allowed_extensions)}"
        )

    # Save uploaded file
    file_id = str(uuid.uuid4())
    save_path = UPLOAD_DIR / f"{file_id}{file_ext}"
    try:
        content = await file.read()
        with open(save_path, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # Use filename as title if not provided
    if not title:
        title = Path(file.filename).stem.replace('_', ' ').replace('-', ' ').title()
    if not guest_name:
        guest_name = "Uploaded Document"

    try:
        chunk_count = await ingest_uploaded_file(str(save_path), title, guest_name, db)
        return {
            "status": "success",
            "message": f"Successfully ingested '{title}' ({chunk_count} chunks)",
            "episode_title": title,
            "chunk_count": chunk_count
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")
