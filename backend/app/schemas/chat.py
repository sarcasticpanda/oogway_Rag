from uuid import UUID
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class ChatRequest(BaseModel):
    session_id: Optional[UUID] = None
    message: str
    provider: Optional[str] = None
    model: Optional[str] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    task_type: Optional[str] = "qa"  # "qa", "ship30", "artifact"
    user_preferences: Optional[Dict[str, Any]] = None

class Ship30Request(BaseModel):
    session_id: Optional[UUID] = None
    topic: str
    provider: Optional[str] = None
    model: Optional[str] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None

class ArtifactResponse(BaseModel):
    id: UUID
    session_id: UUID
    title: str
    artifact_type: str
    content: str
    word_count: int
    source_references: List[Dict[str, Any]] = []
    created_at: str

    class Config:
        from_attributes = True

class ModelInfoResponse(BaseModel):
    active_provider: str
    active_model: str
    available_providers: List[str]
    ollama_status: str
    ollama_models: List[str]
    cloud_providers: List[Dict[str, Any]]
