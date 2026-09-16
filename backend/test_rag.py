"""Test script to check database state and RAG quality."""
import asyncio
from app.db import AsyncSessionLocal
from sqlalchemy import text
from app.rag.retrieve import retrieve_context

async def main():
    async with AsyncSessionLocal() as db:
        # Check indexes
        result = await db.execute(text("""
            SELECT indexname FROM pg_indexes 
            WHERE tablename = 'transcript_chunks'
            ORDER BY indexname
        """))
        indexes = result.all()
        print("Current indexes:")
        for idx in indexes:
            print(f"  - {idx[0]}")
        
        # Check chunk statistics
        result2 = await db.execute(text("""
            SELECT 
                COUNT(*) as total_chunks,
                COUNT(DISTINCT episode_id) as episodes,
                AVG(LENGTH(chunk_text)) as avg_length,
                MIN(LENGTH(chunk_text)) as min_length,
                MAX(LENGTH(chunk_text)) as max_length
            FROM transcript_chunks
        """))
        stats = result2.fetchone()
        print(f"\nChunk Statistics:")
        print(f"  Total chunks: {stats[0]}")
        print(f"  Episodes: {stats[1]}")
        print(f"  Avg chunk length: {stats[2]:.0f} chars")
        print(f"  Min/Max length: {stats[3]} / {stats[4]}")
        
        # Test retrieval
        print("\n--- Testing Retrieval ---")
        ctx, citations, grounded = await retrieve_context(
            'What did Lenny guests say about product-led growth?',
            db,
            top_k=6
        )
        print(f"Grounded: {grounded}")
        print(f"Citations: {len(citations)}")
        print(f"Context length: {len(ctx)} chars")
        
        if citations:
            print("\nTop citations:")
            for i, c in enumerate(citations[:5], 1):
                print(f"  {i}. {c.episode_title}")
                print(f"     Similarity: {c.similarity_score:.4f}")
        
        # Show sample context
        print(f"\n--- Sample Context (first 500 chars) ---")
        print(ctx[:500] if ctx else "No context returned")

if __name__ == "__main__":
    asyncio.run(main())
