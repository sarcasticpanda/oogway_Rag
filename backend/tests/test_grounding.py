import pytest
from app.rag.prompts import build_rag_messages, extract_follow_up_questions

def test_grounded_prompt_construction():
    """Verify prompt adapts when evidence is grounded vs ungrounded."""
    grounded_msgs = build_rag_messages(
        query="What is retention?",
        context="Source: Brian Balfour on Retention loops.",
        history=[],
        is_grounded=True
    )
    user_content = grounded_msgs[-1]["content"]
    assert "based strictly on the provided context evidence above" in user_content
    assert "Source: Brian Balfour" in user_content

    ungrounded_msgs = build_rag_messages(
        query="What is the capital of Mars?",
        context="",
        history=[],
        is_grounded=False
    )
    un_system_content = ungrounded_msgs[0]["content"]
    un_user_content = ungrounded_msgs[-1]["content"]
    assert "LOW-CONFIDENCE / UNGROUNDED NOTICE" in un_system_content
    assert "explicitly state that Lenny's podcast archive does not contain evidence" in un_user_content

def test_extract_follow_up_questions():
    """Verify extraction of follow-up questions from model response."""
    raw_response = """To improve user retention, focus on setup moments.
As Casey Winters explains, the first mile of product experience dictates long-term retention.

Follow-up Questions:
1. How does Casey Winters differentiate between activation and retention?
2. What are the best metrics to measure churn?
3. How do consumer vs B2B retention curves differ?
"""
    cleaned, follow_ups = extract_follow_up_questions(raw_response)
    assert "To improve user retention" in cleaned
    assert len(follow_ups) == 3
    assert "Casey Winters differentiate" in follow_ups[0]
    assert "measure churn" in follow_ups[1]
