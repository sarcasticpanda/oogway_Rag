"""Test Supabase connection and check database state."""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def test():
    url = os.getenv("DATABASE_URL", "")
    # asyncpg needs plain postgresql:// scheme
    url = url.replace("postgresql+asyncpg://", "postgresql://")
    print(f"Connecting to: {url.split('@')[-1]}")
    try:
        conn = await asyncpg.connect(url, timeout=15)
        print("SUCCESS: Connected to Supabase PostgreSQL.")
        
        # Check pgvector
        try:
            v = await conn.fetchval("SELECT extversion FROM pg_extension WHERE extname = 'vector'")
            print(f"pgvector extension: {v or 'NOT INSTALLED'}")
        except Exception as e:
            print(f"pgvector check failed: {e}")
        
        # List tables
        rows = await conn.fetch(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name"
        )
        print(f"\nTables in public schema ({len(rows)}):")
        for r in rows:
            print(f"  - {r['table_name']}")
        
        # Count episodes / chunks if tables exist
        tables = [r['table_name'] for r in rows]
        if 'episodes' in tables:
            count = await conn.fetchval("SELECT COUNT(*) FROM episodes")
            print(f"\nEpisodes: {count}")
        if 'transcript_chunks' in tables:
            count = await conn.fetchval("SELECT COUNT(*) FROM transcript_chunks")
            print(f"Transcript chunks: {count}")
        if 'sessions' in tables:
            count = await conn.fetchval("SELECT COUNT(*) FROM sessions")
            print(f"Sessions: {count}")
        
        await conn.close()
    except Exception as e:
        print(f"CONNECTION FAILED: {type(e).__name__}: {str(e)[:300]}")

asyncio.run(test())