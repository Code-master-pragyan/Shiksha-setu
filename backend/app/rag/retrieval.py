import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.models.knowledge import KnowledgeChunk
from app.services.embeddings.embedding_provider import EmbeddingProvider
from app.api.schemas.retrieval import RetrievalResult

logger = logging.getLogger(__name__)

class RetrievalService:
    def __init__(self, provider: EmbeddingProvider):
        self.provider = provider

    def search(
        self, 
        db: Session, 
        query: str, 
        grade: Optional[int] = None,
        subject: Optional[str] = None,
        language: Optional[str] = None,
        chapter: Optional[str] = None,
        top_k: int = 5
    ) -> List[RetrievalResult]:
        """
        Embed the query and retrieve top K chunks from PostgreSQL via pgvector.
        """
        logger.info(f"Generating embedding for query: '{query}'")
        try:
            query_embedding = self.provider.embed_text(query)
        except Exception as e:
            logger.error(f"Failed to generate query embedding: {e}")
            raise RuntimeError("Could not generate query embedding") from e
            
        expected_dim = self.provider.dimension
        if len(query_embedding) != expected_dim:
            logger.error(f"Dimension mismatch: expected {expected_dim}, got {len(query_embedding)}")
            raise ValueError("Query embedding dimension mismatch")

        # Base query using cosine distance
        stmt = select(
            KnowledgeChunk, 
            KnowledgeChunk.embedding.cosine_distance(query_embedding).label("distance")
        )
        
        # Apply filters
        if grade is not None:
            stmt = stmt.filter(KnowledgeChunk.grade == grade)
        if subject is not None:
            stmt = stmt.filter(KnowledgeChunk.subject == subject)
        if language is not None:
            stmt = stmt.filter(KnowledgeChunk.language == language)
        if chapter is not None:
            stmt = stmt.filter(KnowledgeChunk.chapter == chapter)
            
        # Order by distance (smaller is more similar for cosine distance)
        stmt = stmt.order_by("distance").limit(top_k)
        
        results = []
        try:
            rows = db.execute(stmt).all()
        except Exception as e:
            logger.error(f"Database query failed: {e}")
            raise RuntimeError("Database similarity search failed") from e
            
        for chunk, distance in rows:
            # Cosine similarity is typically 1 - cosine distance
            # Pgvector cosine distance is between 0 and 2. 0 = exact match.
            similarity = 1.0 - distance
            
            result = RetrievalResult(
                chunk_id=chunk.chunk_id,
                text=chunk.text,
                title=chunk.title,
                chapter_number=chunk.chapter_number,
                chapter=chunk.chapter,
                section=chunk.section,
                page_start=chunk.page_start,
                page_end=chunk.page_end,
                subject=chunk.subject,
                grade=chunk.grade,
                language=chunk.language,
                similarity_score=round(similarity, 4)
            )
            results.append(result)
            
        return results
