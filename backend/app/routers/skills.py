from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db import get_db
from app.models.session import Session
from app.models.artifact import Artifact
from app.models.agent_run import AgentRun
from app.schemas.chat import Ship30Request
from app.skills.ship30 import generate_ship30_essay

router = APIRouter(prefix="/skills", tags=["skills"])

@router.post("/ship30")
async def create_ship30_essay(req: Ship30Request, db: AsyncSession = Depends(get_db)):
    """
    Dedicated Ship 30 for 30 Skill endpoint:
    1. Retrieves relevant Lenny podcast evidence.
    2. Writes atomic essay targeting ~1,250 words with Ship 30 formatting.
    3. Persists both Markdown and isolated HTML artifacts in database.
    4. Records execution in agent_runs table for observability.
    """
    # 1. Resolve or create session
    session = None
    if req.session_id:
        res = await db.execute(select(Session).where(Session.id == req.session_id))
        session = res.scalar_one_or_none()

    if not session:
        session = Session(
            title=f"Ship30: {req.topic[:35]}",
            active_provider=req.provider or "ollama",
            active_model=req.model or "llama3.1"
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)

    provider_name = req.provider or session.active_provider
    model_name = req.model or session.active_model

    # 2. Record agent run
    agent_run = AgentRun(
        session_id=session.id,
        task_type="ship30_essay",
        provider=provider_name,
        model_name=model_name,
        status="running"
    )
    db.add(agent_run)
    await db.commit()
    await db.refresh(agent_run)

    # 3. Generate essay
    try:
        md_content, html_content, word_count, citations, title = await generate_ship30_essay(
            topic=req.topic,
            db=db,
            provider=provider_name,
            model=model_name,
            api_key=req.api_key,
            base_url=req.base_url,
        )
        agent_run.status = "completed"
    except Exception as e:
        agent_run.status = "failed"
        agent_run.error_message = str(e)
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate Ship 30 essay: {str(e)}"
        )

    # 4. Save both Markdown and HTML artifacts
    citations_dicts = [c.model_dump() for c in citations]

    md_artifact = Artifact(
        session_id=session.id,
        title=f"{title} (Markdown)",
        artifact_type="markdown",
        content=md_content,
        word_count=word_count,
        source_references=citations_dicts
    )
    db.add(md_artifact)

    html_artifact = Artifact(
        session_id=session.id,
        title=f"{title} (HTML Visual)",
        artifact_type="html",
        content=html_content,
        word_count=word_count,
        source_references=citations_dicts
    )
    db.add(html_artifact)

    session.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(md_artifact)
    await db.refresh(html_artifact)

    return {
        "session_id": str(session.id),
        "title": title,
        "word_count": word_count,
        "markdown_artifact_id": str(md_artifact.id),
        "html_artifact_id": str(html_artifact.id),
        "citations": citations_dicts,
        "content_preview": md_content[:500] + "..."
    }
