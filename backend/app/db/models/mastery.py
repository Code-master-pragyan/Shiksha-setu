from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from app.db.database import Base

class StudentMastery(Base):
    __tablename__ = "student_mastery"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("student_profiles.id"), nullable=False, index=True)
    concept_id = Column(UUID(as_uuid=True), ForeignKey("concepts.id"), nullable=False, index=True)
    mastery_score = Column(Float, default=0.0)
    attempts = Column(Integer, default=0)
    correct_attempts = Column(Integer, default=0)
    consecutive_errors = Column(Integer, default=0)
    last_attempt_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint('student_id', 'concept_id', name='uq_student_concept_mastery'),
    )

    student = relationship("StudentProfile", back_populates="mastery_records")
    concept = relationship("Concept", back_populates="mastery_records")
