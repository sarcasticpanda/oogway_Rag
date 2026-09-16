"""Fix stale models in existing sessions so old chats work."""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def fix():
    url = os.getenv("DATABASE_URL", "").replace("postgresql+asyncpg://", "postgresql://")
    conn = await asyncpg.connect(url, timeout=15)
    
    fixed = await conn.fetchval(
        "UPDATE sessions SET active_model = 'openai/gpt-oss-20b' "
        "WHERE active_model IN ('llama3.1', 'llama3-70b-8192', 'llama3-8b', 'mistral')"
    )
    print(f"Fixed {fixed} sessions with stale models.")
    
    rows = await conn.fetch("SELECT title, active_provider, active_model FROM sessions ORDER BY updated_at DESC LIMIT 5")
    for r in rows:
        print(f"  {r['title'][:40]:40} | {r['active_provider']} | {r['active_model']}")
    await conn.close()

asyncio.run(fix())