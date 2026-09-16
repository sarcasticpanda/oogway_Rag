"""Check sessions stored in DB — their active models may be stale/wrong."""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def check():
    url = os.getenv("DATABASE_URL", "").replace("postgresql+asyncpg://", "postgresql://")
    conn = await asyncpg.connect(url, timeout=15)
    rows = await conn.fetch("SELECT id, title, active_provider, active_model, updated_at FROM sessions ORDER BY updated_at DESC LIMIT 10")
    print("Sessions in DB:")
    for r in rows:
        print(f"  {str(r['id'])[:8]}... | {r['title'][:40]:40} | provider={r['active_provider']} | model={r['active_model']}")
    
    # Count sessions with stale models
    stale = await conn.fetchval("SELECT COUNT(*) FROM sessions WHERE active_model IN ('llama3.1', 'llama3-70b-8192')")
    print(f"\nSessions with STALE models: {stale}")
    await conn.close()

asyncio.run(check())