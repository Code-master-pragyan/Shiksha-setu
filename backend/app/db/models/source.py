from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from app.db.database import Base

class Source(Base):
    __tablename__ = "sources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    publisher = Column(String, nullable=True)
    chapter = Column(String, nullable=True)
    section = Column(String, nullable=True)
    page = Column(Integer, nullable=True)
    url = Column(String, nullable=True)
    language = Column(String, nullable=False, default="English")
    source_type = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    questions = relationship("Question", back_populates="source")
