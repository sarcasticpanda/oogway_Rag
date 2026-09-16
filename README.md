# Lenny Growth Assistant

AI-powered Product & Growth Assistant based on Lenny's Podcast transcripts.

## Quick Start

### Option 1: Cloud AI (Recommended - Fast & Easy)

1. **Setup environment**:
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

2. **Start the application**:
   ```bash
   docker-compose -f docker-compose.simple.yml up -d
   ```

3. **Access the app**:
   - Frontend: http://localhost
   - API docs: http://localhost:8000/docs

### Option 2: Local AI with Ollama (Offline, but slower first start)

1. **Start with Ollama**:
   ```bash
   docker-compose up -d
   ```
   
   Note: First start will download ~3.7GB Ollama model. This takes 5-10 minutes.

2. **Access the app**:
   - Frontend: http://localhost
   - API docs: http://localhost:8000/docs

## Architecture

- **Frontend**: React + TypeScript + Vite + Tailwind CSS
- **Backend**: FastAPI + PostgreSQL + pgvector
- **AI**: Multi-model support (OpenAI, Anthropic, Groq, Ollama)

## Available Commands

```bash
# Start services
docker-compose -f docker-compose.simple.yml up -d

# View logs
docker-compose -f docker-compose.simple.yml logs -f

# Stop services
docker-compose -f docker-compose.simple.yml down

# Stop and remove volumes
docker-compose -f docker-compose.simple.yml down -v
```

## Features

- 💬 Chat with AI about product & growth topics
- 📚 Grounded in Lenny's Podcast knowledge base
- 🎨 Generate artifacts (code, diagrams, documents)
- 🔄 Multi-model AI provider switching
- 📊 Session management and history

## Development

See individual README files in `frontend/` and `backend/` for local development setup.
