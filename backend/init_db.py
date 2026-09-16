#!/usr/bin/env python3
"""Initialize database schema with all tables."""
import asyncio
from app.db import Base, engine, init_db
from app.models.episode import Episode
from app.models.transcript_chunk import TranscriptChunk
from app.models.session import Session
from app.models.message import Message
from app.models.artifact import Artifact
from app.models.agent_run import AgentRun

async def create_all_tables():
    """Create all database tables and enable pgvector."""
    print("🔧 Initializing database...")
    await init_db()
    print("✅ Database initialized successfully!")
    print("✅ Tables created: episodes, transcript_chunks, sessions, messages, artifacts, agent_runs")
    print("✅ pgvector extension enabled")

if __name__ == "__main__":
    asyncio.run(create_all_tables())
