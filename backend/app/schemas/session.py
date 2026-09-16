from datetime import datetime
from uuid import UUID
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class CitationItem(BaseModel):
    episode_id: Optional[str] = None
    episode_title: str
    guest_name: str
    chapter_title: Optional[str] = None
    timestamp: Optional[str] = None
    quote: str
    similarity_score: Optional[float] = None

class MessageBase(BaseModel):
    role: str
    content: str
    message_type: str = "chat"

class MessageCreate(MessageBase):
    pass

class MessageResponse(MessageBase):
    id: UUID
    session_id: UUID
    citations: List[Dict[str, Any]] = []
    created_at: datetime

    class Config:
        from_attributes = True

class SessionCreate(BaseModel):
    title: Optional[str] = "New Conversation"
    active_provider: Optional[str] = "ollama"
    active_model: Optional[str] = "llama3.1"
    user_preferences: Optional[Dict[str, Any]] = None

class SessionUpdate(BaseModel):
    title: Optional[str] = None
    active_provider: Optional[str] = None
    active_model: Optional[str] = None
    user_preferences: Optional[Dict[str, Any]] = None

class SessionResponse(BaseModel):
    id: UUID
    title: str
    active_provider: str
    active_model: str
    user_preferences: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime
    message_count: Optional[int] = 0

    class Config:
        from_attributes = True
