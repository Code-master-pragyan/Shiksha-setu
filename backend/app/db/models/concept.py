from sqlalchemy import Column, Integer, String, Text, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from app.db.database import Base

class Concept(Base):
    __tablename__ = "concepts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subject = Column(String, nullable=False, index=True)
    grade = Column(Integer, nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    difficulty = Column(String, nullable=True) # beginner, intermediate, advanced
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint('subject', 'grade', 'name', name='uq_concept_subject_grade_name'),
    )

    questions = relationship("Question", back_populates="concept")
    attempts = relationship("Attempt", back_populates="concept")
    mastery_records = relationship("StudentMastery", back_populates="concept")
