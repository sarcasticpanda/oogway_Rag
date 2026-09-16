# Manual Test Plan
## Lenny Growth Assistant

**Version**: 1.0  
**Last Updated**: September 16, 2026  
**Tester**: Forward Deployed Engineer  
**Environment**: Local Docker Compose

---

## 1. Pre-Test Setup

### 1.1 Environment Prerequisites
- [ ] Docker Desktop installed and running
- [ ] `.env` file configured with API keys:
  - `OPENAI_API_KEY` (required)
  - `ANTHROPIC_API_KEY` (optional)
  - `GROQ_API_KEY` (optional)
- [ ] Port 80 (frontend) and 8000 (backend) are available

### 1.2 Start Application
```bash
cd lenny-growth-assistant
docker-compose -f docker-compose.simple.yml up -d
```

### 1.3 Verify Services
```bash
docker-compose ps
```
Expected: All services show "Up" status (postgres, api, frontend)

### 1.4 Access Points
- Frontend: http://localhost
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 2. Functional Tests

### 2.1 Chat Interface - Basic Flow

#### Test Case 2.1.1: First Message
**Steps**:
1. Open http://localhost in browser
2. Observe empty state with welcome message
3. Type "What is product-led growth?" in input box
4. Click Send button or press Enter

**Expected Results**:
- [ ] Message appears immediately in chat (optimistic UI)
- [ ] Loading dots appear below user message
- [ ] AI response streams word-by-word (not all at once)
- [ ] Response completes within 5-10 seconds
- [ ] Response includes markdown formatting (bold, lists, etc.)
- [ ] Sources section appears at bottom with episode citations
- [ ] No error messages in console

**Pass/Fail**: ___________

---

#### Test Case 2.1.2: Follow-up Question
**Steps**:
1. After receiving first response, type "Tell me more"
2. Send message

**Expected Results**:
- [ ] Follow-up maintains conversation context
- [ ] Response references previous discussion
- [ ] Session ID remains the same (check network tab)

**Pass/Fail**: ___________

---

#### Test Case 2.1.3: Empty Message Handling
**Steps**:
1. Click Send with empty input box
2. Try sending whitespace-only message

**Expected Results**:
- [ ] Send button disabled when input is empty
- [ ] No API call made
- [ ] No error thrown

**Pass/Fail**: ___________

---

### 2.2 Model Selection

#### Test Case 2.2.1: Switch Models
**Steps**:
1. Click model selector in header (shows current model)
2. Select different model (e.g., gpt-4o → gpt-4o-mini)
3. Send a test message

**Expected Results**:
- [ ] Dropdown shows all available providers
- [ ] Selected model is highlighted
- [ ] Response comes from newly selected model
- [ ] Model selection persists across page refresh

**Pass/Fail**: ___________

---

#### Test Case 2.2.2: Fallback Behavior
**Steps**:
1. If Ollama is not running, select an Ollama model
2. Send a message

**Expected Results**:
- [ ] Error message shown to user
- [ ] Suggestion to check if Ollama is running
- [ ] App does not crash

**Pass/Fail**: ___________

---

### 2.3 Session Management

#### Test Case 2.3.1: New Chat Creation
**Steps**:
1. Have an active conversation
2. Click "New Chat" button in sidebar
3. Verify new session started

**Expected Results**:
- [ ] Chat area clears
- [ ] New session ID generated (check network requests)
- [ ] Previous session appears in sidebar history
- [ ] Input box remains focused

**Pass/Fail**: ___________

---

#### Test Case 2.3.2: Session History
**Steps**:
1. Create 3-4 different conversations
2. Check sidebar for session list
3. Click on a previous session

**Expected Results**:
- [ ] Sessions grouped by date (Today, Yesterday, Older)
- [ ] Each session shows preview/title
- [ ] Clicking session loads full conversation history
- [ ] Current session is highlighted

**Pass/Fail**: ___________

---

#### Test Case 2.3.3: Delete Session
**Steps**:
1. Hover over a session in sidebar
2. Click delete icon
3. Confirm deletion

**Expected Results**:
- [ ] Confirmation dialog appears
- [ ] After confirm, session removed from list
- [ ] If deleting active session, redirects to new chat
- [ ] Deletion persists after page refresh

**Pass/Fail**: ___________

---

### 2.4 Knowledge Base

#### Test Case 2.4.1: View Episodes
**Steps**:
1. Click "Knowledge Base" tab in sidebar
2. Scroll through episode list

**Expected Results**:
- [ ] Episodes listed with guest names
- [ ] Episode titles visible
- [ ] List is scrollable
- [ ] Loading state shown while fetching

**Pass/Fail**: ___________

---

#### Test Case 2.4.2: Search Episodes
**Steps**:
1. In Knowledge Base tab, use search box
2. Type "retention"
3. View filtered results

**Expected Results**:
- [ ] Results update as you type (debounced)
- [ ] Matching episodes highlighted
- [ ] No results message if query has zero matches
- [ ] Clear search button appears

**Pass/Fail**: ___________

---

#### Test Case 2.4.3: Upload Document
**Steps**:
1. Click "Upload Document" button
2. Select a PDF file (< 10MB)
3. Wait for upload to complete

**Expected Results**:
- [ ] File picker opens
- [ ] Progress bar shown during upload
- [ ] Success message after completion
- [ ] Document appears in knowledge base list
- [ ] Can now query about document content

**Pass/Fail**: ___________

---

#### Test Case 2.4.4: Upload Validation
**Steps**:
1. Try uploading invalid file types (.txt, .exe, etc.)
2. Try uploading file > 10MB

**Expected Results**:
- [ ] Error message for invalid file type
- [ ] Error message for oversized file
- [ ] No partial upload occurs

**Pass/Fail**: ___________

---

### 2.5 Artifacts

#### Test Case 2.5.1: Generate Artifact
**Steps**:
1. In chat, type: `@artifact report: Summarize key growth strategies`
2. Send message

**Expected Results**:
- [ ] AI recognizes artifact command
- [ ] Structured artifact generated (not just plain text)
- [ ] Artifact appears in "Artifacts" tab
- [ ] Artifact has title, timestamp, type

**Pass/Fail**: ___________

---

#### Test Case 2.5.2: View Artifacts
**Steps**:
1. Click "Artifacts" tab in sidebar
2. Click on a generated artifact

**Expected Results**:
- [ ] List shows all previously generated artifacts
- [ ] Clicking artifact opens in detail view
- [ ] Artifact content is formatted (markdown/HTML)
- [ ] Can copy artifact content

**Pass/Fail**: ___________

---

#### Test Case 2.5.3: Export Artifact
**Steps**:
1. Open an artifact
2. Click export button
3. Choose format (PDF, Markdown, etc.)

**Expected Results**:
- [ ] Export options displayed
- [ ] File downloads successfully
- [ ] Exported file is readable
- [ ] Formatting preserved

**Pass/Fail**: ___________

---

### 2.6 RAG Quality

#### Test Case 2.6.1: Grounded Response
**Steps**:
1. Ask: "What does Lenny say about retention curves?"
2. Verify response quality

**Expected Results**:
- [ ] Response cites specific episodes
- [ ] Episode titles and timestamps shown
- [ ] Content is accurate to podcast knowledge
- [ ] No hallucinated information

**Pass/Fail**: ___________

---

#### Test Case 2.6.2: Ungrounded Query
**Steps**:
1. Ask: "What is the capital of France?"
2. Check how system handles off-topic query

**Expected Results**:
- [ ] System acknowledges query is outside knowledge base
- [ ] Response explicitly states low confidence
- [ ] No fake podcast citations generated
- [ ] Suggests rephrasing or checking scope

**Pass/Fail**: ___________

---

#### Test Case 2.6.3: Multi-hop Reasoning
**Steps**:
1. Ask: "Compare what Brian Balfour and Casey Winters say about growth loops"

**Expected Results**:
- [ ] Response synthesizes information from multiple episodes
- [ ] Both guests cited separately
- [ ] Clear attribution for each perspective
- [ ] Comparison is coherent

**Pass/Fail**: ___________

---

### 2.7 Error Handling

#### Test Case 2.7.1: API Key Missing
**Steps**:
1. Stop containers
2. Remove `OPENAI_API_KEY` from `.env`
3. Restart containers
4. Try sending message

**Expected Results**:
- [ ] Friendly error message to user
- [ ] Logs show configuration error
- [ ] App suggests checking API key
- [ ] App does not crash

**Pass/Fail**: ___________

---

#### Test Case 2.7.2: Network Timeout
**Steps**:
1. Simulate slow network (browser dev tools)
2. Send message

**Expected Results**:
- [ ] Loading state persists
- [ ] Timeout error after 30-60 seconds
- [ ] User can retry
- [ ] No duplicate messages

**Pass/Fail**: ___________

---

#### Test Case 2.7.3: Database Connection Failure
**Steps**:
1. Stop postgres container
2. Try querying knowledge base

**Expected Results**:
- [ ] Error message shown
- [ ] Logs indicate database issue
- [ ] App remains functional for non-DB features
- [ ] Suggests checking deployment

**Pass/Fail**: ___________

---

## 3. UI/UX Tests

### 3.1 Responsive Design

#### Test Case 3.1.1: Desktop (1920x1080)
**Steps**:
1. Open browser at full desktop resolution
2. Navigate all features

**Expected Results**:
- [ ] Sidebar visible and fixed
- [ ] Chat area centered, max-width ~900px
- [ ] All buttons and text readable
- [ ] No horizontal scroll

**Pass/Fail**: ___________

---

#### Test Case 3.1.2: Tablet (768x1024)
**Steps**:
1. Resize browser to tablet dimensions
2. Test chat and sidebar

**Expected Results**:
- [ ] Sidebar collapses to hamburger menu
- [ ] Chat uses full width
- [ ] Touch targets are 44px minimum
- [ ] No layout breakage

**Pass/Fail**: ___________

---

#### Test Case 3.1.3: Mobile (375x667)
**Steps**:
1. Test on mobile device or resize to mobile viewport
2. Navigate all features

**Expected Results**:
- [ ] Single column layout
- [ ] Input sticky at bottom
- [ ] Sidebar as full-screen overlay
- [ ] Font size readable (min 14px)
- [ ] No pinch-zoom required

**Pass/Fail**: ___________

---

### 3.2 Accessibility

#### Test Case 3.2.1: Keyboard Navigation
**Steps**:
1. Navigate app using only Tab, Enter, Escape keys
2. Test all interactive elements

**Expected Results**:
- [ ] All buttons reachable via Tab
- [ ] Focus indicators visible (2px outline)
- [ ] Enter activates buttons
- [ ] Escape closes modals
- [ ] No keyboard traps

**Pass/Fail**: ___________

---

#### Test Case 3.2.2: Screen Reader
**Steps**:
1. Enable screen reader (NVDA, VoiceOver, etc.)
2. Navigate chat interface

**Expected Results**:
- [ ] All text announced correctly
- [ ] Buttons have descriptive labels
- [ ] Loading states announced
- [ ] Error messages read aloud
- [ ] Landmarks identified (header, main, nav)

**Pass/Fail**: ___________

---

#### Test Case 3.2.3: Color Contrast
**Steps**:
1. Use browser accessibility inspector
2. Check all text/background combinations

**Expected Results**:
- [ ] All text meets WCAG AA (4.5:1 ratio)
- [ ] Interactive elements distinguishable
- [ ] Focus states have sufficient contrast

**Pass/Fail**: ___________

---

### 3.3 Performance

#### Test Case 3.3.1: Initial Load Time
**Steps**:
1. Clear browser cache
2. Navigate to http://localhost
3. Measure time to interactive

**Expected Results**:
- [ ] First paint < 1 second
- [ ] Time to interactive < 3 seconds
- [ ] No render-blocking resources
- [ ] Progressive enhancement (works before JS loads)

**Pass/Fail**: ___________

---

#### Test Case 3.3.2: Chat Streaming Latency
**Steps**:
1. Send message
2. Measure time to first token

**Expected Results**:
- [ ] First token appears < 1 second
- [ ] Streaming is smooth (no stuttering)
- [ ] Total response time < 10 seconds

**Pass/Fail**: ___________

---

#### Test Case 3.3.3: Long Conversation Scroll
**Steps**:
1. Create conversation with 50+ messages
2. Scroll through history

**Expected Results**:
- [ ] Scroll is smooth (60fps)
- [ ] No jank or lag
- [ ] Auto-scroll to bottom on new message
- [ ] Pagination or virtualization for large lists

**Pass/Fail**: ___________

---

## 4. Security Tests

### 4.1 XSS Protection
**Steps**:
1. Try sending: `<script>alert('XSS')</script>`
2. Check if script executes

**Expected Results**:
- [ ] Script tags are escaped
- [ ] No alert shown
- [ ] Content displayed as plain text

**Pass/Fail**: ___________

---

### 4.2 SQL Injection
**Steps**:
1. Try query: `'; DROP TABLE episodes; --`
2. Verify database remains intact

**Expected Results**:
- [ ] Query treated as text, not SQL
- [ ] No database changes
- [ ] Logs show sanitized input

**Pass/Fail**: ___________

---

### 4.3 API Rate Limiting
**Steps**:
1. Send 100 rapid requests to `/api/v1/chat`
2. Check for rate limit response

**Expected Results**:
- [ ] Requests blocked after threshold
- [ ] 429 status code returned
- [ ] Retry-After header present

**Pass/Fail**: ___________

---

## 5. Data Persistence

### 5.1 Session Persistence
**Steps**:
1. Create conversation
2. Refresh page
3. Verify session restored

**Expected Results**:
- [ ] Session ID preserved (localStorage)
- [ ] Message history reloaded
- [ ] Current session highlighted

**Pass/Fail**: ___________

---

### 5.2 Settings Persistence
**Steps**:
1. Change model selection
2. Refresh page
3. Check if setting persists

**Expected Results**:
- [ ] Model choice remembered
- [ ] Sidebar collapsed state preserved
- [ ] Theme settings persist (future)

**Pass/Fail**: ___________

---

## 6. Edge Cases

### 6.1 Very Long Message
**Steps**:
1. Paste 10,000+ character message
2. Send

**Expected Results**:
- [ ] Message truncated or rejected gracefully
- [ ] Error message if over limit
- [ ] No server crash

**Pass/Fail**: ___________

---

### 6.2 Rapid Consecutive Messages
**Steps**:
1. Send 5 messages rapidly without waiting for responses

**Expected Results**:
- [ ] All messages queued properly
- [ ] Responses arrive in order
- [ ] No lost messages

**Pass/Fail**: ___________

---

### 6.3 Special Characters
**Steps**:
1. Send message with emojis, unicode, symbols: `🚀 Testing €100 © ™`

**Expected Results**:
- [ ] All characters display correctly
- [ ] No encoding errors
- [ ] Markdown still works

**Pass/Fail**: ___________

---

## 7. Cross-Browser Testing

### 7.1 Chrome/Chromium
- [ ] All features work
- [ ] No console errors
- [ ] Performance acceptable

**Pass/Fail**: ___________

---

### 7.2 Firefox
- [ ] All features work
- [ ] No console errors
- [ ] Performance acceptable

**Pass/Fail**: ___________

---

### 7.3 Safari
- [ ] All features work
- [ ] No console errors
- [ ] Performance acceptable

**Pass/Fail**: ___________

---

### 7.4 Edge
- [ ] All features work
- [ ] No console errors
- [ ] Performance acceptable

**Pass/Fail**: ___________

---

## 8. Deployment Verification

### 8.1 Docker Health Checks
```bash
docker-compose ps
docker-compose logs api
docker-compose logs frontend
docker-compose logs postgres
```

**Expected Results**:
- [ ] All containers show "healthy" status
- [ ] No error logs in recent output
- [ ] Resource usage reasonable (< 2GB RAM)

**Pass/Fail**: ___________

---

### 8.2 Environment Variables
**Steps**:
1. Review `.env.example`
2. Verify all required vars documented
3. Test with missing optional vars

**Expected Results**:
- [ ] App starts with only required vars
- [ ] Clear error messages for missing required vars
- [ ] Graceful degradation for optional vars

**Pass/Fail**: ___________

---

## 9. Test Summary

### Overall Results
- **Total Test Cases**: 50+
- **Passed**: _______
- **Failed**: _______
- **Blocked**: _______
- **Not Tested**: _______

### Critical Issues Found
1. ___________________________________
2. ___________________________________
3. ___________________________________

### Recommendations
1. ___________________________________
2. ___________________________________
3. ___________________________________

### Sign-off
**Tester**: ________________  
**Date**: September 16, 2026  
**Status**: ☐ Ready for Production  ☐ Needs Fixes  
**Notes**: _________________________________
