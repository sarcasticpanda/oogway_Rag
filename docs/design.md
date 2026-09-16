# UI/UX Design Document
## Lenny Growth Assistant

**Version**: 1.0  
**Last Updated**: September 16, 2026  
**Status**: Production Ready

---

## Table of Contents
1. [Design Philosophy](#1-design-philosophy)
2. [Design Principles](#2-design-principles)
3. [Information Architecture](#3-information-architecture)
4. [Visual Design System](#4-visual-design-system)
5. [Key Interaction States](#5-key-interaction-states)
6. [Responsive Behavior](#6-responsive-behavior)
7. [Accessibility](#7-accessibility)
8. [Design Decisions](#8-design-decisions)

---

## 1. Design Philosophy

### Vision
Create a **conversational AI interface** that feels natural, trustworthy, and focused—removing friction between questions and answers while maintaining transparency about sources and limitations.

### Core Values
1. **Clarity over Complexity**: Simple, uncluttered interface that doesn't overwhelm
2. **Trust through Transparency**: Always show sources, never hide AI limitations
3. **Speed without Sacrifice**: Fast responses without compromising quality
4. **Accessible to All**: WCAG AA compliance, keyboard navigation, semantic HTML

### User Experience Goals
- **Onboarding**: User asks first question within 30 seconds of landing
- **Engagement**: Natural conversation flow, not a search interface
- **Discovery**: Artifacts and knowledge base encourage exploration
- **Confidence**: Source citations build trust in AI responses

---

## 2. Design Principles

### Principle 1: Conversation-First
**What it means**: The chat interface is the primary interaction, not a sidebar feature  
**How it's applied**:
- Chat takes center stage (60-70% of viewport width)
- Sidebar is collapsible but accessible
- Message input is always visible and focused
- No distracting header navigation

**Anti-pattern**: Complex multi-panel layouts that compete for attention

---

### Principle 2: Progressive Disclosure
**What it means**: Show advanced features only when users need them  
**How it's applied**:
- Model selector: Hidden in header, revealed on click
- Artifacts: Generated on-demand, not pre-loaded
- Knowledge base: Separate tab, not inline in chat
- Settings: Modal overlay, not persistent panel

**Anti-pattern**: Everything-visible-at-once dashboard sprawl

---

### Principle 3: Feedback at Every Step
**What it means**: Users always know what's happening  
**How it's applied**:
- Loading states: Pulsing dots for AI thinking
- Streaming: Words appear as they're generated
- Success/error: Toast notifications with clear messages
- Upload progress: Percentage bar for documents

**Anti-pattern**: Silent operations that leave users guessing

---

### Principle 4: Forgiving Interactions
**What it means**: Easy to undo, hard to lose data  
**How it's applied**:
- Sessions auto-save every message
- Delete requires confirmation
- No destructive actions without warning
- Draft messages preserved on tab switch

**Anti-pattern**: One-click-and-it's-gone destructive actions

---

### Principle 5: Performance is a Feature
**What it means**: Design choices that improve perceived speed  
**How it's applied**:
- Optimistic UI updates (show message immediately)
- Skeleton loaders instead of spinners
- Lazy loading for session history
- Streaming responses (no waiting for full reply)

**Anti-pattern**: Blocking operations that freeze the UI

---

## 3. Information Architecture

### Site Map

```
Home (Chat Interface)
├── Active Conversation
│   ├── Message History
│   ├── Message Input
│   └── Follow-up Suggestions
├── Sidebar (Collapsible)
│   ├── New Chat Button
│   ├── Session History
│   │   ├── Today
│   │   ├── Yesterday
│   │   └── Older
│   ├── Knowledge Base (Tab)
│   │   ├── Episode List
│   │   └── Upload Document
│   ├── Artifacts (Tab)
│   │   └── Generated Content List
│   └── Profile/Settings
└── Header
    ├── Logo
    ├── Model Selector
    └── Collapse Sidebar Toggle
```

### Navigation Patterns

**Primary Navigation**: Tabs in sidebar
- Knowledge Base
- Artifacts
- (Future: Analytics, Team)

**Secondary Navigation**: Inline actions
- New Chat (button)
- Delete Session (hover action)
- Export Artifact (artifact view)

**Tertiary Navigation**: Modals/overlays
- Settings
- Model configuration
- Upload dialogs

---

## 4. Visual Design System

### 4.1 Color Palette

#### Light Mode (Default)
```css
/* Base Colors */
--background: #ffffff;        /* Main background */
--foreground: #0a0a0a;        /* Primary text */
--muted: #f5f5f5;             /* Subtle backgrounds */
--muted-foreground: #737373;  /* Secondary text */

/* Interactive */
--primary: #0f172a;           /* Primary actions */
--primary-foreground: #f8fafc; /* Text on primary */
--accent: #f1f5f9;            /* Hover states */
--accent-foreground: #0f172a; /* Text on accent */

/* Semantic */
--success: #10b981;           /* Success messages */
--warning: #f59e0b;           /* Warnings */
--error: #ef4444;             /* Errors */
--info: #3b82f6;              /* Info messages */

/* Borders */
--border: #e5e7eb;            /* Default borders */
--input: #e5e7eb;             /* Input borders */
--ring: #0f172a;              /* Focus rings */
```

#### Dark Mode (Future)
```css
--background: #0a0a0a;
--foreground: #fafafa;
--muted: #171717;
--muted-foreground: #a3a3a3;
/* ... */
```

### 4.2 Typography

**Font Family**:
```css
--font-sans: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif;
--font-mono: 'Fira Code', 'Courier New', monospace;
```

**Type Scale**:
```css
/* Headings */
--text-4xl: 2.25rem;   /* Page titles */
--text-3xl: 1.875rem;  /* Section headers */
--text-2xl: 1.5rem;    /* Card titles */
--text-xl: 1.25rem;    /* Subsections */
--text-lg: 1.125rem;   /* Large body */

/* Body */
--text-base: 1rem;      /* Default (16px) */
--text-sm: 0.875rem;    /* Small labels */
--text-xs: 0.75rem;     /* Captions */
```

**Font Weights**:
- Regular: 400 (body text)
- Medium: 500 (labels, buttons)
- Semibold: 600 (headings)

**Line Heights**:
- Tight: 1.25 (headings)
- Normal: 1.5 (body text)
- Relaxed: 1.75 (long-form content)

### 4.3 Spacing System

**Base Unit**: 4px (0.25rem)

```css
/* Spacing Scale */
--space-1: 0.25rem;  /* 4px */
--space-2: 0.5rem;   /* 8px */
--space-3: 0.75rem;  /* 12px */
--space-4: 1rem;     /* 16px */
--space-5: 1.25rem;  /* 20px */
--space-6: 1.5rem;   /* 24px */
--space-8: 2rem;     /* 32px */
--space-10: 2.5rem;  /* 40px */
--space-12: 3rem;    /* 48px */
--space-16: 4rem;    /* 64px */
```

**Application**:
- Message padding: 16px (--space-4)
- Button padding: 12px 24px (--space-3 --space-6)
- Section gaps: 24px (--space-6)
- Page margins: 32px (--space-8)

### 4.4 Border Radius

```css
--radius-sm: 0.25rem;   /* 4px - Small elements */
--radius-md: 0.5rem;    /* 8px - Default */
--radius-lg: 0.75rem;   /* 12px - Cards */
--radius-xl: 1rem;      /* 16px - Modals */
--radius-full: 9999px;  /* Pills, avatars */
```

### 4.5 Shadows

```css
/* Elevation System */
--shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
--shadow-md: 0 4px 6px rgba(0, 0, 0, 0.07);
--shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
--shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.15);
```

**Usage**:
- Cards: shadow-sm
- Dropdowns: shadow-md
- Modals: shadow-lg
- Popovers: shadow-xl

### 4.6 Component Styles

#### Buttons
```css
/* Primary Button */
.btn-primary {
  background: var(--primary);
  color: var(--primary-foreground);
  padding: 0.75rem 1.5rem;
  border-radius: var(--radius-md);
  font-weight: 500;
  transition: all 150ms ease;
}

.btn-primary:hover {
  background: var(--primary-hover);
  transform: translateY(-1px);
}

/* Secondary Button */
.btn-secondary {
  background: var(--accent);
  color: var(--accent-foreground);
  /* ... */
}

/* Ghost Button */
.btn-ghost {
  background: transparent;
  color: var(--foreground);
  border: 1px solid var(--border);
  /* ... */
}
```

#### Input Fields
```css
.input {
  background: var(--background);
  border: 1px solid var(--input);
  border-radius: var(--radius-md);
  padding: 0.75rem 1rem;
  font-size: var(--text-base);
  transition: border-color 150ms ease;
}

.input:focus {
  border-color: var(--ring);
  outline: 2px solid var(--ring);
  outline-offset: 2px;
}
```

#### Message Bubbles
```css
/* User Message */
.message-user {
  background: var(--accent);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  margin-left: auto;
  max-width: 80%;
}

/* Assistant Message */
.message-assistant {
  background: var(--muted);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  max-width: 85%;
}
```

---

## 5. Key Interaction States

### 5.1 Chat States

#### Empty State
**Visual**: Large centered content
```
┌─────────────────────────────────────┐
│                                     │
│         🎙️ Lenny Growth            │
│           Assistant                 │
│                                     │
│   How can I help you grow?          │
│                                     │
│   Ask about Lenny's podcast...      │
│                                     │
│   [Suggested Questions Below]       │
│   • What is product-led growth?     │
│   • How to improve retention?       │
│   • Growth frameworks                │
│                                     │
└─────────────────────────────────────┘
```

#### Loading State
**Visual**: Pulsing dots
```
User: What is product-led growth?
Assistant: ● ● ● (pulsing animation)
```

#### Streaming Response
**Visual**: Words appear incrementally
```
User: What is product-led growth?
Assistant: Product-led growth (PLG) is a go-to-market
           strategy where the product itself drives...
           [streaming, cursor blinks at end]
```

#### Response Complete
**Visual**: Full message with actions
```
User: What is product-led growth?
Assistant: [Full response with markdown formatting]
           
           Sources:
           • April Dunford episode (42:15)
           • Brian Balfour episode (28:30)
           
           [Copy] [Follow-up: Tell me more]
```

#### Error State
**Visual**: Red border, error message
```
Assistant: ⚠️ I encountered an error generating
           that response. 
           
           [Retry] [Report Issue]
```

### 5.2 Upload States

#### Idle
```
┌───────────────────────────────┐
│  📄 Upload Document            │
│                                │
│  Drop PDF or DOCX here         │
│  or click to browse            │
│                                │
│  Max size: 10MB                │
└───────────────────────────────┘
```

#### Uploading
```
┌───────────────────────────────┐
│  📄 Uploading...               │
│                                │
│  document.pdf                  │
│  [████████░░] 80%             │
│                                │
└───────────────────────────────┘
```

#### Success
```
┌───────────────────────────────┐
│  ✅ Upload Complete            │
│                                │
│  document.pdf                  │
│  Processed 45 chunks           │
│                                │
│  [View in Knowledge Base]      │
└───────────────────────────────┘
```

### 5.3 Model Selector States

#### Closed
```
[Header: 📊 gpt-4o-mini ▼]
```

#### Open
```
┌────────────────────────────┐
│  OpenAI                    │
│  • gpt-4o          [✓]     │
│  • gpt-4o-mini             │
│  • gpt-3.5-turbo           │
│                            │
│  Anthropic                 │
│  • claude-3.5-sonnet       │
│  • claude-3-opus           │
│                            │
│  Groq                      │
│  • llama-3-70b             │
│                            │
│  Ollama (Local)            │
│  • qwen2.5-coder:3b        │
└────────────────────────────┘
```

### 5.4 Session History States

#### Loading
```
Sidebar:
  [New Chat]
  
  Today
  ● ● ● Loading...
```

#### Loaded
```
Sidebar:
  [New Chat]
  
  Today
  • Product-led growth discussion
  • Retention strategies
  
  Yesterday
  • Hiring best practices
  • Pricing models
  
  Last 7 days
  • 12 more conversations
```

#### Hover
```
• Product-led growth discussion
  [🗑️ Delete] [📋 Copy Link]
```

---

## 6. Responsive Behavior

### 6.1 Breakpoints

```css
/* Mobile First Approach */
--screen-sm: 640px;   /* Small tablets */
--screen-md: 768px;   /* Tablets */
--screen-lg: 1024px;  /* Laptops */
--screen-xl: 1280px;  /* Desktops */
--screen-2xl: 1536px; /* Large screens */
```

### 6.2 Layout Adaptations

#### Desktop (≥1024px)
```
┌─────────────────────────────────────────────────┐
│ Header                                          │
├───────┬─────────────────────────────────────────┤
│       │                                         │
│ Side  │         Main Chat Area                  │
│ bar   │                                         │
│       │         (60-70% width)                  │
│ 20%   │                                         │
│       │                                         │
└───────┴─────────────────────────────────────────┘
```

**Characteristics**:
- Sidebar always visible (can be collapsed)
- Chat area centered, max-width 900px
- Artifacts open in side panel (right 30%)
- Keyboard shortcuts enabled

#### Tablet (768px - 1023px)
```
┌───────────────────────────────────────┐
│ Header                [≡]             │
├───────────────────────────────────────┤
│                                       │
│         Main Chat Area                │
│         (Full Width)                  │
│                                       │
└───────────────────────────────────────┘
```

**Characteristics**:
- Sidebar collapses to hamburger menu
- Chat uses full width
- Artifacts open as overlay modals
- Touch-optimized hit areas (44px minimum)

#### Mobile (<768px)
```
┌─────────────────┐
│ [≡] Logo    [⚙]│
├─────────────────┤
│                 │
│   Chat Area     │
│   (100% width)  │
│                 │
│                 │
│                 │
├─────────────────┤
│ [Type here...]  │
└─────────────────┘
```

**Characteristics**:
- Header sticky at top
- Input sticky at bottom
- Sidebar as full-screen overlay
- Simplified navigation
- Larger touch targets

### 6.3 Font Scaling

```css
/* Mobile */
@media (max-width: 767px) {
  :root {
    font-size: 14px; /* Base size */
  }
}

/* Tablet */
@media (min-width: 768px) and (max-width: 1023px) {
  :root {
    font-size: 15px;
  }
}

/* Desktop */
@media (min-width: 1024px) {
  :root {
    font-size: 16px;
  }
}
```

### 6.4 Interaction Adaptations

| Feature | Desktop | Tablet | Mobile |
|---------|---------|--------|--------|
| Hover effects | Yes | Limited | No |
| Keyboard shortcuts | Yes | Yes | No |
| Swipe gestures | No | Yes | Yes |
| Context menus | Right-click | Long-press | Long-press |
| Multi-select | Shift+Click | Tap checkboxes | Tap checkboxes |

---

## 7. Accessibility

### 7.1 WCAG 2.1 AA Compliance

#### Perceivable
✅ **Text Contrast**: All text meets 4.5:1 ratio (7:1 for large text)
✅ **Color Independence**: Never rely on color alone to convey information
✅ **Resizable Text**: Support up to 200% zoom without loss of functionality
✅ **Alt Text**: All images and icons have descriptive alternatives

#### Operable
✅ **Keyboard Navigation**: All features accessible via keyboard
✅ **Focus Indicators**: Visible 2px outline on focused elements
✅ **No Time Limits**: Streaming responses can be paused
✅ **Skip Links**: "Skip to main content" link for screen readers

#### Understandable
✅ **Consistent Navigation**: Same patterns across all pages
✅ **Clear Labels**: All inputs have associated labels
✅ **Error Messages**: Specific, actionable error descriptions
✅ **Predictable Behavior**: No unexpected context changes

#### Robust
✅ **Semantic HTML**: Proper use of `<header>`, `<main>`, `<nav>`, etc.
✅ **ARIA Labels**: Descriptive labels for interactive elements
✅ **Valid HTML**: Passes W3C validation
✅ **Screen Reader Tested**: Works with NVDA and VoiceOver

### 7.2 Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl/Cmd + K` | Focus search/input |
| `Ctrl/Cmd + N` | New chat |
| `Ctrl/Cmd + /` | Toggle sidebar |
| `Ctrl/Cmd + ,` | Open settings |
| `Escape` | Close modal/cancel |
| `Enter` | Send message |
| `Shift + Enter` | New line in message |
| `↑` / `↓` | Navigate sessions |

### 7.3 Screen Reader Support

**Announcements**:
```html
<!-- Loading state -->
<div role="status" aria-live="polite">
  Generating response...
</div>

<!-- Success -->
<div role="status" aria-live="polite">
  Response complete. 3 sources cited.
</div>

<!-- Error -->
<div role="alert" aria-live="assertive">
  Error: Could not generate response. Please try again.
</div>
```

**Landmarks**:
```html
<header role="banner">
  <nav role="navigation" aria-label="Main">
</header>

<aside role="complementary" aria-label="Session history">

<main role="main" aria-label="Chat conversation">

<form role="search" aria-label="Send message">
```

### 7.4 Focus Management

**Focus Trap in Modals**:
```javascript
// When modal opens
modalElement.focus();
trapFocusWithin(modalElement);

// Tab cycles within modal only
// Escape closes and returns focus to trigger
```

**Focus Restoration**:
```javascript
// After deleting session
focusPreviousSession();

// After closing artifact
returnFocusToTriggerButton();
```

---

## 8. Design Decisions

### 8.1 Why No User Authentication (v1)?

**Decision**: Launch without login/auth  
**Rationale**:
- Reduces friction to try the product
- Simpler deployment (no auth backend)
- Faster iteration on core experience
- Local sessions via browser storage

**Trade-offs**:
- ❌ No cross-device sync
- ❌ No data persistence across browsers
- ✅ Privacy-friendly (no user tracking)
- ✅ Faster time-to-value

**Future**: Add optional login for premium features

---

### 8.2 Why Streaming Responses?

**Decision**: Stream AI responses word-by-word  
**Rationale**:
- **Perceived Speed**: User sees progress immediately (feels 2-3x faster)
- **Early Feedback**: User can stop if off-track
- **Engagement**: More engaging to watch than waiting for full response

**Implementation**:
```typescript
// Frontend receives Server-Sent Events
const eventSource = new EventSource('/api/v1/chat/stream');
eventSource.onmessage = (event) => {
  appendToMessage(event.data);
};
```

**Alternative Considered**: Wait for full response  
**Rejected Because**: Feels slow, users lose confidence

---

### 8.3 Why Sidebar for Sessions (Not Tabs)?

**Decision**: Vertical sidebar with collapsible session list  
**Rationale**:
- **Scannable**: Easy to browse 10-20 recent chats
- **Persistent**: Always accessible, doesn't hide content
- **Familiar**: Pattern used by ChatGPT, Claude, etc.

**Alternative Considered**: Top navigation tabs  
**Rejected Because**: Horizontal space limited, doesn't scale

---

### 8.4 Why Artifacts as Separate Tab?

**Decision**: Artifacts live in dedicated tab, not inline  
**Rationale**:
- **Focus**: Keep chat uncluttered
- **Reusability**: Artifacts are meant to be referenced later
- **Browsing**: Easy to see all artifacts at once

**Alternative Considered**: Inline in chat messages  
**Rejected Because**: Clutters conversation, hard to find later

---

### 8.5 Why Minimal Header?

**Decision**: Slim header with just logo + model selector  
**Rationale**:
- **Vertical Space**: Maximizes chat area (most important)
- **Distraction-Free**: No complex navigation competing for attention
- **Clean Aesthetic**: Modern, focused look

**Alternative Considered**: Full navigation bar  
**Rejected Because**: Chat is 90% of use case, doesn't need nav

---

### 8.6 Why No Dark Mode (v1)?

**Decision**: Light mode only initially  
**Rationale**:
- **Scope**: Limited time, focus on core features
- **Testing**: Fewer edge cases to test
- **Future**: Easy to add with CSS variables

**Trade-offs**:
- ❌ Some users prefer dark mode
- ✅ Faster launch, more polish on single mode

**Future**: Toggle in settings (already architected with CSS vars)

---

### 8.7 Why @ Command for Artifacts?

**Decision**: Use `@artifact` syntax to trigger generation  
**Rationale**:
- **Discoverability**: Easy to explain in placeholder text
- **Familiarity**: Similar to Slack mentions, Discord commands
- **Explicit**: Clear user intent (not accidental)

**Example**:
```
User: @artifact report: Summarize growth strategies
System: [Generates structured report artifact]
```

**Alternative Considered**: Automatic detection  
**Rejected Because**: Too magical, risk of false positives

---

### 8.8 Why No Conversation Branching?

**Decision**: Linear conversations only (no tree structure)  
**Rationale**:
- **Simplicity**: Easier to understand and implement
- **Common Case**: Most users have linear chats
- **Mobile-Friendly**: Branching UX is complex on small screens

**Alternative Considered**: ChatGPT-style branching  
**Rejected Because**: Added complexity for rare use case

**Future**: Consider if user research shows need

---

### 8.9 Typography Choice: Inter

**Decision**: Use Inter font family  
**Rationale**:
- **Readability**: Designed for interfaces, excellent at small sizes
- **Open Source**: Free, no licensing issues
- **Modern**: Clean, professional look
- **Variable Font**: Supports multiple weights efficiently

**Alternative Considered**: System fonts only  
**Rejected Because**: Inconsistent rendering across platforms

---

### 8.10 Why No Emoji Reactions?

**Decision**: No reactions on messages (v1)  
**Rationale**:
- **Single User**: No collaboration features yet
- **Scope**: Focus on core chat experience
- **Utility**: Low value vs. implementation cost

**Future**: Add when team features are introduced

---

## Appendix

### A. Design Inspiration

**Influenced by**:
- ChatGPT: Conversation-first layout
- Linear: Clean, minimal aesthetic
- Notion: Markdown editor experience
- Superhuman: Keyboard-first design

**Differentiated by**:
- Source citations (transparency)
- Artifact system (structured output)
- Knowledge base integration (domain-specific)

### B. User Testing Insights

**Findings from 5 user tests** (September 2026):
1. **Sidebar confusion**: 2/5 didn't notice session history
   - **Fix**: Made "New Chat" button more prominent
2. **Model selector**: Users didn't understand provider differences
   - **Fix**: Added tooltips explaining speed/cost trade-offs
3. **Artifact command**: 4/5 needed prompt to try `@artifact`
   - **Fix**: Added example in input placeholder
4. **Source links**: Users wanted timestamps, not just episode titles
   - **Fix**: Added (MM:SS) format to citations
5. **Mobile input**: Keyboard covered messages
   - **Fix**: Made input sticky, auto-scroll on type

### C. Component Library

**Built with**:
- Tailwind CSS for utility classes
- Custom components (no UI library)
- Radix UI primitives (future: dropdowns, modals)

**Why custom?**:
- **Control**: Exact design match
- **Performance**: No unused code
- **Learning**: Understand patterns deeply

### D. Future Design Enhancements

**Planned for v1.1+**:
1. Dark mode support
2. Customizable themes (color accents)
3. Rich text input (bold, italic, etc.)
4. Inline code editing in artifacts
5. Drag-and-drop session reordering
6. Conversation search/filter
7. Voice input support
8. Collaborative sessions (multi-user)

---

**Document Version**: 1.0  
**Last Updated**: September 16, 2026  
**Design Reviews**: Ongoing (post-launch iterations)
