import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
from app.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

class Base(DeclarativeBase):
    pass

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    async with engine.begin() as conn:
        # Only try to create pgvector extension if using PostgreSQL
        if "postgresql" in settings.DATABASE_URL:
            try:
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            except Exception:
                pass
            
            # Create HNSW index for fast vector similarity search
            try:
                await conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS transcript_chunks_embedding_idx
                    ON transcript_chunks
                    USING hnsw (embedding vector_cosine_ops)
                    WITH (m = 16, ef_construction = 64)
                """))
                logging.getLogger("lenny_assistant").info("HNSW vector index created")
            except Exception as e:
                logging.getLogger("lenny_assistant").warning(f"Failed to create HNSW index: {e}")
            
            # Create additional indexes for filtering
            try:
                await conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_chunks_episode_id 
                    ON transcript_chunks(episode_id)
                """))
                await conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_chunks_chapter
                    ON transcript_chunks(chapter_title)
                """))
                logging.getLogger("lenny_assistant").info("Additional indexes created")
            except Exception as e:
                logging.getLogger("lenny_assistant").warning(f"Failed to create filters indexes: {e}")
        
        # For SQLite, just create tables without vector extension
        await conn.run_sync(Base.metadata.create_all)
