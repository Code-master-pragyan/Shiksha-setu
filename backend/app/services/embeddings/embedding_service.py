from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.models.knowledge import KnowledgeChunk
from app.services.embeddings.embedding_provider import EmbeddingProvider

class EmbeddingService:
    def __init__(self, provider: EmbeddingProvider):
        self.provider = provider

    def ensure_schema(self, db: Session):
        """Ensure pgvector extension is enabled and table is created."""
        db.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        db.commit()
        # Create all tables if they don't exist
        from app.db.database import engine, Base
        import app.db.models.knowledge  # ensure model is registered
        Base.metadata.create_all(bind=engine)

    def process_chunk(self, db: Session, chunk_data: Dict[str, Any]) -> str:
        """
        Embed a chunk and upsert it into the database.
        Returns: 'inserted', 'updated', or 'skipped' (if identical).
        For now, since we use idempotent insert based on chunk_id,
        we can check if it exists first or use postgres ON CONFLICT.
        """
        chunk_id = chunk_data.get("chunk_id")
        existing = db.query(KnowledgeChunk).filter(KnowledgeChunk.chunk_id == chunk_id).first()
        
        # If it exists, we assume we can skip to save API calls
        if existing:
            return 'skipped'

        # Generate embedding
        text_content = chunk_data.get("text", "")
        if not text_content:
            raise ValueError(f"Chunk {chunk_id} has no text")
            
        embedding = self.provider.embed_text(text_content)

        new_chunk = KnowledgeChunk(
            chunk_id=chunk_id,
            document_id=chunk_data.get("document_id"),
            source_file=chunk_data.get("source_file"),
            title=chunk_data.get("title"),
            chapter_number=chunk_data.get("chapter_number"),
            chapter=chunk_data.get("chapter"),
            section=chunk_data.get("section"),
            page_start=chunk_data.get("page_start"),
            page_end=chunk_data.get("page_end"),
            subject=chunk_data.get("subject"),
            grade=chunk_data.get("grade"),
            language=chunk_data.get("language"),
            text=text_content,
            embedding=embedding
        )
        db.add(new_chunk)
        db.commit()
        return 'inserted'
