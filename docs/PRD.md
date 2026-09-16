# Product Requirements Document (PRD)
## Lenny Growth Assistant

**Version**: 1.0  
**Date**: September 16, 2026  
**Author**: Forward Deployed Engineer  
**Status**: Initial Release

---

## Executive Summary

Lenny Growth Assistant is an AI-powered conversational interface that enables product managers, growth practitioners, and startup founders to access insights from Lenny Rachitsky's extensive podcast library through natural language queries. The system uses Retrieval-Augmented Generation (RAG) to provide accurate, source-grounded answers and generate actionable artifacts.

---

## 1. User & Audience

### Primary Users
1. **Product Managers** (Junior to Senior)
   - Need quick access to product strategy insights
   - Want to validate decisions with expert knowledge
   - Looking for frameworks and mental models

2. **Growth Practitioners**
   - Seeking growth tactics and strategies
   - Need case studies and real-world examples
   - Want to learn from successful companies

3. **Startup Founders**
   - Building products with limited resources
   - Need guidance on product-led growth
   - Looking for hiring and team-building advice

### Secondary Users
4. **Engineering Leaders**
   - Understanding product-engineering collaboration
   - Learning about technical product decisions

5. **Design Leaders**
   - Product design best practices
   - User research methodologies

---

## 2. Problem Statement

### The Problem
**Current State**: Lenny's Podcast contains 300+ hours of valuable insights from top product and growth experts, but this knowledge is:
- **Scattered** across hundreds of episodes
- **Time-consuming** to search through manually
- **Difficult to reference** during real-time decisions
- **Hard to synthesize** across multiple episodes

**User Pain Points**:
1. "I remember Lenny interviewed someone about this, but which episode?"
2. "I need advice on PLG right now, but don't have time to watch 3 hours of content"
3. "How do multiple guests' perspectives on this topic compare?"
4. "I want to reference specific advice in my planning doc"

### Why This Matters
- **Time Cost**: Searching through transcripts manually takes 20-30 minutes per query
- **Decision Quality**: Missing relevant insights leads to suboptimal product decisions
- **Learning Efficiency**: Passive listening doesn't enable active knowledge retrieval
- **Team Alignment**: Hard to share specific insights with teammates

---

## 3. Success Metrics

### North Star Metric
**Time-to-Insight**: Average time from question to actionable answer < 30 seconds

### Primary Metrics
1. **Engagement**
   - Daily Active Users (DAU)
   - Questions asked per session (target: 5+)
   - Session duration (target: 10-15 minutes)
   - Return user rate (target: 40% weekly)

2. **Quality**
   - Answer relevance score (user feedback: target 4.5/5)
   - Source accuracy (answers cite correct episodes: target 95%+)
   - Hallucination rate (target: <5% of responses)

3. **Utility**
   - Artifacts generated per session (target: 1-2)
   - Document uploads per user (target: 0.5+)
   - Knowledge base queries per day (target: 100+)

### Secondary Metrics
- API response time (target: <2s for chat, <5s for artifact generation)
- System uptime (target: 99.5%)
- Error rate (target: <1%)
- Model switching frequency (indicates flexibility value)

---

## 4. Assumptions

### User Behavior
1. Users are familiar with Lenny's Podcast and trust the content
2. Users prefer conversational interfaces over traditional search
3. Users will provide feedback on answer quality
4. Users need both quick answers AND deep dives

### Technical
1. RAG provides better accuracy than pure LLM responses
2. Vector search with pgvector is sufficient for 1000+ documents
3. Multi-model support provides meaningful value vs. single provider
4. Local Ollama is viable for privacy-conscious deployments

### Business
1. OpenAI/Anthropic API costs are acceptable for prototype
2. Users will self-host or use provided cloud instance
3. No monetization required for initial release
4. Community will contribute additional content over time

---

## 5. Scope

### In Scope (v1.0)

#### Core Features
✅ **Chat Interface**
- Natural language questions
- Streaming responses
- Multi-turn conversations
- Context retention across messages
- Source citations

✅ **RAG Pipeline**
- Document ingestion (transcripts, PDFs, DOCX)
- Chunking with overlap
- Vector embeddings storage
- Semantic search retrieval
- Context-grounded generation

✅ **Multi-Model AI**
- OpenAI (GPT-4o, GPT-4o-mini, GPT-3.5-turbo)
- Anthropic (Claude 3.5 Sonnet, Claude 3 Opus/Haiku)
- Groq (Llama 3, Mixtral)
- Local Ollama (qwen2.5-coder, llama3, etc.)

✅ **Artifact Generation**
- Reports and summaries
- Code examples
- Ship 30 essays
- Strategy documents
- Diagrams (text-based)

✅ **Knowledge Management**
- View ingested episodes
- Upload custom documents
- Browse document library
- Delete documents

✅ **Session Management**
- Save conversations
- Resume previous chats
- Browse history by date
- Delete sessions

#### Infrastructure
✅ Docker Compose deployment
✅ PostgreSQL + pgvector
✅ FastAPI backend
✅ React + TypeScript frontend
✅ Environment-based configuration
✅ Structured logging
✅ Health checks

### Out of Scope (Future Versions)

❌ **v1.0 Exclusions**:
- User authentication and multi-tenancy
- Payment/subscription system
- Mobile apps (iOS/Android)
- Real-time collaboration
- Video generation or editing
- Audio playback of episodes
- Automatic episode ingestion pipeline
- Advanced analytics dashboard
- A/B testing framework
- Integration with Slack/Discord/Teams
- Browser extension
- Public API for third parties
- Fine-tuning custom models

### Future Roadmap Ideas
- **v1.1**: User accounts, saved preferences, sharing
- **v1.2**: Mobile-responsive PWA
- **v1.3**: Team workspaces and collaboration
- **v2.0**: Public API, integrations, webhooks

---

## 6. User Flows

### Flow 1: First-Time User Setup
1. Clone repository from GitHub
2. Copy `.env.example` to `.env`
3. Add API key (OpenAI/Anthropic) OR use local Ollama
4. Run `docker-compose up -d`
5. Navigate to `http://localhost`
6. See welcome screen with example questions
7. **Success**: User asks first question, receives grounded answer

**Acceptance Criteria**:
- [ ] Setup takes <5 minutes for technical users
- [ ] Clear error messages if API key missing
- [ ] Example questions spark curiosity
- [ ] First response cites actual podcast content

---

### Flow 2: Ask a Question (Core RAG Flow)
1. User types question: "What is product-led growth?"
2. System shows loading indicator
3. Backend:
   - Converts question to embedding
   - Searches vector DB for top-k relevant chunks
   - Retrieves episode context
   - Sends question + context to LLM
   - Streams response back
4. Frontend displays answer with:
   - Episode citations
   - Relevant timestamps
   - Follow-up suggestions
5. User can ask follow-up in same context

**Acceptance Criteria**:
- [ ] Response appears within 3 seconds
- [ ] Answer cites 2-3 relevant episodes
- [ ] No hallucinated information
- [ ] Follow-ups maintain context
- [ ] User can copy/share response

---

### Flow 3: Generate an Artifact
1. User types: "@artifact report: Summarize PLG strategies"
2. System detects `@artifact` command
3. Backend:
   - Parses artifact type and prompt
   - Retrieves relevant context
   - Generates structured content
   - Saves to artifacts table
4. Frontend:
   - Shows artifact in side panel
   - Allows export (Markdown, PDF)
   - Links artifact to session
5. User can view in Artifacts tab later

**Acceptance Criteria**:
- [ ] Artifact types: report, code, ship30, diagram, checklist
- [ ] Content is well-formatted Markdown
- [ ] Exportable and shareable
- [ ] Tied to source conversation
- [ ] Versioned (can regenerate)

---

### Flow 4: Upload Custom Document
1. User navigates to Knowledge Base
2. Clicks "Upload Document"
3. Selects PDF or DOCX file (<10MB)
4. System:
   - Extracts text
   - Chunks into segments
   - Generates embeddings
   - Stores in vector DB
   - Shows success notification
5. Document appears in knowledge base list
6. User can now query this content in chat

**Acceptance Criteria**:
- [ ] Supports PDF and DOCX formats
- [ ] Files up to 10MB
- [ ] Clear progress indicator
- [ ] Error handling for corrupted files
- [ ] Uploaded content searchable immediately

---

### Flow 5: Switch AI Models
1. User clicks model selector dropdown
2. Sees available providers:
   - OpenAI (if API key present)
   - Anthropic (if API key present)
   - Groq (if API key present)
   - Ollama (if running locally)
3. Selects new model
4. System validates availability
5. Next query uses new model
6. Response quality/speed may differ

**Acceptance Criteria**:
- [ ] Switch happens instantly
- [ ] No data loss during switch
- [ ] Clear indication which model is active
- [ ] Fallback to default if model unavailable
- [ ] Model preference persists in session

---

### Flow 6: Browse Session History
1. User clicks on sidebar
2. Sees conversations grouped by date:
   - Today
   - Yesterday
   - Last 7 days
   - Older
3. Clicks on a past conversation
4. Chat loads with full history
5. User can continue conversation OR start new one

**Acceptance Criteria**:
- [ ] Fast loading of session list
- [ ] Search/filter sessions (future)
- [ ] Delete individual sessions
- [ ] Clear all history option
- [ ] Session metadata (date, message count, topic)

---

## 7. Acceptance Criteria

### Functional Requirements

#### Chat System
- [ ] Users can send text messages up to 4000 characters
- [ ] Responses stream in real-time (no buffering delay)
- [ ] System cites source episodes with titles
- [ ] Multi-turn conversations maintain context
- [ ] Copy message button works
- [ ] Markdown rendering (bold, lists, code blocks)

#### RAG Pipeline
- [ ] Vector search returns top-5 relevant chunks
- [ ] Embedding generation completes <1s per chunk
- [ ] Retrieved context includes episode metadata
- [ ] Answers avoid hallucination (cite sources)
- [ ] Empty results return "no relevant content found"

#### Artifacts
- [ ] @artifact command triggers generation
- [ ] Supports: report, code, ship30, diagram, checklist
- [ ] Markdown formatting is correct
- [ ] Artifacts saved to database
- [ ] Export to .md file works
- [ ] Artifacts display in dedicated tab

#### Knowledge Base
- [ ] Upload accepts PDF and DOCX <10MB
- [ ] Extraction handles multi-page documents
- [ ] Chunking maintains context (overlap strategy)
- [ ] Delete removes document and embeddings
- [ ] List shows all ingested content

#### Multi-Model
- [ ] OpenAI, Anthropic, Groq, Ollama all work
- [ ] Model switching doesn't break session
- [ ] API errors handled gracefully
- [ ] Timeout after 30 seconds
- [ ] Clear error messages for missing keys

#### Sessions
- [ ] New session creates fresh context
- [ ] Resume session loads all messages
- [ ] Delete session removes from DB
- [ ] Session limit: 100 messages max
- [ ] Auto-save every message

### Non-Functional Requirements

#### Performance
- [ ] Chat response: <3s (P95)
- [ ] Artifact generation: <10s (P95)
- [ ] Page load: <2s
- [ ] Vector search: <500ms
- [ ] Handle 10 concurrent users

#### Reliability
- [ ] 99% uptime for core features
- [ ] Graceful degradation if DB unavailable
- [ ] Retry logic for API calls (3 attempts)
- [ ] No data loss on container restart
- [ ] Health checks on all services

#### Security
- [ ] No API keys in git history
- [ ] Environment variables for secrets
- [ ] Input sanitization (prevent injection)
- [ ] CORS configured correctly
- [ ] No sensitive data in logs

#### Usability
- [ ] Mobile-responsive (≥768px)
- [ ] Keyboard shortcuts (Enter to send, Esc to cancel)
- [ ] Loading states for all async actions
- [ ] Error messages are actionable
- [ ] Tooltips explain complex features

#### Accessibility
- [ ] Semantic HTML structure
- [ ] Keyboard navigation works
- [ ] ARIA labels on interactive elements
- [ ] Focus indicators visible
- [ ] Color contrast meets WCAG AA

---

## 8. Risks & Mitigation

### Technical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| API rate limits hit | High | Medium | Implement request throttling, caching, fallback to local Ollama |
| Vector DB performance degrades at scale | Medium | Low | Index optimization, consider Pinecone/Weaviate for >10k docs |
| Model hallucinations | High | Medium | RAG pipeline, source citations, user feedback loop |
| Ollama too slow on low-end machines | Medium | High | Document minimum requirements, recommend cloud models |
| Embedding costs grow unexpectedly | Medium | Low | Batch processing, cache embeddings, use smaller models |

### Product Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Users don't trust AI answers | High | Medium | Always show sources, allow feedback, highlight RAG vs. pure LLM |
| Setup too complex for non-technical users | Medium | High | One-command Docker setup, clear docs, video tutorial |
| Content licensing concerns | High | Low | Educational/research use, link to original episodes |
| Low answer quality vs. manual search | High | Low | Iterate on retrieval, validate with test questions |

### Operational Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| No monitoring/observability | Medium | High | Structured logs, health endpoints, error tracking |
| Docker Compose not production-ready | Low | High | Document as prototype, suggest k8s/ECS for production |
| No user support channel | Low | Medium | GitHub Issues, README troubleshooting section |

---

## 9. Implementation Plan

### Phase 1: Foundation (Week 1) ✅ COMPLETE
- [x] Project setup (FastAPI + React)
- [x] PostgreSQL + pgvector
- [x] Basic chat UI
- [x] Simple RAG pipeline
- [x] Docker Compose

### Phase 2: Core Features (Week 2) ✅ COMPLETE
- [x] Multi-model support
- [x] Artifact generation
- [x] Document upload
- [x] Session management
- [x] Knowledge base UI

### Phase 3: Polish & Deploy (Week 3) ✅ CURRENT
- [x] Comprehensive README
- [x] Screenshots and demos
- [x] Error handling
- [x] Logging and observability
- [ ] Automated tests
- [ ] Documentation (PRD, architecture, design)
- [ ] Demo video

### Phase 4: Future (Post-Launch)
- [ ] User accounts
- [ ] Analytics dashboard
- [ ] Mobile PWA
- [ ] API endpoints
- [ ] Slack integration

---

## 10. Open Questions

1. **Content Licensing**: Do we need explicit permission to use podcast transcripts for RAG?
   - **Answer**: Educational/fair use, always link back to original source

2. **Scalability**: At what point do we need to migrate from pgvector to dedicated vector DB?
   - **Answer**: Test with 10k+ documents, evaluate latency

3. **Monetization**: Should v1 include any payment/auth infrastructure?
   - **Answer**: No, focus on core value first

4. **Model Costs**: What's acceptable monthly API spend for prototype?
   - **Answer**: <$100/month for initial users

5. **Community**: Open source immediately or start closed?
   - **Answer**: Open source from day 1, encourage contributions

---

## 11. Dependencies

### External
- OpenAI API (optional, for GPT models)
- Anthropic API (optional, for Claude models)
- Groq API (optional, for fast inference)
- Ollama (optional, for local models)

### Internal
- Docker & Docker Compose
- PostgreSQL 16 with pgvector extension
- Node.js 20+ for frontend build
- Python 3.11+ for backend

---

## 12. Success Criteria for Launch

### Must Have (P0)
- [ ] All core flows work end-to-end
- [ ] No critical bugs
- [ ] Documentation complete
- [ ] Demo video recorded
- [ ] Tests pass

### Should Have (P1)
- [ ] Error handling comprehensive
- [ ] Performance targets met
- [ ] Accessibility basics covered
- [ ] Code quality high

### Nice to Have (P2)
- [ ] Advanced features (exports, sharing)
- [ ] Analytics and tracking
- [ ] Multiple themes

---

## Appendix

### A. Competitive Analysis
- **ChatGPT**: General knowledge, but no Lenny-specific grounding
- **Perplexity**: Good at search, but doesn't specialize in product/growth
- **Manual Search**: Accurate but time-consuming
- **Lenny's Website Search**: Limited to keyword matching

**Our Differentiation**: Specialized, RAG-grounded, multi-model, artifact generation

### B. User Research Findings
- Product managers spend 2-3 hours/week searching for resources
- Podcast listeners want to reference specific advice but struggle with recall
- Teams need shareable artifacts, not just chat logs
- Privacy concerns drive interest in local/self-hosted solutions

### C. Glossary
- **RAG**: Retrieval-Augmented Generation
- **Vector DB**: Database optimized for similarity search
- **Embedding**: Numerical representation of text
- **Chunk**: Segment of document used for retrieval
- **Artifact**: Generated content output (report, code, etc.)

---

**Document Status**: Complete for v1.0  
**Next Review**: After launch feedback collection
