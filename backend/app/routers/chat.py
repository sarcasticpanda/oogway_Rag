import json
import asyncio
import re
from html import escape
from uuid import UUID
from datetime import datetime
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db import get_db
from app.models.session import Session
from app.models.message import Message
from app.models.episode import Episode
from app.schemas.chat import ChatRequest
from app.rag.retrieve import retrieve_context
from app.rag.prompts import build_rag_messages, extract_follow_up_questions, get_artifact_instructions
from app.rag.artifacts import extract_artifact_from_response, should_generate_artifact, get_artifact_prompt_instructions
from app.ai.factory import AIProviderFactory
from app.config import settings
from app.models.artifact import Artifact

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("")
async def chat_endpoint(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    """
    Standard (non-streaming) chat endpoint:
    1. Validates or creates session.
    2. Retrieves top-k relevant podcast transcript chunks via pgvector.
    3. Evaluates grounding and adds explicit caveat if unsupported.
    4. Calls configured provider (Ollama / Claude / OpenAI).
    5. Persists user & assistant messages with citations in PostgreSQL.
    6. Returns answer, citations, and dynamic follow-up questions.
    """
    # 1. Resolve session
    session = None
    if request.session_id:
        res = await db.execute(select(Session).where(Session.id == request.session_id))
        session = res.scalar_one_or_none()

    if not session:
        session = Session(
            title=request.message[:40] + ("..." if len(request.message) > 40 else ""),
            active_provider=request.provider or "ollama",
            active_model=request.model or "llama3.1"
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)

    # 2. Retrieve history
    msg_res = await db.execute(
        select(Message).where(Message.session_id == session.id).order_by(Message.created_at).limit(10)
    )
    history_rows = msg_res.scalars().all()
    history = [{"role": m.role, "content": m.content} for m in history_rows]

    # 3. Retrieve evidence. Artifacts need a wider source-scoped evidence set
    # than ordinary Q&A so the model can synthesize the selected document.
    is_artifact_request = should_generate_artifact(request.message) or request.task_type == "artifact"
    retrieval_query = request.message
    if request.source_scope == "chat":
        retrieval_query = "\n".join(turn["content"] for turn in history[-8:] if turn["role"] in {"user", "assistant"})
        retrieval_query = f"{retrieval_query}\n{request.message}".strip()
    context_str, citations, is_grounded = await retrieve_context(
        retrieval_query,
        db,
        top_k=12 if is_artifact_request else 6,
        source_ids=request.source_ids if request.source_scope == "selected" else None,
    )

    # 4. Build prompt
    prompt_messages = build_rag_messages(
        query=request.message,
        context=context_str,
        history=history,
        is_grounded=is_grounded,
        user_preferences=request.user_preferences,
    )
    
    if is_artifact_request:
        kind_match = re.search(r"@(ship30|artifact)\s*(ship30|summary|report|checklist|html)?", request.message.lower())
        task_type = "ship30" if "@ship30" in request.message.lower() else (kind_match.group(2) if kind_match and kind_match.group(2) else "general")
        subtype_match = re.search(r"(?:html|markdown)\s*:\s*(essay|summary|report|checklist)", request.message.lower())
        requested_deliverable = subtype_match.group(1) if subtype_match else task_type
        selected_titles = []
        if request.source_scope == "selected" and request.source_ids:
            selected_result = await db.execute(select(Episode.title).where(Episode.id.in_(request.source_ids)))
            selected_titles = [row[0] for row in selected_result.all()]
        source_scope = ", ".join(selected_titles) if selected_titles else ("the current conversation" if request.source_scope == "chat" else "all retrieved knowledge sources")
        prompt_messages.append({"role": "system", "content": get_artifact_prompt_instructions(task_type) + f"\nREFERENCE MODE: {request.source_scope}.\nSOURCE SCOPE: Use only {source_scope}.\nREQUESTED DELIVERABLE: {requested_deliverable}.\nUSER REQUEST: {request.message}\nTransform the evidence into the requested deliverable; do not merely paste or paraphrase isolated chunks. For a JD, extract only requirements actually present and label recommendations as recommendations. Do not invent technologies, names, timelines, or requirements. Every substantive claim must be traceable to the supplied evidence."})

    # 5. Execute LLM completion
    provider_name = request.provider or session.active_provider
    model_name = request.model or session.active_model

    # Sanity check: if the stored model is a known-decommissioned/stale value,
    # fall back to the provider's current default so old sessions still work.
    STALE_MODELS = {"llama3.1", "llama3-70b-8192", "llama3-8b", "mistral"}
    if model_name in STALE_MODELS:
        model_name = None
        if session.active_model in STALE_MODELS:
            session.active_model = settings.DEFAULT_MODEL

    chat_provider = AIProviderFactory.get_chat_provider(
        provider=provider_name,
        model=model_name,
        api_key=request.api_key,
        base_url=request.base_url,
    )
    # Resolve the model actually used (provider defaults apply when None)
    resolved_model = getattr(chat_provider, "model", None) or model_name

    # Try the requested provider, with fallback to Ollama if available
    raw_response = None
    providers_to_try = [provider_name]
    if provider_name.lower() != "ollama":
        providers_to_try.append("ollama")
    
    last_error = None
    for try_provider in providers_to_try:
        try:
            fp = AIProviderFactory.get_chat_provider(
                provider=try_provider,
                model=model_name,
                api_key=request.api_key,
                base_url=request.base_url,
            )
            raw_response = await fp.complete(prompt_messages)
            # Update final provider if we fell back
            if try_provider != provider_name:
                provider_name = try_provider
            break
        except Exception as e:
            last_error = e
            continue
    
    if raw_response is None:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI provider unavailable. Tried: {', '.join(providers_to_try)}. Last error: {last_error}"
        )

    # 6. Extract artifact if present
    cleaned_response, artifact_data = extract_artifact_from_response(raw_response)
    if is_artifact_request and not raw_response.strip():
        source_lines = [
            f"- **{citation.guest_name}**: {citation.quote}"
            for citation in citations
        ]
        fallback_content = "# Grounded Report\n\n## Retrieved Evidence\n\n"
        fallback_content += "\n".join(source_lines) if source_lines else "No matching source evidence was retrieved."
        artifact_data = {
            "type": "markdown",
            "title": "Grounded report from this chat",
            "content": fallback_content,
        }
        cleaned_response = "Created a grounded report from the retrieved evidence. Open it in the artifact panel."
    if is_artifact_request and artifact_data is None:
        # Some providers ignore wrapper instructions. Preserve the requested output
        # as an artifact instead of leaking raw markup into the conversation.
        fallback_type = task_type if task_type in {"html", "summary", "report", "checklist", "ship30"} else "markdown"
        if fallback_type == "html":
            fallback_content = (
                "<!doctype html><html><head><meta charset=\"utf-8\"><style>"
                "body{font-family:system-ui;max-width:760px;margin:40px auto;padding:0 20px;line-height:1.6}"
                "</style></head><body><article><pre style=\"white-space:pre-wrap;font:inherit\">"
                f"{escape(raw_response)}"
                "</pre></article></body></html>"
            )
        else:
            fallback_content = raw_response.strip()
        artifact_data = {
            "type": "html" if fallback_type == "html" else "markdown",
            "title": f"{fallback_type.title()} from this chat",
            "content": fallback_content,
        }
        cleaned_response = f"Created {artifact_data['title']}. Open it in the artifact panel."
    
    # 7. Parse follow-ups
    final_response, follow_ups = extract_follow_up_questions(cleaned_response)
    if is_artifact_request and not final_response.strip():
        final_response = f"Created {artifact_data['title']}. Open it from the artifact button below."

    # 8. Persist messages
    citations_data = [c.model_dump() for c in citations]
    user_msg = Message(
        session_id=session.id,
        role="user",
        content=request.message,
        message_type="chat"
    )
    db.add(user_msg)

    asst_msg = Message(
        session_id=session.id,
        role="assistant",
        content=final_response,
        message_type="artifact" if artifact_data else "chat",
        citations=citations_data
    )
    db.add(asst_msg)

    # 9. Save artifact if generated
    artifact_id = None
    if artifact_data:
        artifact = Artifact(
            session_id=session.id,
            title=artifact_data["title"],
            artifact_type=artifact_data["type"],
            content=artifact_data["content"],
            word_count=len(artifact_data["content"].split()),
            source_references=citations_data
        )
        db.add(artifact)
        await db.flush()
        artifact_id = str(artifact.id)

    session.updated_at = datetime.utcnow()
    await db.commit()

    return {
        "session_id": str(session.id),
        "message": final_response,
        "is_grounded": is_grounded,
        "citations": citations_data,
        "follow_ups": follow_ups,
        "provider": provider_name,
        "model": resolved_model,
        "artifact_id": artifact_id,
        "artifact_data": artifact_data
    }

@router.post("/stream")
async def chat_stream_endpoint(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    """
    Server-Sent Events (SSE) streaming chat endpoint.
    Emits initial metadata & citations, then streams tokens, then final follow-ups.
    """
    # 1. Resolve session
    session = None
    if request.session_id:
        res = await db.execute(select(Session).where(Session.id == request.session_id))
        session = res.scalar_one_or_none()

    if not session:
        session = Session(
            title=request.message[:40] + ("..." if len(request.message) > 40 else ""),
            active_provider=request.provider or settings.AI_PROVIDER,
            active_model=request.model or settings.DEFAULT_MODEL
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)

    # 2. Retrieve history
    msg_res = await db.execute(
        select(Message).where(Message.session_id == session.id).order_by(Message.created_at).limit(10)
    )
    history = [{"role": m.role, "content": m.content} for m in msg_res.scalars().all()]

    # 3. Retrieve context
    context_str, citations, is_grounded = await retrieve_context(request.message, db, top_k=6)
    citations_data = [c.model_dump() for c in citations]

    prompt_messages = build_rag_messages(
        query=request.message,
        context=context_str,
        history=history,
        is_grounded=is_grounded
    )
    if request.task_type == "artifact":
        prompt_messages.append({"role": "system", "content": get_artifact_instructions()})

    provider_name = request.provider or session.active_provider
    model_name = request.model or session.active_model
    chat_provider = AIProviderFactory.get_chat_provider(provider=provider_name, model=model_name)

    async def event_generator():
        # Step A: Send metadata & citations event
        initial_payload = {
            "session_id": str(session.id),
            "is_grounded": is_grounded,
            "citations": citations_data,
            "provider": provider_name,
            "model": model_name
        }
        yield f"event: metadata\ndata: {json.dumps(initial_payload)}\n\n"

        # Step B: Stream tokens from provider
        collected_tokens = []
        try:
            async for token in chat_provider.stream(prompt_messages):
                collected_tokens.append(token)
                yield f"event: delta\ndata: {json.dumps({'token': token})}\n\n"
        except Exception as e:
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
            return

        full_content = "".join(collected_tokens)
        cleaned_answer, follow_ups = extract_follow_up_questions(full_content)

        # Step C: Save messages to DB (in background session)
        try:
            user_msg = Message(
                session_id=session.id,
                role="user",
                content=request.message,
                message_type="chat"
            )
            db.add(user_msg)

            asst_msg = Message(
                session_id=session.id,
                role="assistant",
                content=cleaned_answer,
                message_type="chat",
                citations=citations_data
            )
            db.add(asst_msg)

            if request.task_type == "artifact" or "<artifact>" in cleaned_answer:
                from app.models.artifact import Artifact
                title = "Ship 30 Essay"
                content = cleaned_answer
                if "<artifact>" in cleaned_answer and "</artifact>" in cleaned_answer:
                    start = cleaned_answer.find("<artifact>") + 10
                    end = cleaned_answer.rfind("</artifact>")
                    content = cleaned_answer[start:end].strip()
                
                artifact = Artifact(
                    session_id=session.id,
                    title=title,
                    artifact_type="markdown",
                    content=content,
                    word_count=len(content.split())
                )
                db.add(artifact)

            session.updated_at = datetime.utcnow()
            await db.commit()
        except Exception as err:
            pass

        # Step D: Emit completion event with follow-up questions
        yield f"event: done\ndata: {json.dumps({'follow_ups': follow_ups})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
