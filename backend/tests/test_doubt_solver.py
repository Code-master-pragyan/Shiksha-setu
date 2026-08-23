import pytest
from unittest.mock import MagicMock
from app.ai.doubt_solver import DoubtSolverService
from app.api.schemas.doubt import DoubtRequest
from app.api.schemas.retrieval import RetrievalResult
from app.ai.schemas import DoubtAnswer

def test_empty_retrieval_insufficient_context():
    retrieval_service = MagicMock()
    retrieval_service.search.return_value = []
    
    ai_provider = MagicMock()
    
    context_service = MagicMock()
    context_service.get_context.return_value = MagicMock(learning_level="beginner", grade=8)
    
    solver = DoubtSolverService(retrieval_service=retrieval_service, ai_provider=ai_provider, context_service=context_service)
    
    req = DoubtRequest(
        question="What is the capital of Brazil?",
        grade=8,
        subject="Science",
        preferred_language="English",
        top_k=3
    )
    
    db = MagicMock()
    response = solver.solve(db, req)
    
    assert "couldn't find enough information" in response.answer
    assert response.confidence == "low"
    assert len(response.citations) == 0
    ai_provider.generate_grounded_answer.assert_not_called()

def test_successful_doubt_solving():
    retrieval_service = MagicMock()
    chunk = RetrievalResult(
        chunk_id="c1", text="Yeast reproduces rapidly and produces carbon dioxide.",
        title="Microbes", chapter_number=2, chapter="Microbes", section="Yeast",
        page_start=15, page_end=16, subject="Science", grade=8, language="English", similarity_score=0.8
    )
    retrieval_service.search.return_value = [chunk]
    
    ai_provider = MagicMock()
    ai_provider.generate_grounded_answer.return_value = DoubtAnswer(
        answer="Yeast produces carbon dioxide, which makes dough rise.",
        key_points=["Yeast reproduces rapidly.", "Carbon dioxide gas is produced."],
        confidence="high",
        citations=[], # Gemini's citations should be ignored
        follow_up_question="Do you know what fermentation is?"
    )
    
    context_service = MagicMock()
    context_service.get_context.return_value = MagicMock(learning_level="beginner", grade=8)
    
    solver = DoubtSolverService(retrieval_service=retrieval_service, ai_provider=ai_provider, context_service=context_service)
    
    req = DoubtRequest(
        question="Why does yeast make dough rise?",
        grade=8,
        subject="Science",
        preferred_language="English",
        top_k=3
    )
    
    db = MagicMock()
    response = solver.solve(db, req)
    
    assert "carbon dioxide" in response.answer
    assert response.confidence == "high"
    assert len(response.citations) == 1
    assert response.citations[0].source_title == "Microbes"
    assert response.citations[0].page_start == 15
