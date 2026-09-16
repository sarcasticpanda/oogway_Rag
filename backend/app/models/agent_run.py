import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db import Base

class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    task_type = Column(String(64), nullable=False)  # "qa", "ship30", "artifact"
    provider = Column(String(64), nullable=False)
    model_name = Column(String(128), nullable=False)
    retrieval_latency_ms = Column(Float, default=0.0)
    generation_latency_ms = Column(Float, default=0.0)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    status = Column(String(32), default="success")  # "success", "error", "refused"
    error_details = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="agent_runs")
