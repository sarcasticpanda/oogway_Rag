# Lenny Growth Assistant

<div align="center">



**AI-powered Product & Growth Assistant grounded in Lenny's Podcast transcripts A take home assignment**

[Quick Start](#-quick-start) • [Features](#-features) • [Architecture](#-architecture) • [Documentation](#-documentation)

</div>

---

## 📖 Overview

Lenny Growth Assistant is an intelligent chat application that helps you learn about product management and growth strategies from Lenny's extensive podcast library. Built with modern AI capabilities and vector search, it provides contextual, accurate answers grounded in real expert knowledge.

###  Key Highlights

-  **RAG-Powered**: Vector search with pgvector for accurate, grounded responses
-  **Artifact Generation**: Create documents, code, diagrams, and essays
-  **Multi-Model Support**: Switch between OpenAI, Anthropic, Groq, or local Ollama
-  **Knowledge Base**: Upload custom documents and transcripts
-  **Session History**: Save and resume conversations
-  **Production-Ready**: Fully containerized with Docker

---

## Quick Start

### Prerequisites

- Docker & Docker Compose installed
- (Optional) API key for OpenAI, Anthropic, or Groq

### Option 1: Cloud AI Setup (Recommended - Fast & Easy)

**Perfect for: Production use, fast responses, no local GPU needed**

1. **Clone and setup**:
   ```bash
   git clone <your-repo-url>
   cd lenny-growth-assistant
   cp .env.example .env
   ```

2. **Add your API key** (edit `.env`):
   ```bash
   OPENAI_API_KEY=sk-your-key-here
   # or use ANTHROPIC_API_KEY, GROQ_API_KEY
   ```

3. **Launch the application**:
   ```bash
   docker-compose -f docker-compose.simple.yml up -d
   ```

4. **Access the app**:
   - 🌐 **Frontend**: http://localhost
   - 📚 **API Docs**: http://localhost:8000/docs
   - 🗄️ **PostgreSQL**: localhost:5432

### Option 2: Local AI with Ollama (Offline, Privacy-Focused)

**Perfect for: Offline use, data privacy, no API costs**

1. **Launch with Ollama**:
   ```bash
   docker-compose up -d
   ```
   
   ⚠️ **Note**: First start downloads ~3.7GB Ollama model (5-10 minutes)

2. **Access the app** at http://localhost

---

##  Features

### 💬 Intelligent Chat Interface
- Natural language conversations about product and growth
- Context-aware responses grounded in Lenny's podcast transcripts
- Real-time streaming responses
- Message history and follow-up questions

###  Artifact System
Generate various types of content:
- **Documents**: Reports, summaries, case studies
- **Code**: Implementation examples, snippets
- **Diagrams**: Flowcharts, architecture diagrams
- **Ship 30 Essays**: Twitter-style growth essays

### Multi-Model AI Support
Switch between providers on-the-fly:
- **OpenAI**: GPT-4o, GPT-4o-mini, GPT-3.5-turbo
- **Anthropic**: Claude 3.5 Sonnet, Claude 3 Opus/Haiku
- **Groq**: Llama 3, Mixtral (super fast inference)
- **Ollama**: Local models (qwen2.5-coder, llama3, etc.)

###  Knowledge Base Management
- Upload PDF documents and DOCX files
- Ingest Lenny's podcast transcripts
- Vector search with pgvector
- Chunk-based retrieval for accuracy

###  Session Management
- Save conversation history
- Resume previous chats
- Organize by date
- Export conversations

---

## 🏗️ Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   React     │─────▶│   FastAPI    │─────▶│ PostgreSQL  │
│  Frontend   │      │   Backend    │      │  + pgvector │
│  (Vite)     │      │   (Python)   │      │             │
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │  AI Providers│
                     │ OpenAI/Claude│
                     │  Groq/Ollama │
                     └──────────────┘
```

### Tech Stack

**Frontend**
- React 18 + TypeScript
- Vite for fast builds
- Tailwind CSS for styling
- TanStack Query for data fetching
- React Router for navigation

**Backend**
- FastAPI (Python 3.11)
- PostgreSQL 16 with pgvector
- SQLAlchemy 2.0 (async)
- Asyncpg for database
- Multi-model AI integration

**Infrastructure**
- Docker & Docker Compose
- Nginx for production serving
- Multi-stage builds for optimization

---

##  Available Commands

### Docker Commands

```bash
# Start services (cloud AI)
docker-compose -f docker-compose.simple.yml up -d

# Start services (with Ollama)
docker-compose up -d

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f api
docker-compose logs -f frontend

# Stop services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v

# Rebuild containers
docker-compose build --no-cache

# Check service status
docker-compose ps
```

### Development Commands

```bash
# Frontend development
cd frontend
npm install
npm run dev          # Start dev server at http://localhost:5173
npm run build        # Build for production
npm run preview      # Preview production build

# Backend development
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload  # Start with hot reload
pytest                         # Run tests
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root (copy from `.env.example`):

```bash
# AI Provider (choose one or configure multiple)
AI_PROVIDER=openai              # openai | anthropic | groq | ollama
DEFAULT_MODEL=gpt-4o-mini

# API Keys (only for cloud providers)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=...
GROQ_API_KEY=...

# Embedding Configuration
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIM=1536

# Database (auto-configured in Docker)
DATABASE_URL=postgresql+asyncpg://lenny:lenny_secret@postgres:5432/lenny_db

# CORS (add your frontend URLs)
CORS_ORIGINS=["http://localhost:5173", "http://localhost:80"]
```

---

## 📚 Documentation

### API Endpoints

Once running, visit http://localhost:8000/docs for full API documentation.

**Key endpoints:**
- `POST /api/v1/chat` - Send a chat message
- `GET /api/v1/sessions` - List chat sessions
- `GET /api/v1/artifacts` - List generated artifacts
- `POST /api/v1/knowledge/upload` - Upload documents
- `GET /api/v1/models` - Get available AI models

### Project Structure

```
lenny-growth-assistant/
├── frontend/                 # React frontend
│   ├── src/
│   │   ├── components/      # UI components
│   │   ├── hooks/          # Custom React hooks
│   │   └── main.tsx        # Entry point
│   ├── Dockerfile          # Frontend container
│   └── nginx.conf          # Production web server config
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── main.py         # FastAPI app entry
│   │   ├── routers/        # API routes
│   │   ├── models/         # Database models
│   │   ├── rag/            # RAG implementation
│   │   └── ai_providers/   # AI integrations
│   ├── Dockerfile          # Backend container
│   └── requirements.txt    # Python dependencies
├── docker-compose.yml      # Full stack with Ollama
├── docker-compose.simple.yml # Cloud AI only
└── README.md              # This file
```

---




---

<div align="center">

**Built with ❤️ for product builders and growth enthusiasts**

⭐ Star this repo if you find it helpful!

</div>
