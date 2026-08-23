from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from app.db.database import Base

class Question(Base):
    __tablename__ = "questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    concept_id = Column(UUID(as_uuid=True), ForeignKey("concepts.id"), nullable=False, index=True)
    source_id = Column(UUID(as_uuid=True), ForeignKey("sources.id"), nullable=True)
    question_text = Column(Text, nullable=False)
    difficulty = Column(String, nullable=True)
    question_type = Column(String, nullable=True)
    options = Column(JSONB, nullable=True)
    correct_answer = Column(Text, nullable=False)
    explanation = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    concept = relationship("Concept", back_populates="questions")
    source = relationship("Source", back_populates="questions")
    attempts = relationship("Attempt", back_populates="question")
