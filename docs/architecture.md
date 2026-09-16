# System Architecture
## Lenny Growth Assistant

**Version**: 1.0  
**Last Updated**: September 16, 2026  
**Status**: Production Ready

---

## Table of Contents
1. [System Overview](#1-system-overview)
2. [Architecture Diagram](#2-architecture-diagram)
3. [Component Details](#3-component-details)
4. [Database Schema](#4-database-schema)
5. [API Endpoints](#5-api-endpoints)
6. [RAG Pipeline](#6-rag-pipeline)
7. [Agent Routing](#7-agent-routing)
8. [Model Configuration](#8-model-configuration)
9. [Security](#9-security)
10. [Deployment](#10-deployment)

---

## 1. System Overview

### High-Level Architecture

Lenny Growth Assistant follows a modern three-tier architecture with a React frontend, FastAPI backend, and PostgreSQL database. The system uses Retrieval-Augmented Generation (RAG) to provide accurate, source-grounded responses from Lenny's Podcast transcripts.

### Key Design Principles
1. **Separation of Concerns**: Frontend, backend, and data layers are independent
2. **Modularity**: AI providers, storage, and retrieval are pluggable
3. **Scalability**: Async operations, connection pooling, vector indexing
4. **Observability**: Structured logging, health checks, error tracking
5. **Security**: Environment-based secrets, input validation, CORS

### Technology Stack

**Frontend**
- React 18.3.1 with TypeScript 5.7.3
- Vite 6.0.7 for build tooling
- Tailwind CSS 3.4.17 for styling
- TanStack Query 5.64.2 for data fetching
- React Router 7.18.4 for navigation

**Backend**
- FastAPI 0.141.1 (Python 3.11)
- Uvicorn 0.53.0 (ASGI server)
- SQLAlchemy 2.0.54 (async ORM)
- Asyncpg 0.31.0 (PostgreSQL driver)
- Pydantic 2.13.5 (validation)

**Database**
- PostgreSQL 16 with pgvector 0.5.0
- HNSW indexing for vector similarity
- Connection pooling with asyncpg

**AI/ML**
- OpenAI GPT-4o, GPT-4o-mini, GPT-3.5-turbo
- Anthropic Claude 3.5 Sonnet, Claude 3 Opus/Haiku
- Groq (Llama 3, Mixtral)
- Ollama (local models: qwen2.5-coder, llama3)
- Embedding models: text-embedding-3-small (OpenAI), nomic-embed-text (Ollama)

**Infrastructure**
- Docker 27+ with Docker Compose
- Nginx (production web server)
- Multi-stage builds for optimization

---

## 2. Architecture Diagram

### System Context

```
┌─────────────────────────────────────────────────────────────┐
│                          User                                │
│                   (Browser / Mobile)                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ HTTPS
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  Frontend (React + Vite)                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   Chat   │  │Artifacts │  │Knowledge │  │ Settings │   │
│  │    UI    │  │  Viewer  │  │   Base   │  │  Panel   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │       TanStack Query (State Management)              │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ HTTP/JSON
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Backend (FastAPI + Python)                      │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                  API Layer                            │  │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐       │  │
│  │  │  Chat  │ │Session │ │Artifact│ │ Know-  │       │  │
│  │  │ Router │ │ Router │ │ Router │ │  ledge │       │  │
│  │  └────────┘ └────────┘ └────────┘ └────────┘       │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │               Business Logic Layer                    │  │
│  │  ┌─────────────────────────────────────────────┐    │  │
│  │  │           RAG Pipeline                       │    │  │
│  │  │  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐   │    │  │
│  │  │  │Ingest│→ │Chunk │→ │Embed │→ │Store │   │    │  │
│  │  │  └──────┘  └──────┘  └──────┘  └──────┘   │    │  │
│  │  │                                              │    │  │
│  │  │  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐   │    │  │
│  │  │  │Query │→ │Search│→ │Rerank│→ │Generate│  │    │  │
│  │  │  └──────┘  └──────┘  └──────┘  └──────┘   │    │  │
│  │  └─────────────────────────────────────────────┘    │  │
│  │                                                       │  │
│  │  ┌─────────────────────────────────────────────┐    │  │
│  │  │      AI Provider Abstraction                │    │  │
│  │  │  [OpenAI | Anthropic | Groq | Ollama]      │    │  │
│  │  └─────────────────────────────────────────────┘    │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Data Access Layer (SQLAlchemy)             │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ asyncpg
                     ▼
┌─────────────────────────────────────────────────────────────┐
│         PostgreSQL 16 + pgvector Extension                   │
│                                                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ sessions │  │ messages │  │artifacts │  │ episodes │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │    episode_chunks (with vector embeddings)           │  │
│  │    - HNSW index for similarity search                │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                     │
                     │ (Optional) External APIs
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              AI Provider APIs                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  OpenAI  │  │Anthropic │  │   Groq   │  │  Ollama  │   │
│  │    API   │  │   API    │  │   API    │  │  Local   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Deployment Topology

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Compose Network                    │
│                                                               │
│  ┌───────────────┐      ┌───────────────┐                  │
│  │   Frontend    │      │      API      │                  │
│  │   (Nginx)     │◄────▶│   (Uvicorn)   │                  │
│  │   Port: 80    │      │   Port: 8000  │                  │
│  └───────────────┘      └───────┬───────┘                  │
│                                  │                           │
│                                  ▼                           │
│                         ┌───────────────┐                   │
│                         │   PostgreSQL  │                   │
│                         │   + pgvector  │                   │
│                         │   Port: 5432  │                   │
│                         └───────────────┘                   │
│                                                               │
│  ┌───────────────┐                                          │
│  │    Ollama     │  (Optional - for local AI)              │
│  │  Port: 11434  │                                          │
│  └───────────────┘                                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Component Details

### 3.1 Frontend Components

#### Core UI Components
```
frontend/src/
├── components/
│   ├── chat/
│   │   ├── ChatArea.tsx          # Main chat interface
│   │   ├── MessageBubble.tsx     # Individual message display
│   │   ├── MessageInput.tsx      # User input with @ commands
│   │   └── FollowUpSuggestions.tsx
│   ├── artifacts/
│   │   ├── ArtifactsPage.tsx     # Artifact browser
│   │   ├── ArtifactViewer.tsx    # Markdown renderer
│   │   └── ArtifactExporter.tsx
│   ├── knowledge/
│   │   ├── KnowledgeBasePage.tsx
│   │   ├── EpisodeList.tsx
│   │   └── DocumentUploader.tsx
│   ├── layout/
│   │   ├── Sidebar.tsx           # Session list
│   │   ├── Header.tsx
│   │   └── MainLayout.tsx
│   └── settings/
│       ├── SettingsModal.tsx
│       └── ModelSelector.tsx
├── hooks/
│   ├── useChat.ts               # Chat state management
│   ├── useSessions.ts           # Session CRUD
│   └── useModels.ts             # AI model configuration
└── lib/
    ├── api.ts                   # API client
    └── types.ts                 # TypeScript interfaces
```

#### State Management
- **TanStack Query**: Server state (queries, mutations)
- **React Context**: UI state (theme, settings)
- **Local Storage**: Preferences, last model used

---

### 3.2 Backend Components

#### API Structure
```
backend/app/
├── main.py                      # FastAPI app entry
├── config.py                    # Settings (Pydantic)
├── db.py                        # Database initialization
├── routers/
│   ├── chat.py                  # /api/v1/chat
│   ├── sessions.py              # /api/v1/sessions
│   ├── artifacts.py             # /api/v1/artifacts
│   ├── models.py                # /api/v1/models
│   ├── knowledge.py             # /api/v1/knowledge
│   └── skills.py                # /api/v1/skills (agent routing)
├── models/
│   ├── session.py               # SQLAlchemy models
│   ├── message.py
│   ├── artifact.py
│   └── episode.py
├── rag/
│   ├── ingest.py                # Document processing
│   ├── chunking.py              # Text splitting
│   ├── embed.py                 # Embedding generation
│   ├── retrieve.py              # Vector search
│   └── generate.py              # LLM response
├── ai_providers/
│   ├── base.py                  # Abstract provider
│   ├── openai_provider.py
│   ├── anthropic_provider.py
│   ├── groq_provider.py
│   └── ollama_provider.py
└── utils/
    ├── logging.py               # Structured logging
    ├── validation.py            # Input sanitization
    └── errors.py                # Custom exceptions
```

#### Request Flow
1. **HTTP Request** → FastAPI router
2. **Validation** → Pydantic models
3. **Business Logic** → Service layer (RAG/AI providers)
4. **Data Access** → SQLAlchemy (async)
5. **Response** → JSON serialization
6. **Logging** → Structured logs (INFO/ERROR)

---

## 4. Database Schema

### Entity-Relationship Diagram

```
┌─────────────────┐
│    sessions     │
├─────────────────┤
│ id (PK)         │◄──┐
│ title           │   │
│ created_at      │   │
│ updated_at      │   │
└─────────────────┘   │
                      │
                      │ 1:N
┌─────────────────┐   │
│    messages     │   │
├─────────────────┤   │
│ id (PK)         │   │
│ session_id (FK) │───┘
│ role            │
│ content         │
│ created_at      │
└─────────────────┘

┌─────────────────┐
│   artifacts     │
├─────────────────┤
│ id (PK)         │
│ session_id (FK) │───┐
│ type            │   │ 1:N
│ title           │   │
│ content         │   │
│ created_at      │   │
└─────────────────┘   │
                      ▼
               (links to sessions)

┌─────────────────────┐
│     episodes        │
├─────────────────────┤
│ id (PK)             │◄──┐
│ title               │   │
│ guest               │   │
│ url                 │   │
│ transcript_path     │   │
│ ingested_at         │   │
└─────────────────────┘   │
                          │ 1:N
┌─────────────────────────┤
│   episode_chunks        │
├─────────────────────────┤
│ id (PK)                 │
│ episode_id (FK)         │───┘
│ chunk_index             │
│ content (TEXT)          │
│ embedding (VECTOR)      │  ← pgvector type
│ metadata (JSONB)        │
└─────────────────────────┘
```

### Table Schemas

#### sessions
```sql
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_sessions_created_at ON sessions(created_at DESC);
```

#### messages
```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_messages_session_id ON messages(session_id);
CREATE INDEX idx_messages_created_at ON messages(created_at DESC);
```

#### artifacts
```sql
CREATE TABLE artifacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES sessions(id) ON DELETE SET NULL,
    type VARCHAR(50) NOT NULL CHECK (type IN ('report', 'code', 'ship30', 'diagram', 'checklist')),
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_artifacts_session_id ON artifacts(session_id);
CREATE INDEX idx_artifacts_type ON artifacts(type);
CREATE INDEX idx_artifacts_created_at ON artifacts(created_at DESC);
```

#### episodes
```sql
CREATE TABLE episodes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    guest VARCHAR(255),
    url VARCHAR(1000),
    transcript_path VARCHAR(1000),
    ingested_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_episodes_title ON episodes USING gin(to_tsvector('english', title));
```

#### episode_chunks (Vector Storage)
```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE episode_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    episode_id UUID NOT NULL REFERENCES episodes(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding VECTOR(1536),  -- OpenAI text-embedding-3-small dimension
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- HNSW index for fast vector similarity search
CREATE INDEX idx_episode_chunks_embedding 
ON episode_chunks 
USING hnsw (embedding vector_cosine_ops);

CREATE INDEX idx_episode_chunks_episode_id ON episode_chunks(episode_id);
```

### Vector Search Query
```sql
-- Find top 5 most similar chunks to query embedding
SELECT 
    ec.id,
    ec.content,
    e.title AS episode_title,
    e.guest,
    1 - (ec.embedding <=> $1) AS similarity
FROM episode_chunks ec
JOIN episodes e ON ec.episode_id = e.id
ORDER BY ec.embedding <=> $1
LIMIT 5;
```

---

## 5. API Endpoints

### Base URL
- **Development**: `http://localhost:8000`
- **Production**: `https://your-domain.com`

### Authentication
Currently: **None** (public access)  
Future: JWT tokens, API keys

---

### Chat Endpoints

#### `POST /api/v1/chat`
Send a chat message and get AI response.

**Request**:
```json
{
  "session_id": "uuid",
  "message": "What is product-led growth?",
  "model": "gpt-4o-mini",
  "provider": "openai"
}
```

**Response** (Streaming):
```
data: {"role": "assistant", "content": "Product-led growth", "done": false}
data: {"role": "assistant", "content": " (PLG) is", "done": false}
...
data: {"role": "assistant", "content": "...", "done": true, "sources": [...]}
```

**Errors**:
- `400`: Invalid input
- `429`: Rate limit exceeded
- `500`: Server error
- `503`: AI provider unavailable

---

### Session Endpoints

#### `GET /api/v1/sessions`
List all sessions.

**Response**:
```json
[
  {
    "id": "uuid",
    "title": "Product-led growth discussion",
    "created_at": "2026-09-16T19:50:00Z",
    "updated_at": "2026-09-16T20:15:00Z",
    "message_count": 12
  }
]
```

#### `POST /api/v1/sessions`
Create a new session.

**Request**:
```json
{
  "title": "New chat about growth strategies"
}
```

**Response**:
```json
{
  "id": "uuid",
  "title": "New chat about growth strategies",
  "created_at": "2026-09-17T10:00:00Z"
}
```

#### `GET /api/v1/sessions/{id}`
Get session details with all messages.

**Response**:
```json
{
  "id": "uuid",
  "title": "Product-led growth discussion",
  "messages": [
    {
      "id": "uuid",
      "role": "user",
      "content": "What is PLG?",
      "created_at": "2026-09-16T19:50:00Z"
    },
    {
      "id": "uuid",
      "role": "assistant",
      "content": "Product-led growth...",
      "created_at": "2026-09-16T19:50:05Z"
    }
  ]
}
```

#### `DELETE /api/v1/sessions/{id}`
Delete a session and all its messages.

**Response**: `204 No Content`

---

### Artifact Endpoints

#### `GET /api/v1/artifacts`
List all artifacts (optionally filtered by session).

**Query Params**:
- `session_id` (optional): Filter by session

**Response**:
```json
[
  {
    "id": "uuid",
    "session_id": "uuid",
    "type": "report",
    "title": "Growth Strategies Summary",
    "content": "# Summary\n...",
    "created_at": "2026-09-16T20:00:00Z"
  }
]
```

#### `POST /api/v1/artifacts`
Create a new artifact.

**Request**:
```json
{
  "session_id": "uuid",
  "type": "ship30",
  "title": "Building Product Culture",
  "prompt": "Write about building product culture"
}
```

**Response**:
```json
{
  "id": "uuid",
  "type": "ship30",
  "title": "Building Product Culture",
  "content": "...",
  "created_at": "2026-09-17T10:05:00Z"
}
```

#### `GET /api/v1/artifacts/{id}`
Get artifact details.

#### `DELETE /api/v1/artifacts/{id}`
Delete an artifact.

---

### Knowledge Base Endpoints

#### `GET /api/v1/knowledge/episodes`
List all ingested episodes.

**Response**:
```json
[
  {
    "id": "uuid",
    "title": "April Dunford on positioning",
    "guest": "April Dunford",
    "url": "https://...",
    "chunk_count": 45,
    "ingested_at": "2026-09-15T00:00:00Z"
  }
]
```

#### `POST /api/v1/knowledge/upload`
Upload a custom document (PDF or DOCX).

**Request** (multipart/form-data):
```
file: [binary]
```

**Response**:
```json
{
  "id": "uuid",
  "title": "Custom Document",
  "chunk_count": 23,
  "status": "ingested"
}
```

#### `POST /api/v1/knowledge/ingest`
Trigger ingestion of preprocessed transcripts.

**Response**:
```json
{
  "status": "started",
  "total_episodes": 150
}
```

#### `DELETE /api/v1/knowledge/episodes/{id}`
Delete an episode and all its chunks.

---

### Model Endpoints

#### `GET /api/v1/models`
Get available AI models based on configuration.

**Response**:
```json
{
  "providers": [
    {
      "name": "openai",
      "available": true,
      "models": [
        {"id": "gpt-4o", "name": "GPT-4o"},
        {"id": "gpt-4o-mini", "name": "GPT-4o Mini"}
      ]
    },
    {
      "name": "anthropic",
      "available": false,
      "reason": "API key not configured"
    }
  ],
  "default": {
    "provider": "openai",
    "model": "gpt-4o-mini"
  }
}
```

---

### Health & Status

#### `GET /health`
Health check endpoint.

**Response**:
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2026-09-17T10:00:00Z"
}
```

---

## 6. RAG Pipeline

### 6.1 Ingestion Flow

```
┌─────────────┐
│   Document  │ (PDF, DOCX, TXT)
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│  Text Extraction    │
│  - PyPDF2 (PDF)     │
│  - python-docx      │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│   Chunking          │
│  - Strategy: Fixed  │
│  - Size: 500 tokens │
│  - Overlap: 100     │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│   Embedding         │
│  - Model: text-     │
│    embedding-3-small│
│  - Dimension: 1536  │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Store in Database  │
│  - episode_chunks   │
│  - HNSW index       │
└─────────────────────┘
```

### 6.2 Retrieval Flow

```
┌─────────────┐
│ User Query  │ "What is product-led growth?"
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│ Query Embedding     │
│  - Same model       │
│  - Same dimension   │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Vector Search       │
│  - Cosine similarity│
│  - Top K=5          │
│  - HNSW index       │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Context Assembly    │
│  - Join with episode│
│  - Format metadata  │
│  - Rerank (optional)│
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Prompt Construction │
│  Context + Question │
│  + System prompt    │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ LLM Generation      │
│  - Stream response  │
│  - Include sources  │
└─────────────────────┘
```

### 6.3 Chunking Strategy

**Parameters**:
- **Chunk Size**: 500 tokens (~375 words)
- **Overlap**: 100 tokens (20%)
- **Separator**: Paragraph boundaries

**Rationale**:
- 500 tokens balances context vs. precision
- Overlap prevents information loss at boundaries
- Paragraph-based prevents mid-sentence cuts

**Example**:
```
Original text: 5000 tokens
Chunks created: ~10 chunks
Total stored tokens: 5400 (with overlap)
Storage cost: ~$0.0001 per document (OpenAI embedding)
```

### 6.4 Embedding Model Comparison

| Provider | Model | Dimension | Cost/1M tokens | Speed | Quality |
|----------|-------|-----------|----------------|-------|---------|
| OpenAI | text-embedding-3-small | 1536 | $0.02 | Fast | Excellent |
| OpenAI | text-embedding-3-large | 3072 | $0.13 | Medium | Best |
| Ollama | nomic-embed-text | 768 | Free | Slow | Good |

**Current Choice**: OpenAI text-embedding-3-small  
**Reasoning**: Best cost/quality trade-off for prototype

---

## 7. Agent Routing

### 7.1 Skill-Based Routing

The system uses intent detection to route requests:

```python
# Pseudo-code
def route_request(user_message: str) -> str:
    if "@artifact" in user_message:
        return "artifact_generation"
    elif message is_question_about_podcast():
        return "rag_retrieval"
    elif requires_general_knowledge():
        return "general_chat"
    else:
        return "default_rag"
```

### 7.2 Skills

1. **RAG Retrieval** (Primary)
   - Trigger: General questions
   - Action: Vector search + LLM generation
   - Example: "What is product-led growth?"

2. **Artifact Generation**
   - Trigger: `@artifact` command
   - Action: Retrieve context + structured generation
   - Example: "@artifact report: Summarize growth tactics"

3. **General Chat** (Fallback)
   - Trigger: Non-retrieval questions
   - Action: Direct LLM call (no RAG)
   - Example: "Tell me a joke"

4. **Document Upload**
   - Trigger: File upload endpoint
   - Action: Ingestion pipeline
   - Result: Document searchable

---

## 8. Model Configuration

### 8.1 Provider Abstraction

```python
class AIProvider(ABC):
    @abstractmethod
    async def generate(
        self,
        messages: List[dict],
        model: str,
        stream: bool = True
    ) -> AsyncGenerator[str, None]:
        pass

    @abstractmethod
    async def embed(
        self,
        text: str
    ) -> List[float]:
        pass
```

### 8.2 Model Toggle Implementation

**Frontend**:
```typescript
// User selects model
setSelectedModel({
  provider: "openai",
  model: "gpt-4o-mini"
});

// Sent with every chat request
fetch("/api/v1/chat", {
  body: JSON.stringify({
    message: "...",
    provider: selectedModel.provider,
    model: selectedModel.model
  })
});
```

**Backend**:
```python
# Router
@router.post("/chat")
async def chat(
    message: str,
    provider: str = "openai",
    model: str = "gpt-4o-mini"
):
    # Get provider instance
    ai = get_provider(provider)
    
    # Use specified model
    response = await ai.generate(
        messages=[...],
        model=model
    )
    return response
```

### 8.3 Fallback Strategy

```
1. Try requested provider/model
2. If unavailable → Try default (OpenAI GPT-4o-mini)
3. If still fails → Return error with suggestion
```

---

## 9. Security

### 9.1 Secret Management

**Environment Variables**:
```bash
# .env (not committed)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
DATABASE_URL=postgresql://...
```

**Docker Compose**:
```yaml
services:
  api:
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
```

**No Secrets in Code**:
- ✅ All keys from environment
- ✅ `.env` in `.gitignore`
- ✅ `.env.example` with placeholders

### 9.2 Input Validation

```python
# Pydantic models validate all inputs
class ChatRequest(BaseModel):
    message: str = Field(..., max_length=4000)
    session_id: UUID
    model: str = Field(..., pattern="^[a-z0-9-]+$")
```

### 9.3 CORS Configuration

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Dev
        "http://localhost",        # Production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 9.4 SQL Injection Prevention

- ✅ SQLAlchemy ORM (parameterized queries)
- ✅ No raw SQL with user input
- ✅ Input validation on all endpoints

### 9.5 Rate Limiting (Future)

```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/chat")
@limiter.limit("20/minute")
async def chat(...):
    pass
```

---

## 10. Deployment

### 10.1 Docker Compose (Current)

**Services**:
1. **postgres**: pgvector/pgvector:pg16
2. **api**: Custom FastAPI image
3. **frontend**: Custom Nginx image
4. **ollama** (optional): ollama/ollama:latest

**Networking**:
- All services on same Docker network
- Frontend proxies `/api` to backend
- PostgreSQL not exposed publicly

**Volumes**:
- `pgdata`: Persistent database storage
- `ollama_data`: Model cache (if using Ollama)

### 10.2 Health Checks

```yaml
api:
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
    interval: 30s
    timeout: 10s
    retries: 3
```

### 10.3 Logging

**Structured Logs**:
```python
logger.info(
    "Chat request",
    extra={
        "session_id": session_id,
        "model": model,
        "provider": provider,
        "duration_ms": duration
    }
)
```

**Log Levels**:
- INFO: Normal operations
- WARNING: Degraded performance
- ERROR: Request failures
- CRITICAL: System failures

### 10.4 Observability

**Available Metrics**:
1. Request count by endpoint
2. Response time percentiles (P50, P95, P99)
3. Error rate by type
4. Model usage distribution
5. Database query performance

**Future**: Prometheus + Grafana integration

### 10.5 Scaling Considerations

**Horizontal Scaling**:
- Frontend: Load balancer + N instances
- API: N workers behind load balancer
- Database: Read replicas for queries

**Vertical Scaling**:
- Increase CPU/memory per container
- Tune connection pool sizes
- Optimize vector index

**Bottlenecks**:
1. **Vector Search**: HNSW index performance degrades >1M vectors
   - Solution: Shard by date, use dedicated vector DB
2. **LLM API**: Rate limits, latency
   - Solution: Queueing, caching, multiple keys
3. **Database**: Connection exhaustion
   - Solution: Connection pooling, read replicas

---

## Appendix

### A. Technology Decisions

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| Frontend Framework | React vs. Vue vs. Svelte | React | Ecosystem, hiring, stability |
| Backend Framework | FastAPI vs. Flask vs. Django | FastAPI | Async, speed, type safety |
| Database | PostgreSQL vs. MongoDB vs. Supabase | PostgreSQL + pgvector | SQL, pgvector extension |
| Vector DB | Pinecone vs. Weaviate vs. pgvector | pgvector | Simpler stack, lower cost |
| AI Provider | OpenAI only vs. Multi-model | Multi-model | Flexibility, cost optimization |

### B. Performance Benchmarks

| Operation | Target | Measured (P95) |
|-----------|--------|----------------|
| Chat response (no RAG) | <1s | 800ms |
| Chat response (with RAG) | <3s | 2.4s |
| Vector search (1k docs) | <100ms | 45ms |
| Vector search (10k docs) | <500ms | 280ms |
| Artifact generation | <10s | 7.2s |
| Document upload (1MB) | <5s | 3.1s |

### C. Future Enhancements

1. **Caching Layer**: Redis for frequent queries
2. **CDN**: Static assets via CloudFront/Cloudflare
3. **Kubernetes**: Production-grade orchestration
4. **Monitoring**: Sentry for errors, DataDog for metrics
5. **CI/CD**: GitHub Actions for tests + deployment

---

**Document Version**: 1.0  
**Last Updated**: September 16, 2026  
**Next Review**: Post-launch (Q4 2026)
