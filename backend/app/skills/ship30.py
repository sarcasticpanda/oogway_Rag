import re
from typing import Tuple, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.factory import AIProviderFactory
from app.rag.retrieve import retrieve_context
from app.schemas.session import CitationItem

SHIP30_SYSTEM_PROMPT = """You are a master digital writer and atomic essayist certified in the Ship 30 for 30 methodology.
Your mission is to write a comprehensive, deeply compelling, actionable long-form atomic essay (~1,200 to 1,300 words, targeting 1,250 words) based strictly on Lenny Rachitsky's podcast knowledge base.

Ship 30 for 30 Writing Principles to obey:
1. HEADLINE: Create a punchy, high-converting headline using one of the proven formats:
   - How to [Achieve Desirable Result] Without [Common Pain Point]
   - [Number] Unconventional Lessons on [Topic] from Top Tech Operators
   - The [Framework Name]: Why Most People Fail at [Topic] (And How to Fix It)
2. THE HOOK (First 2-3 sentences):
   - Call out the reader directly.
   - Contrast common conventional wisdom against operational reality.
   - Establish immediate stakes.
3. RHYTHM & PACING (Rate of Revelation):
   - Use 1-sentence paragraphs for emphasis.
   - Vary paragraph length (1-3 sentences max).
   - Use bold lead-ins for key insights.
   - No walls of text. Every line must pull the reader into the next.
4. EVIDENCE & OPERATOR GROUNDING:
   - Deeply weave in real operator case studies, quotes, and frameworks from the provided Lenny podcast sources.
   - Attribute every major concept to the specific guest (e.g. "As Brian Chesky explained on Lenny's Podcast...", "Elena Verna's B2B PLG loop demonstrates...").
   - If the provided context does not have enough detail for an assertion, do NOT fabricate facts or guest names.
5. ACTIONABLE FRAMEWORKS:
   - Break strategies into clear, numbered tactical steps.
   - Include concrete "Do This / Don't Do That" contrast tables or lists.
6. TARGET WORD COUNT:
   - Write approximately 1,250 words (between 1,150 and 1,350 words). Provide thorough, in-depth analysis so that it meets this length requirement.

OUTPUT FORMAT:
Provide the complete essay in clean Markdown with clear headings (H1, H2, H3), bullet points, and blockquotes for operator quotes.
"""

SHIP30_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
  :root {{
    --bg-primary: #0f172a;
    --bg-card: #1e293b;
    --text-primary: #f8fafc;
    --text-secondary: #94a3b8;
    --accent: #38bdf8;
    --accent-gradient: linear-gradient(135deg, #38bdf8, #818cf8);
    --border: #334155;
    --quote-bg: rgba(56, 189, 248, 0.08);
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    background-color: var(--bg-primary);
    color: var(--text-primary);
    line-height: 1.75;
    padding: 2.5rem 1.5rem;
    display: flex;
    justify-content: center;
  }}
  .article-container {{
    max-width: 800px;
    width: 100%;
  }}
  .badge {{
    display: inline-block;
    background: var(--quote-bg);
    color: var(--accent);
    border: 1px solid var(--border);
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-bottom: 1.25rem;
  }}
  h1 {{
    font-size: 2.5rem;
    font-weight: 800;
    line-height: 1.2;
    margin-bottom: 1rem;
    background: var(--accent-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }}
  .meta-bar {{
    display: flex;
    gap: 1.5rem;
    color: var(--text-secondary);
    font-size: 0.875rem;
    border-bottom: 1px solid var(--border);
    padding-bottom: 1.5rem;
    margin-bottom: 2rem;
  }}
  p {{
    margin-bottom: 1.25rem;
    color: #e2e8f0;
    font-size: 1.05rem;
  }}
  p.lead {{
    font-size: 1.25rem;
    font-weight: 500;
    color: var(--text-primary);
  }}
  h2 {{
    font-size: 1.6rem;
    font-weight: 700;
    margin-top: 2.5rem;
    margin-bottom: 1rem;
    color: #f1f5f9;
    border-left: 4px solid var(--accent);
    padding-left: 0.75rem;
  }}
  h3 {{
    font-size: 1.25rem;
    font-weight: 600;
    margin-top: 1.75rem;
    margin-bottom: 0.75rem;
    color: #cbd5e1;
  }}
  ul, ol {{
    margin-left: 1.5rem;
    margin-bottom: 1.5rem;
    color: #cbd5e1;
  }}
  li {{ margin-bottom: 0.5rem; }}
  blockquote {{
    background: var(--quote-bg);
    border-left: 4px solid var(--accent);
    padding: 1.25rem 1.5rem;
    border-radius: 0 8px 8px 0;
    margin: 1.5rem 0;
    font-style: italic;
    color: #f8fafc;
  }}
  .sources-panel {{
    margin-top: 3.5rem;
    padding: 1.5rem;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
  }}
  .sources-panel h4 {{
    color: var(--accent);
    margin-bottom: 0.75rem;
    font-size: 1rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }}
  .citation-card {{
    font-size: 0.875rem;
    color: var(--text-secondary);
    padding: 0.5rem 0;
    border-top: 1px solid var(--border);
  }}
  .citation-card strong {{ color: var(--text-primary); }}
</style>
</head>
<body>
<div class="article-container">
  <div class="badge">Ship 30 for 30 • Lenny Rachitsky Masterclass</div>
  <h1>{title}</h1>
  <div class="meta-bar">
    <span>Target: ~1,250 Words</span>
    <span>Actual: ~{word_count} Words</span>
    <span>Format: Atomic Operator Essay</span>
  </div>
  <div class="content">
    {body_html}
  </div>
  <div class="sources-panel">
    <h4>Verified Lenny Podcast Citations</h4>
    {citations_html}
  </div>
</div>
</body>
</html>
"""

def simple_markdown_to_html(md: str) -> str:
    """Lightweight markdown to clean HTML converter without external heavy deps."""
    html = md
    # Escape special brackets if needed, but keep basic html tags
    lines = html.split("\n")
    output = []
    in_list = False

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if in_list:
                output.append("</ul>")
                in_list = False
            continue

        if stripped.startswith("# "):
            if in_list:
                output.append("</ul>")
                in_list = False
            # Skip top H1 since it is rendered in header
            continue
        elif stripped.startswith("## "):
            if in_list:
                output.append("</ul>")
                in_list = False
            output.append(f"<h2>{stripped[3:]}</h2>")
        elif stripped.startswith("### "):
            if in_list:
                output.append("</ul>")
                in_list = False
            output.append(f"<h3>{stripped[4:]}</h3>")
        elif stripped.startswith("> "):
            if in_list:
                output.append("</ul>")
                in_list = False
            output.append(f"<blockquote>{stripped[2:]}</blockquote>")
        elif stripped.startswith("- ") or stripped.startswith("* "):
            if not in_list:
                output.append("<ul>")
                in_list = True
            item_text = stripped[2:]
            # format bold
            item_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', item_text)
            output.append(f"<li>{item_text}</li>")
        else:
            if in_list:
                output.append("</ul>")
                in_list = False
            p_text = stripped
            p_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', p_text)
            output.append(f"<p>{p_text}</p>")

    if in_list:
        output.append("</ul>")

    return "\n".join(output)

async def generate_ship30_essay(
    topic: str,
    db: AsyncSession,
    provider: str | None = None,
  model: str | None = None,
  api_key: str | None = None,
  base_url: str | None = None,
) -> Tuple[str, str, int, List[CitationItem], str]:
    """
    Executes the Ship 30 for 30 writing workflow:
    1. Retrieves relevant Lenny podcast evidence via pgvector.
    2. Builds structured writing prompt with Ship 30 constraints (~1,250 words).
    3. Calls LLM via Provider abstraction.
    4. Evaluates word count and generates both Markdown and sandboxed HTML representations.
    Returns:
      (markdown_content, html_content, word_count, citations, essay_title)
    """
    context_str, citations, is_grounded = await retrieve_context(topic, db, top_k=8)

    user_prompt = f"""TOPIC REQUESTED: {topic}

RETRIEVED PODCAST EVIDENCE:
{context_str if context_str else "No transcripts directly matched this query. Please state clearly that this topic is not documented in Lenny's podcast."}

INSTRUCTIONS:
Write an exceptional, in-depth Ship 30 for 30 atomic essay (~1,250 words) on this topic.
Ensure you start with an attention-grabbing H1 headline. Ground your points in the provided operator evidence.
"""

    chat_provider = AIProviderFactory.get_chat_provider(
        provider=provider,
        model=model,
        api_key=api_key,
        base_url=base_url,
    )
    messages = [
        {"role": "system", "content": SHIP30_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]

    response_text = await chat_provider.complete(messages, max_tokens=2500, temperature=0.7)

    # Programmatic word-count verification loop (Req 11.2)
    # Target 1,150 – 1,350 words; if too short, ask the model to expand.
    for attempt in range(3):
        words = response_text.split()
        word_count = len(words)
        if 1150 <= word_count <= 1350:
            break
        direction = "expand" if word_count < 1150 else "tighten"
        expand_prompt = SHIP30_SYSTEM_PROMPT + (
            f"\n\nThe previous draft was {word_count} words. The required range is 1,150–1,350 words. "
            f"Please {direction} the draft so the next version is within that range. "
            f"Preserve transcript-grounded claims, the headline, and the core structure.\n\n"
            f"CURRENT DRAFT:\n{response_text}"
        )
        response_text = await chat_provider.complete(
            [{"role": "system", "content": expand_prompt}],
            max_tokens=2500,
            temperature=0.7
        )

    # Calculate actual word count
    words = response_text.split()
    word_count = len(words)
    if not 1150 <= word_count <= 1350:
        raise ValueError(f"Ship30 generation produced {word_count} words after 3 attempts; expected 1150-1350.")

    # Extract title from first H1 or first line
    title = f"Atomic Essay: {topic.title()}"
    for line in response_text.split("\n"):
        if line.startswith("# "):
            title = line.replace("# ", "").strip()
            break

    # Build citations HTML
    citations_html_parts = []
    for c in citations:
        citations_html_parts.append(
            f'<div class="citation-card">'
            f'<strong>{c.guest_name}</strong> — <em>"{c.episode_title}"</em> ({c.chapter_title})<br/>'
            f'<span>"{c.quote}"</span>'
            f'</div>'
        )
    citations_html = "\n".join(citations_html_parts) if citations_html_parts else "<p>General product synthesis</p>"

    # Convert markdown body to styled HTML
    body_html = simple_markdown_to_html(response_text)
    html_content = SHIP30_HTML_TEMPLATE.format(
        title=title,
        word_count=word_count,
        body_html=body_html,
        citations_html=citations_html
    )

    return response_text, html_content, word_count, citations, title
