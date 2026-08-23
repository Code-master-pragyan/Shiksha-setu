from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime, timezone
from app.db.database import Base
from pgvector.sqlalchemy import Vector

class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chunk_id = Column(String, unique=True, nullable=False, index=True)
    document_id = Column(String, nullable=False)
    source_file = Column(String, nullable=False)
    title = Column(String, nullable=False)
    chapter_number = Column(Integer, nullable=True)
    chapter = Column(String, nullable=True)
    section = Column(String, nullable=True)
    page_start = Column(Integer, nullable=False)
    page_end = Column(Integer, nullable=False)
    subject = Column(String, nullable=False)
    grade = Column(Integer, nullable=False)
    language = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    embedding = Column(Vector(3072), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
