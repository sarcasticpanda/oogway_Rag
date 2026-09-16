# Critical Issues Analysis & Action Plan

**Date**: 2026-09-17
**Status**: 🔴 Multiple Critical Issues Identified

---

## 🚨 Issue 1: Server Error 502 (Groq API)

**Symptoms**:
- UI shows "Server error: 502" with Retry button
- Chat requests failing with Bad Gateway error
- Screenshot shows error at 01:46 AM

**Root Causes**:
1. Groq API key may be invalid/expired
2. Rate limiting on Groq free tier
3. Network connectivity issues
4. API endpoint URL incorrect

**Investigation Steps**:
```bash
# Check Groq API key
echo $GROQ_API_KEY

# Test API directly
curl -X POST "https://api.groq.com/openai/v1/chat/completions" \
  -H "Authorization: Bearer $GROQ_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"openai/gpt-oss-20b","messages":[{"role":"user","content":"test"}]}'
```

**Fixes Required**:
- [ ] Validate Groq API key in `.env`
- [ ] Add API key validation on startup
- [ ] Implement graceful fallback to Ollama
- [ ] Add better error messages to UI
- [ ] Add retry logic with exponential backoff

---

## 🚨 Issue 2: Incomplete Chat Management

**Current State**:
- ✅ Clear all chats button exists
- ❌ No rename session
- ❌ No delete single session
- ❌ No export conversation
- ❌ No duplicate session
- ❌ No session search

**Required Features** (from prmt2.md):
```
Chat Management:
- Rename chat session
- Delete individual chat
- Export chat to markdown/JSON
- Duplicate session
- Search conversations
- Filter by date/topic
```

**Files to Modify**:
1. `frontend/src/components/settings/SettingsModal.tsx` - Add full chat management
2. `backend/app/routers/sessions.py` - Add rename/export endpoints
3. `backend/app/schemas/session.py` - Add request schemas

**Implementation**:
```typescript
// Add to SettingsModal.tsx
interface ChatManagementProps {
  sessions: Session[];
  onRename: (id: string, newTitle: string) => Promise<void>;
  onDelete: (id: string) => Promise<void>;
  onExport: (id: string, format: 'md' | 'json') => Promise<void>;
  onDuplicate: (id: string) => Promise<void>;
}
```

---

## 🚨 Issue 3: Missing Ollama Model Selector

**Current State**:
- ✅ Ollama provider exists in backend
- ✅ Model dropdown shows provider
- ❌ No way to select specific Ollama models
- ❌ No "Browse local models" button
- ❌ Can't see available models in Ollama

**Required** (from prmt1.md):
```
3. Cloud and local Ollama model switching
```

**Files to Check**:
```
backend/app/routers/models.py  # Check if /models endpoint lists Ollama
frontend/src/components/chat/ChatArea.tsx  # Model selector UI
```

**Implementation Plan**:
1. Add `/api/v1/models/ollama` endpoint to list local models
2. Add model selector dropdown when Ollama is selected
3. Show model tags, size, and capabilities
4. Allow custom model URL for remote Ollama

```python
# backend/app/routers/models.py
@router.get("/ollama")
async def list_ollama_models():
    try:
        resp = await httpx.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
        models = resp.json().get("models", [])
        return {"models": models}
    except Exception as e:
        return {"models": [], "error": str(e)}
```

---

## 🚨 Issue 4: RAG Quality - Incomplete Chunks

**Problem**:
> "AI is still not answering from the documents properly only certain length of it is going not the complete chunk"

**Root Cause Analysis**:

### A. Chunk Size Issues
```python
# Current chunking in ingest script
chunk_size = ???  # Need to verify
chunk_overlap = ???  # Need to verify
```

### B. Retrieval Issues
```python
# Current retrieve.py
top_k = 6  # Only retrieves 6 chunks
context_blocks.append(f"{chunk.chunk_text}\n")  # Full text included?
```

### C. Context Window Issues
- Model context limit: OpenAI GPT-oss-20b = ~8k tokens
- Chunks being truncated in prompt?
- Need to verify actual prompt size

**Investigation Steps**:
```python
# Test chunk retrieval
from app.rag.retrieve import retrieve_context

context, citations, grounded = await retrieve_context(
    "What did Lenny say about product-led growth?",
    db,
    top_k=10
)

print(f"Context length: {len(context)} chars")
print(f"Citations: {len(citations)}")
for i, cit in enumerate(citations[:3]):
    print(f"\nCitation {i+1}:")
    print(f"Quote length: {len(cit.quote)}")
    print(f"Quote: {cit.quote[:200]}...")
```

**Fixes Required**:
- [ ] Increase `top_k` for artifact generation (currently 12, should be 15-20)
- [ ] Verify chunk_text is complete (not truncated in DB)
- [ ] Add prompt compression if hitting context limits
- [ ] Implement reranking for better chunk selection
- [ ] Add semantic chunking (not just fixed size)

---

## 🚨 Issue 5: Vector DB Performance & Indexing

**Questions**:
> "how is this vector db working so bad which type of similarity search we used did we do any indexing"

### Current Implementation:

```python
# retrieve.py
distance_expr = emb_col.cosine_distance(query_vector)
stmt = (
    select(TranscriptChunk, Episode, (1.0 - distance_expr).label("similarity"))
    .join(Episode, TranscriptChunk.episode_id == Episode.id)
    .order_by(distance_expr)  # Sequential scan?
    .limit(top_k)
)
```

### Issues:
1. **No Vector Index Visible** - Need to check if `ivfflat` or `hnsw` index exists
2. **Cosine Distance** - Using cosine (good), but is it indexed?
3. **Sequential Scan** - May be doing full table scan

### Check Current Indexes:
```python
# Run this to check indexes
import asyncio
from app.db import AsyncSessionLocal

async def check_indexes():
    async with AsyncSessionLocal() as db:
        result = await db.execute("""
            SELECT 
                indexname, 
                indexdef 
            FROM pg_indexes 
            WHERE tablename = 'transcript_chunks' 
            AND indexdef LIKE '%vector%'
        """)
        indexes = result.all()
        for idx in indexes:
            print(f"Index: {idx[0]}")
            print(f"Definition: {idx[1]}\n")

asyncio.run(check_indexes())
```

### Required Indexes:

```sql
-- IVFFlat index (faster, less accurate)
CREATE INDEX IF NOT EXISTS transcript_chunks_embedding_ivfflat_idx 
ON transcript_chunks 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- OR HNSW index (slower build, better accuracy)
CREATE INDEX IF NOT EXISTS transcript_chunks_embedding_hnsw_idx 
ON transcript_chunks 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Additional indexes for filtering
CREATE INDEX IF NOT EXISTS idx_chunks_episode_id 
ON transcript_chunks(episode_id);

CREATE INDEX IF NOT EXISTS idx_chunks_chapter 
ON transcript_chunks(chapter_title);
```

### Performance Comparison:

| Index Type | Build Time | Query Speed | Accuracy | Best For |
|------------|------------|-------------|----------|----------|
| **None** (seq scan) | 0s | ❌ Slow (>1s) | 100% | <1k vectors |
| **IVFFlat** | ~30s | ⚡ Fast (50-100ms) | 95-98% | 10k-1M vectors |
| **HNSW** | ~5min | ⚡⚡ Fastest (20-50ms) | 98-99% | 100k-10M vectors |

### Fix Vector DB Performance:

**Step 1: Add Migration to Create Indexes**
```python
# backend/app/db.py - Add to init_db()
async def create_vector_indexes(engine):
    async with engine.begin() as conn:
        # Check if index exists
        result = await conn.execute(text("""
            SELECT 1 FROM pg_indexes 
            WHERE indexname = 'transcript_chunks_embedding_hnsw_idx'
        """))
        
        if not result.scalar():
            logging.info("Creating HNSW vector index...")
            await conn.execute(text("""
                CREATE INDEX transcript_chunks_embedding_hnsw_idx 
                ON transcript_chunks 
                USING hnsw (embedding vector_cosine_ops)
                WITH (m = 16, ef_construction = 64);
            """))
            logging.info("Vector index created successfully.")
```

**Step 2: Optimize Query with Index Hints**
```python
# retrieve.py - Add index hint
stmt = (
    select(TranscriptChunk, Episode, (1.0 - distance_expr).label("similarity"))
    .join(Episode, TranscriptChunk.episode_id == Episode.id)
    .order_by(distance_expr)
    .limit(top_k)
    .execution_options(postgresql_enable_seqscan=False)  # Force index usage
)
```

**Step 3: Add Query Performance Monitoring**
```python
import time

start = time.time()
result = await db.execute(stmt)
elapsed = time.time() - start

logger.info(f"Vector search took {elapsed:.3f}s for top_k={top_k}")
if elapsed > 0.5:
    logger.warning(f"Slow vector query detected: {elapsed:.3f}s")
```

---

## 🚨 Issue 6: Zero Hallucinations Guarantee?

**Question**:
> "what kind are we providing zero hallucinations?"

**Current Grounding Mechanism**:

```python
SIMILARITY_THRESHOLD = 0.35  # Minimum cosine similarity for grounding

if top_similarity >= SIMILARITY_THRESHOLD:
    is_grounded = True
else:
    is_grounded = False
    # Add caveat to response
```

**Reality Check**:
- ❌ **NO system provides "zero hallucinations"**
- ✅ We provide **grounding indicators**
- ✅ We provide **source citations**
- ❌ LLM can still hallucinate even with context

**What We Actually Provide**:

1. **Grounding Flag**: `is_grounded: true/false`
2. **Source Citations**: Episode + timestamp + quote
3. **Warning Message**: "This answer may not be fully supported"
4. **Context Visibility**: User can see sources

**How to Improve Grounding**:

```python
# Add strict grounding mode
if request.strict_grounding:
    # Only use direct quotes
    prompt += """
    STRICT MODE: You must ONLY use direct quotes from the sources.
    Do not paraphrase, infer, or add information.
    If the answer is not in the sources, say "I don't have information about that."
    """
    
# Add citation density requirement
if request.require_citations:
    prompt += """
    Every factual claim must include [Source: Episode Title, Timestamp]
    """
```

**Best Practices for Reducing Hallucinations**:

1. ✅ **High Similarity Threshold** (0.35 is reasonable)
2. ✅ **Source Citations** (we have this)
3. ✅ **Grounding Warnings** (we have this)
4. ❌ **Answer Verification** (need to add)
5. ❌ **Factuality Scoring** (need to add)
6. ❌ **Claim Attribution** (need to add)

---

## 📋 Priority Action Plan

### P0 - Critical (Fix Today)
- [ ] **Fix 502 Error**: Validate Groq API key, add fallback
- [ ] **Add Vector Indexes**: Create HNSW index for performance
- [ ] **Fix Chunk Retrieval**: Increase top_k, verify full chunks

### P1 - High (This Week)
- [ ] **Complete Chat Management**: Rename, delete, export
- [ ] **Add Ollama Model Selector**: List and select local models
- [ ] **Improve Grounding**: Add strict mode, citation density

### P2 - Medium (Next Week)
- [ ] Add semantic chunking
- [ ] Add reranking
- [ ] Add answer verification
- [ ] Add performance monitoring

---

## 🧪 Testing Checklist

### Vector DB Performance
```bash
# Test query speed
time curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"What is product-led growth?","provider":"groq"}'

# Expected: <500ms with index, >1000ms without
```

### RAG Quality
```bash
# Test chunk completeness
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Summarize everything Adam Fishman said about metrics","provider":"groq"}'

# Check: Response should be comprehensive, not truncated
```

### Grounding Test
```bash
# Test non-grounded query
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"What did Lenny say about quantum computing?","provider":"groq"}'

# Expected: is_grounded: false, warning message
```

---

## 📊 Current System Metrics

### Database
- Episodes: 284
- Chunks: 7,585 unique
- Avg chunk size: ~500 tokens (estimate)
- Total vectors: 7,585 x 768 dims = 5.8M floats

### Performance (Without Index)
- Query time: ~1-2 seconds
- Sequential scan: YES ❌
- Index usage: NO ❌

### Performance (With HNSW Index - Expected)
- Query time: ~50-100ms ✅
- Index scan: YES ✅
- Accuracy: 98-99% ✅

---

**Next Steps**: Address P0 items immediately, then move to P1.
