import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db import Base

class Episode(Base):
    __tablename__ = "episodes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(512), nullable=False, index=True)
    guest_name = Column(String(256), nullable=False, index=True)
    publication_date = Column(String(64), nullable=True)
    episode_url = Column(String(1024), nullable=True)
    summary = Column(Text, nullable=True)
    key_frameworks = Column(JSON, default=list)
    expertise_tags = Column(JSON, default=list)
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    chunks = relationship("TranscriptChunk", back_populates="episode", cascade="all, delete-orphan")
