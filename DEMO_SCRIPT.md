# 🎥 Demo Video Script (2-3 minutes)

## Video Requirements
- **Length**: 2-3 minutes
- **Camera**: Enabled (show your face)
- **Content**: Problem → Product → Demo → Technical Trade-off
- **Platform**: Upload to YouTube (unlisted is fine)

---

## 📝 Script Template

### Opening (15 seconds)
**[Camera on, smile, confident tone]**

"Hi! I'm [Your Name], and I built Lenny Growth Assistant—an AI-powered product and growth assistant that helps teams learn from Lenny Rachitsky's extensive podcast library using RAG and multi-model AI support."

---

### Problem Statement (30 seconds)
**[Screen: Show blank browser or problem slide]**

"Product managers and growth teams face a challenge: Lenny's Podcast has hundreds of hours of valuable insights from top experts, but finding specific advice is time-consuming. You need to remember which episode covered what topic, search through transcripts manually, or rely on scattered notes.

**The core problem**: Knowledge is siloed and hard to access when you need it most—during product decisions, growth strategy discussions, or team meetings."

---

### Solution Overview (20 seconds)
**[Screen: Navigate to http://localhost - show main interface]**

"Lenny Growth Assistant solves this with a conversational AI interface that's grounded in real podcast transcripts. Instead of searching, you just ask questions in natural language, and the system retrieves relevant context using vector search and generates accurate, source-grounded answers."

---

### Tech Stack Quick Overview (25 seconds)
**[Screen: Stay on main interface, gesture to different parts]**

"Let me quickly cover the tech stack:
- **Frontend**: React with TypeScript and Tailwind CSS for a modern, responsive UI
- **Backend**: FastAPI with Python, handling all the AI orchestration
- **Database**: PostgreSQL with pgvector extension for semantic search
- **AI Layer**: Multi-model support—OpenAI, Anthropic Claude, Groq, or local Ollama
- **Infrastructure**: Fully containerized with Docker Compose for one-command deployment"

---

### Feature Demo 1: RAG-Powered Chat (30 seconds)
**[Screen: Type a question in the chat]**

"Let me show you the core RAG pipeline in action. I'll ask: 'What did Lenny's guests say about product-led growth?'"

**[Type the question, press Enter]**

"Notice how the system:
1. Takes my query and converts it to an embedding
2. Searches the vector database for relevant podcast chunks
3. Retrieves the top context from actual transcripts
4. Sends that context plus my question to the AI model
5. Generates a grounded response with specific examples"

**[Show the response appearing]**

"See how it's citing specific insights? That's the RAG pipeline ensuring accuracy."

---

### Feature Demo 2: Multi-Model Support (15 seconds)
**[Screen: Click on model selector dropdown]**

"A key feature is multi-model flexibility. You can switch between OpenAI's GPT-4, Claude, Groq for speed, or run everything locally with Ollama—all without changing your workflow."

**[Show dropdown options]**

---

### Feature Demo 3: Artifact Generation (20 seconds)
**[Screen: Navigate to Artifacts section]**

"Beyond chat, the system generates artifacts. Type '@artifact' to create:
- Product strategy documents
- Ship 30 essays for Twitter
- Code examples
- Diagrams and flowcharts"

**[Click on Artifacts tab, show existing artifacts]**

"These are versioned, exportable, and tied to your conversation context."

---

### Feature Demo 4: Knowledge Base (15 seconds)
**[Screen: Navigate to Knowledge Base]**

"The knowledge base shows all ingested content. You can upload your own PDFs and documents, and they're automatically chunked, embedded, and added to the searchable corpus."

**[Show the episodes list or upload interface]**

---

### Technical Trade-off Discussion (25 seconds)
**[Screen: Can stay on interface or show architecture diagram]**

"One important technical trade-off I made: **Embedding Strategy**.

I chose to use **smaller, focused chunks** (500 tokens with 100-token overlap) rather than whole-document embeddings. 

**Trade-off**:
- ✅ **Pro**: More precise retrieval, better context relevance, handles long transcripts
- ❌ **Con**: Higher storage costs, more embeddings to generate initially, slightly slower ingestion

I prioritized **retrieval accuracy over ingestion speed** because the assistant needs to give precise answers, even if initial setup takes longer. For a production deployment with thousands of documents, we'd batch process and cache embeddings."

---

### Session Management & History (10 seconds)
**[Screen: Show sidebar with session history]**

"All conversations are saved with session management, so you can resume previous discussions and maintain context across multiple chats."

---

### Closing & Deployment (15 seconds)
**[Screen: Optional - show terminal with docker-compose command]**

"Everything runs with one command: `docker-compose up`. It's production-ready with:
- Structured logging for observability
- Health checks on all services
- Graceful error handling
- Environment-based configuration

The entire system is documented, tested, and ready for another team to operate."

**[Camera: Face]**

"Thanks for watching! Check out the GitHub repo for the full code, architecture docs, and deployment guide."

---

## 🎬 Recording Tips

### Before Recording:
1. ✅ Clear browser cache
2. ✅ Close unnecessary tabs
3. ✅ Set browser to 100% zoom
4. ✅ Test your microphone
5. ✅ Have the application running on http://localhost
6. ✅ Prepare 1-2 demo questions
7. ✅ Clear your session history OR use it to show multiple conversations

### During Recording:
- **Speak clearly and confidently**
- **Move your cursor deliberately** (not too fast)
- **Pause briefly** between sections
- **Don't worry about perfection**—authenticity matters more
- **Show enthusiasm** for the technical solution

### Screen Recording Setup:
- Use OBS Studio, Loom, or native screen recorder
- **Resolution**: 1920x1080 (1080p)
- **Frame rate**: 30 fps minimum
- **Include**: Both your camera feed (corner) and screen
- **Audio**: Clear, no background noise

---

## 🎯 Key Points to Emphasize

### Customer Value:
✅ Saves time searching through hours of content  
✅ Get expert insights when you need them  
✅ Grounded answers prevent hallucinations  

### Technical Excellence:
✅ RAG pipeline with vector search  
✅ Multi-model AI flexibility  
✅ Production-ready deployment  
✅ Comprehensive error handling  

### Forward Deployed Engineer Skills:
✅ One-command deployment  
✅ Observable and maintainable  
✅ Well-documented for handoff  
✅ Security-conscious (no secrets committed)  

---

## 📊 Timing Breakdown

| Section | Time | Running Total |
|---------|------|---------------|
| Opening | 15s | 0:15 |
| Problem | 30s | 0:45 |
| Solution | 20s | 1:05 |
| Tech Stack | 25s | 1:30 |
| Demo: RAG Chat | 30s | 2:00 |
| Demo: Multi-Model | 15s | 2:15 |
| Demo: Artifacts | 20s | 2:35 |
| Demo: Knowledge Base | 15s | 2:50 |
| Technical Trade-off | 25s | 3:15 |
| Session Mgmt | 10s | 3:25 |
| Closing | 15s | 3:40 |

**Total**: ~3:40 (can be trimmed to 3:00 by speaking faster or cutting sections)

---

## 🎥 Alternative: Shorter 2-Minute Version

If you need exactly 2 minutes:

1. **Opening**: 10s
2. **Problem**: 20s
3. **Solution + Tech Stack**: 20s
4. **Demo: RAG Pipeline**: 40s
5. **Demo: Multi-Model**: 10s
6. **Technical Trade-off**: 20s
7. **Closing**: 10s

**Total**: 2:10

---

## 📝 Demo Questions to Use

### Good Demo Questions:
1. "What did Lenny's guests say about product-led growth?"
2. "How do successful companies approach user onboarding?"
3. "What metrics should I track for a SaaS product?"
4. "@artifact report: Summarize key growth strategies from the last 5 episodes"
5. "@artifact ship30: Write about building a product culture"

### Why These Work:
- Demonstrate RAG retrieval
- Show real podcast knowledge
- Highlight artifact generation
- Prove multi-turn conversation ability

---

## 🚀 Final Checklist Before Recording

- [ ] Docker containers running
- [ ] Browser on http://localhost
- [ ] Camera and mic tested
- [ ] Lighting is good
- [ ] Background is clean/professional
- [ ] Script reviewed (not memorized—be natural!)
- [ ] Demo questions ready
- [ ] Timer/stopwatch ready
- [ ] Recording software configured

---

## 📤 After Recording

1. **Edit** (optional): Trim pauses, add subtle transitions
2. **Upload** to YouTube (can be unlisted)
3. **Get the link**: Copy YouTube URL
4. **Add to README**: Include video link in your README
5. **Submit**: Add to submission form

---

Good luck! You've got this! 🎉
