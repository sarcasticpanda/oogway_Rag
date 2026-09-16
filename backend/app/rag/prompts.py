from typing import List, Dict, Tuple

GROUNDED_SYSTEM_PROMPT = """You are "The Lenny Growth Assistant", an elite AI advisor specialized in product management, startup growth, user retention, pricing, and company building.

Your knowledge is strictly derived from Lenny Rachitsky's podcast interviews with world-class product leaders, growth practitioners, and founders.

CRITICAL OPERATIONAL RULES:
1. STRICT GROUNDING: Answer questions ONLY using the provided transcript context snippets below. Do not fabricate, assume, or synthesize facts not present in the evidence.
2. CITATIONS: Every factual assertion, quote, or specific framework must cite the source using the format [Guest Name, "Episode Title", Chapter/Timestamp if available].
3. UNKNOWN / UNSUPPORTED QUERIES: If the provided transcript context does not contain sufficient information to answer the question, you MUST explicitly acknowledge this. Say:
   "Based on Lenny's podcast archive, this specific topic is not covered in the available transcripts. Rather than speculating, I recommend..."
   Do NOT attempt to guess or answer with generic internet knowledge when context is missing.
4. TONE & STRUCTURE: Be concise, analytical, and highly actionable. Use headers, bullet points, and bold emphasis for key takeaways.
"""

LOW_GROUNDING_WARNING = """
[LOW-CONFIDENCE / UNGROUNDED NOTICE]
The retrieved context below may NOT contain sufficient direct evidence to reliably answer the question.
If the evidence does not clearly support the answer, explicitly acknowledge that Lenny's podcast does not contain direct evidence on this topic instead of hallucinating.
"""

def build_rag_messages(
    query: str,
    context: str,
    history: List[Dict[str, str]] | None = None,
    is_grounded: bool = True,
    user_preferences: Dict[str, str] | None = None,
) -> List[Dict[str, str]]:
    """Constructs prompt message list with system grounding, conversation history, and user query."""
    messages = []
    
    # 1. System grounding instructions
    system_msg = GROUNDED_SYSTEM_PROMPT
    if not is_grounded:
        system_msg += "\n" + LOW_GROUNDING_WARNING
    if user_preferences:
        style = user_preferences.get("response_style")
        if style:
            system_msg += f"\nUSER RESPONSE PREFERENCE: {style}"
        instructions = user_preferences.get("instructions")
        if instructions:
            system_msg += f"\nUSER RESPONSE INSTRUCTIONS: {instructions}"

    messages.append({"role": "system", "content": system_msg})

    # 2. Add history (up to last 6 turns)
    if history:
        for turn in history[-6:]:
            messages.append({"role": turn["role"], "content": turn["content"]})

    # 3. Add user prompt with context blocks
    user_prompt = ""
    if context:
        user_prompt += f"CONTEXT EVIDENCE FROM LENNY'S PODCAST ARCHIVE:\n{context}\n\n"
    else:
        user_prompt += "NO DIRECT EVIDENCE RETRIEVED FROM LENNY'S PODCAST ARCHIVE.\n\n"

    if is_grounded:
        user_prompt += (
            f"USER QUESTION: {query}\n\n"
            f"Please answer based strictly on the provided context evidence above, including explicit guest attribution. "
            f"At the very end of your response, provide 2 or 3 suggested follow-up questions under the exact header 'Follow-up Questions:'."
        )
    else:
        user_prompt += (
            f"USER QUESTION: {query}\n\n"
            f"Note: If this question is outside the scope of Lenny's podcast or the retrieved evidence is empty/insufficient, "
            f"explicitly state that Lenny's podcast archive does not contain evidence for this. "
            f"At the very end of your response, provide 2 or 3 suggested follow-up questions under the exact header 'Follow-up Questions:'."
        )

    messages.append({"role": "user", "content": user_prompt})
    return messages

def extract_follow_up_questions(response_text: str) -> Tuple[str, List[str]]:
    """Splits the main response from the generated follow-up questions."""
    header_variants = ["Follow-up Questions:", "Follow-up questions:", "Suggested Follow-ups:"]
    found_idx = -1
    matched_header = ""

    for h in header_variants:
        idx = response_text.rfind(h)
        if idx != -1:
            found_idx = idx
            matched_header = h
            break

    if found_idx == -1:
        return response_text.strip(), [
            "What frameworks from other guests relate to this?",
            "Can you dive deeper into real-world examples mentioned?",
            "How do top startups put this into practice?"
        ]

    cleaned_answer = response_text[:found_idx].strip()
    follow_up_section = response_text[found_idx + len(matched_header):].strip()

    questions = []
    for line in follow_up_section.split("\n"):
        line = line.strip()
        if not line:
            continue
        # Remove numbers like "1.", "2)", "-", "*"
        cleaned_q = line.lstrip("0123456789.-*• \t")
        if cleaned_q and len(cleaned_q) > 5:
            questions.append(cleaned_q)

    if not questions:
        questions = [
            "What frameworks from other guests relate to this?",
            "Can you dive deeper into real-world examples mentioned?"
        ]

    return cleaned_answer, questions[:3]

def get_artifact_instructions() -> str:
    return """The user requested an artifact. Generate either a structured Markdown document or an HTML/CSS document according to the request.
    Wrap the complete artifact in typed tags: <artifact type="markdown" title="...">...</artifact> or <artifact type="html" title="...">...</artifact>.
    Do not place raw artifact markup in the conversational response."""
