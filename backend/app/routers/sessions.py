from typing import List
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, delete

from app.db import get_db
from app.models.session import Session
from app.models.message import Message
from app.models.artifact import Artifact
from app.schemas.session import SessionCreate, SessionUpdate, SessionResponse, MessageResponse

router = APIRouter(prefix="/sessions", tags=["sessions"])

@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_sessions(db: AsyncSession = Depends(get_db)):
    """Delete every chat session and its persisted messages/artifacts."""
    await db.execute(delete(Session))
    await db.commit()
    return None

@router.get("", response_model=List[SessionResponse])
async def list_sessions(db: AsyncSession = Depends(get_db)):
    """List all chat sessions ordered by last updated timestamp."""
    # Subquery to count messages per session
    msg_count_subq = (
        select(Message.session_id, func.count(Message.id).label("count"))
        .group_by(Message.session_id)
        .subquery()
    )

    stmt = (
        select(Session, func.coalesce(msg_count_subq.c.count, 0))
        .outerjoin(msg_count_subq, Session.id == msg_count_subq.c.session_id)
        .order_by(desc(Session.updated_at))
    )
    result = await db.execute(stmt)
    rows = result.all()

    sessions = []
    for sess, count in rows:
        resp = SessionResponse(
            id=sess.id,
            title=sess.title,
            active_provider=sess.active_provider,
            active_model=sess.active_model,
            user_preferences=sess.user_preferences or {},
            created_at=sess.created_at,
            updated_at=sess.updated_at,
            message_count=count
        )
        sessions.append(resp)
    return sessions

@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(sess_in: SessionCreate, db: AsyncSession = Depends(get_db)):
    """Create a new independent chat session."""
    session = Session(
        title=sess_in.title or "New Conversation",
        active_provider=sess_in.active_provider or "ollama",
        active_model=sess_in.active_model or "llama3.1",
        user_preferences=sess_in.user_preferences or {}
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return SessionResponse(
        id=session.id,
        title=session.title,
        active_provider=session.active_provider,
        active_model=session.active_model,
        user_preferences=session.user_preferences or {},
        created_at=session.created_at,
        updated_at=session.updated_at,
        message_count=0
    )

@router.get("/{session_id}")
async def get_session(session_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get single session with its message history and attached artifacts."""
    sess_res = await db.execute(select(Session).where(Session.id == session_id))
    session = sess_res.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    msg_res = await db.execute(
        select(Message).where(Message.session_id == session_id).order_by(Message.created_at)
    )
    messages = msg_res.scalars().all()

    art_res = await db.execute(
        select(Artifact).where(Artifact.session_id == session_id).order_by(desc(Artifact.created_at))
    )
    artifacts = art_res.scalars().all()

    return {
        "session": SessionResponse(
            id=session.id,
            title=session.title,
            active_provider=session.active_provider,
            active_model=session.active_model,
            user_preferences=session.user_preferences or {},
            created_at=session.created_at,
            updated_at=session.updated_at,
            message_count=len(messages)
        ),
        "messages": [
            {
                "id": str(m.id),
                "role": m.role,
                "content": m.content,
                "message_type": m.message_type,
                "citations": m.citations or [],
                "created_at": m.created_at.isoformat()
            }
            for m in messages
        ],
        "artifacts": [
            {
                "id": str(a.id),
                "title": a.title,
                "artifact_type": a.artifact_type,
                "word_count": a.word_count,
                "created_at": a.created_at.isoformat()
            }
            for a in artifacts
        ]
    }

@router.patch("/{session_id}", response_model=SessionResponse)
async def update_session(session_id: UUID, update_in: SessionUpdate, db: AsyncSession = Depends(get_db)):
    """Update session title or provider/model settings."""
    res = await db.execute(select(Session).where(Session.id == session_id))
    session = res.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if update_in.title is not None:
        session.title = update_in.title
    if update_in.active_provider is not None:
        session.active_provider = update_in.active_provider
    if update_in.active_model is not None:
        session.active_model = update_in.active_model
    if update_in.user_preferences is not None:
        session.user_preferences = update_in.user_preferences

    session.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(session)

    return SessionResponse(
        id=session.id,
        title=session.title,
        active_provider=session.active_provider,
        active_model=session.active_model,
        user_preferences=session.user_preferences or {},
        created_at=session.created_at,
        updated_at=session.updated_at,
        message_count=0
    )

@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(session_id: UUID, db: AsyncSession = Depends(get_db)):
    """Delete a session and cascade delete its messages and artifacts."""
    res = await db.execute(select(Session).where(Session.id == session_id))
    session = res.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    await db.delete(session)
    await db.commit()
    return None
