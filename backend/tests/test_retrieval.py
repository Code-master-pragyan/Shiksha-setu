import pytest
from unittest.mock import MagicMock
from app.rag.retrieval import RetrievalService
from app.api.schemas.retrieval import RetrievalRequest
from pydantic import ValidationError

def test_query_validation():
    # Valid
    req = RetrievalRequest(query="What is a cell?")
    assert req.top_k == 5
    assert req.query == "What is a cell?"
    
    # Empty query
    with pytest.raises(ValidationError):
        RetrievalRequest(query="")
        
    # Invalid top_k
    with pytest.raises(ValidationError):
        RetrievalRequest(query="Test", top_k=0)
        
    with pytest.raises(ValidationError):
        RetrievalRequest(query="Test", top_k=21)

def test_vector_dimension_validation():
    # Setup mock provider returning wrong dimension
    provider = MagicMock()
    provider.dimension = 3072
    provider.embed_text.return_value = [0.1] * 768 # Wrong dimension
    
    service = RetrievalService(provider=provider)
    
    db = MagicMock()
    with pytest.raises(ValueError, match="Query embedding dimension mismatch"):
        service.search(db, query="Test query", top_k=5)

def test_retrieval_success():
    provider = MagicMock()
    provider.dimension = 3072
    provider.embed_text.return_value = [0.1] * 3072
    
    service = RetrievalService(provider=provider)
    
    # Mock DB rows
    db = MagicMock()
    
    chunk_mock = MagicMock()
    chunk_mock.chunk_id = "test_1"
    chunk_mock.text = "test text"
    chunk_mock.title = "test title"
    chunk_mock.chapter_number = 1
    chunk_mock.chapter = "test chap"
    chunk_mock.section = "test sec"
    chunk_mock.page_start = 1
    chunk_mock.page_end = 2
    chunk_mock.subject = "Science"
    chunk_mock.grade = 8
    chunk_mock.language = "English"
    
    # Rows return (KnowledgeChunk, distance)
    db.execute.return_value.all.return_value = [
        (chunk_mock, 0.1) # distance = 0.1 -> similarity = 0.9
    ]
    
    results = service.search(db, query="Test query", top_k=5)
    
    assert len(results) == 1
    assert results[0].chunk_id == "test_1"
    assert results[0].similarity_score == 0.9
    
def test_empty_results():
    provider = MagicMock()
    provider.dimension = 3072
    provider.embed_text.return_value = [0.1] * 3072
    
    service = RetrievalService(provider=provider)
    
    db = MagicMock()
    db.execute.return_value.all.return_value = []
    
    results = service.search(db, query="Test query", top_k=5)
    assert len(results) == 0
