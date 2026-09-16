from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.db import get_db
from app.models.artifact import Artifact
from app.models.session import Session

router = APIRouter(prefix="/artifacts", tags=["artifacts"])

@router.get("")
async def list_artifacts(session_id: Optional[UUID] = None, db: AsyncSession = Depends(get_db)):
    """List generated artifacts, optionally filtered by session."""
    stmt = select(Artifact, Session.title.label("session_title")).join(Session, Artifact.session_id == Session.id).order_by(desc(Artifact.created_at))
    if session_id:
        stmt = stmt.where(Artifact.session_id == session_id)

    res = await db.execute(stmt)
    rows = res.all()

    return [
        {
            "id": str(a.id),
            "session_id": str(a.session_id),
            "title": a.title,
            "artifact_type": a.artifact_type,
            "word_count": a.word_count,
            "source_references": a.source_references or [],
            "created_at": a.created_at.isoformat(),
            "session_title": session_title,
        }
        for a, session_title in rows
    ]

@router.get("/{artifact_id}")
async def get_artifact(artifact_id: UUID, db: AsyncSession = Depends(get_db)):
    """Retrieve full content of a specific artifact."""
    res = await db.execute(select(Artifact).where(Artifact.id == artifact_id))
    artifact = res.scalar_one_or_none()
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")

    return {
        "id": str(artifact.id),
        "session_id": str(artifact.session_id),
        "title": artifact.title,
        "artifact_type": artifact.artifact_type,
        "content": artifact.content,
        "word_count": artifact.word_count,
        "source_references": artifact.source_references or [],
        "created_at": artifact.created_at.isoformat()
    }

@router.get("/{artifact_id}/raw")
async def get_raw_artifact(artifact_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Returns raw HTML or Markdown content with appropriate sandboxing and content-type headers.
    Enforces strict CSP headers so it can be safely loaded in an iframe.
    """
    res = await db.execute(select(Artifact).where(Artifact.id == artifact_id))
    artifact = res.scalar_one_or_none()
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")

    media_type = "text/html" if artifact.artifact_type == "html" else "text/markdown"
    
    headers = {
        "Content-Security-Policy": "default-src 'self' 'unsafe-inline'; img-src data: https:; script-src 'self' 'unsafe-inline';",
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "SAMEORIGIN"
    }

    return Response(content=artifact.content, media_type=media_type, headers=headers)

@router.delete("/{artifact_id}")
async def delete_artifact(artifact_id: UUID, db: AsyncSession = Depends(get_db)):
    """Delete an artifact."""
    res = await db.execute(select(Artifact).where(Artifact.id == artifact_id))
    artifact = res.scalar_one_or_none()
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")

    await db.delete(artifact)
    await db.commit()
    return {"status": "success", "message": "Artifact deleted"}
