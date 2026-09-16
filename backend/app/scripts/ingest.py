#!/usr/bin/env python3
"""
Ingestion script to parse Lenny podcast transcripts and preprocessed knowledge
from lenny-rag-mcp-main and index into PostgreSQL with pgvector embeddings.
"""

import os
import sys
import json
import asyncio
import argparse
from pathlib import Path
from typing import List, Dict, Any
from sqlalchemy import select, delete

# Ensure parent directory is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.config import settings
from app.db import AsyncSessionLocal, init_db
from app.models.episode import Episode
from app.models.transcript_chunk import TranscriptChunk
from app.ai.factory import AIProviderFactory

DEFAULT_PREPROCESSED_DIR = Path(__file__).resolve().parents[4] / "lenny-rag-mcp-main" / "preprocessed"
DEFAULT_TRANSCRIPTS_DIR = Path(__file__).resolve().parents[4] / "lenny-rag-mcp-main" / "transcripts"

async def ingest_transcripts(
    preprocessed_dir: Path,
    transcripts_dir: Path,
    limit: int | None = None,
    rebuild: bool = False
):
    print(f"[*] Starting Lenny Transcript Ingestion...")
    print(f"   Preprocessed Path: {preprocessed_dir}")
    print(f"   Transcripts Path:  {transcripts_dir}")
    print(f"   Database:          {settings.DATABASE_URL.split('@')[-1]}")

    if not preprocessed_dir.exists():
        print(f"[ERROR] Preprocessed directory does not exist: {preprocessed_dir}")
        return

    # Initialize tables
    await init_db()

    embedder = AIProviderFactory.get_embedding_provider()
    print(f"   Embedding Model:   {settings.EMBEDDING_PROVIDER} ({settings.EMBEDDING_MODEL})")

    json_files = sorted(list(preprocessed_dir.glob("*.json")))
    if limit:
        json_files = json_files[:limit]

    print(f"[*] Found {len(json_files)} episodes to process.")

    async with AsyncSessionLocal() as db:
        if rebuild:
            print("⚠️ Rebuilding database: clearing existing chunks and episodes...")
            await db.execute(delete(TranscriptChunk))
            await db.execute(delete(Episode))
            await db.commit()

        total_chunks_created = 0
        total_episodes_created = 0

        for idx, json_path in enumerate(json_files, 1):
            guest_stem = json_path.stem
            txt_file = transcripts_dir / f"{guest_stem}.txt"

            raw_transcript_lines = []
            if txt_file.exists():
                with open(txt_file, "r", encoding="utf-8", errors="replace") as f:
                    raw_transcript_lines = f.readlines()

            with open(json_path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except Exception as e:
                    print(f"⚠️ Error reading {json_path.name}: {e}")
                    continue

            ep_meta = data.get("episode", {})
            guest_name = ep_meta.get("guest") or guest_stem
            title = f"Lenny's Podcast: {guest_name}"
            summary = ep_meta.get("summary", "")
            expertise = ep_meta.get("expertise_tags", [])
            frameworks = ep_meta.get("key_frameworks", [])

            # Check if episode already exists
            res = await db.execute(select(Episode).where(Episode.title == title))
            existing_ep = res.scalar_one_or_none()

            if existing_ep:
                episode = existing_ep
            else:
                episode = Episode(
                    title=title,
                    guest_name=guest_name,
                    summary=summary,
                    expertise_tags=expertise,
                    key_frameworks=frameworks,
                    metadata_json={
                        "source_file": json_path.name
                    }
                )
                db.add(episode)
                await db.commit()
                await db.refresh(episode)
                total_episodes_created += 1

            # Prepare text chunks for embedding
            chunks_to_insert = []
            texts_to_embed = []

            # 1. Summary chunk
            summary_text = (
                f"Episode Summary: {guest_name} on Lenny's Podcast.\n"
                f"{summary}\n"
                f"Key Frameworks: {', '.join(frameworks)}\n"
                f"Topics: {', '.join(expertise)}"
            )
            texts_to_embed.append(summary_text)
            chunks_to_insert.append({
                "chapter_title": "Overview & Key Frameworks",
                "text": summary_text,
                "ts_start": "00:00:00",
                "ts_end": "00:05:00",
                "meta": {"type": "summary", "guest": guest_name}
            })

            # 2. Topic chunks
            for topic in data.get("topics", []):
                t_title = topic.get("title", "")
                t_summary = topic.get("summary", "")
                ts_start = topic.get("timestamp_start", "")
                ts_end = topic.get("timestamp_end", "")
                l_start = topic.get("line_start", 0)
                l_end = topic.get("line_end", 0)

                # Extract excerpt from raw transcript if available
                excerpt = ""
                if raw_transcript_lines and l_start < len(raw_transcript_lines):
                    excerpt_lines = raw_transcript_lines[l_start:min(l_end, l_start + 40)]
                    excerpt = "".join(excerpt_lines).strip()

                chunk_content = (
                    f"Topic: {t_title}\n"
                    f"Summary: {t_summary}\n"
                )
                if excerpt:
                    chunk_content += f"Transcript Excerpt:\n{excerpt[:800]}"

                texts_to_embed.append(chunk_content)
                chunks_to_insert.append({
                    "chapter_title": t_title,
                    "text": chunk_content,
                    "ts_start": ts_start,
                    "ts_end": ts_end,
                    "meta": {"type": "topic", "guest": guest_name}
                })

            # 3. Key insights
            for insight in data.get("insights", [])[:5]:
                i_text = insight.get("text", "")
                i_context = insight.get("context", "")
                if i_text:
                    insight_chunk = f"Key Insight from {guest_name}:\n{i_text}\nContext: {i_context}"
                    texts_to_embed.append(insight_chunk)
                    chunks_to_insert.append({
                        "chapter_title": "Core Insight",
                        "text": insight_chunk,
                        "ts_start": "",
                        "ts_end": "",
                        "meta": {"type": "insight", "guest": guest_name}
                    })

            # Batch compute embeddings
            embeddings = await embedder.embed(texts_to_embed)

            # Insert chunks into database
            for idx2, (c_info, emb) in enumerate(zip(chunks_to_insert, embeddings)):
                chunk = TranscriptChunk(
                    episode_id=episode.id,
                    chunk_index=idx2,
                    chapter_title=c_info["chapter_title"],
                    chunk_text=c_info["text"],
                    timestamp_start=c_info["ts_start"],
                    timestamp_end=c_info["ts_end"],
                    embedding=emb,
                    metadata_json=c_info["meta"]
                )
                db.add(chunk)

            await db.commit()
            total_chunks_created += len(chunks_to_insert)
            print(f"[{idx}/{len(json_files)}] Ingested {guest_name}: {len(chunks_to_insert)} chunks")

        print(f"\n[SUCCESS] Ingestion complete! Total Episodes: {total_episodes_created}, Total Chunks: {total_chunks_created}")

def main():
    parser = argparse.ArgumentParser(description="Ingest Lenny podcast transcripts into pgvector")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of episodes to process (for testing)")
    parser.add_argument("--rebuild", action="store_true", help="Clear existing records and reindex")
    parser.add_argument("--preprocessed-dir", type=str, default=str(DEFAULT_PREPROCESSED_DIR))
    parser.add_argument("--transcripts-dir", type=str, default=str(DEFAULT_TRANSCRIPTS_DIR))
    args = parser.parse_args()

    asyncio.run(
        ingest_transcripts(
            preprocessed_dir=Path(args.preprocessed_dir),
            transcripts_dir=Path(args.transcripts_dir),
            limit=args.limit,
            rebuild=args.rebuild
        )
    )

if __name__ == "__main__":
    main()
