import pytest
from app.skills.ship30 import SHIP30_SYSTEM_PROMPT, simple_markdown_to_html, SHIP30_HTML_TEMPLATE

def test_ship30_prompt_structure():
    """Verify Ship 30 writing prompt contains core principles and target word count."""
    assert "Ship 30 for 30" in SHIP30_SYSTEM_PROMPT
    assert "1,250 words" in SHIP30_SYSTEM_PROMPT
    assert "HEADLINE" in SHIP30_SYSTEM_PROMPT
    assert "THE HOOK" in SHIP30_SYSTEM_PROMPT
    assert "RHYTHM & PACING" in SHIP30_SYSTEM_PROMPT
    assert "EVIDENCE & OPERATOR GROUNDING" in SHIP30_SYSTEM_PROMPT

def test_markdown_to_html_formatting():
    """Verify custom markdown to HTML conversion formats headers, bolding, and lists."""
    md_sample = """# Main Title
## The Core Framework
As Brian Chesky stated:
> Do things that don't scale.
- Point 1: **Speed** matters
- Point 2: Focus on retention
"""
    html_out = simple_markdown_to_html(md_sample)
    assert "<h2>The Core Framework</h2>" in html_out
    assert "<blockquote>Do things that don't scale.</blockquote>" in html_out
    assert "<ul>" in html_out
    assert "<li>Point 1: <strong>Speed</strong> matters</li>" in html_out

def test_html_template_isolation():
    """Ensure HTML template does not load external tracking scripts or parent window accessors."""
    rendered = SHIP30_HTML_TEMPLATE.format(
        title="Test Title",
        word_count=1250,
        body_html="<p>Test content</p>",
        citations_html="<div>Citation</div>"
    )
    assert "<!DOCTYPE html>" in rendered
    assert "Test Title" in rendered
    assert "parent." not in rendered
    assert "window.top" not in rendered
    assert "localStorage" not in rendered
