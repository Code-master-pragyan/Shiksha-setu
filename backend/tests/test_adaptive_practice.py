import pytest
from unittest.mock import MagicMock
from app.services.mastery import MasteryService
from app.api.schemas.practice import PracticeAttemptRequest

class FakeQuestion:
    def __init__(self, id, concept_id, q_type, ans, expl=None):
        self.id = id
        self.concept_id = concept_id
        self.question_type = q_type
        self.correct_answer = ans
        self.explanation = expl

class FakeMastery:
    def __init__(self, score, cons_err):
        self.mastery_score = score
        self.consecutive_errors = cons_err
        self.attempts = 2
        self.correct_attempts = 1

def test_mastery_correct_increment():
    db = MagicMock()
    fake_q = FakeQuestion("q1", "c1", "multiple_choice", "A", "A is correct")
    fake_m = FakeMastery(0.50, 1)
    
    def side_effect(*args, **kwargs):
        if "questions" in str(args[0]).lower():
            return fake_q
        return fake_m
    db.scalar.side_effect = side_effect
    
    context_service = MagicMock()
    context_service.derive_learning_level.return_value = "intermediate"
    
    service = MasteryService(context_service=context_service, ai_provider=MagicMock())
    req = PracticeAttemptRequest(student_id="s1", question_id="q1", student_answer="A")
    
    res = service.record_attempt(db, req, [])
    
    assert res.correct is True
    assert res.mastery_score == 0.60
    assert fake_m.consecutive_errors == 0
    assert fake_m.correct_attempts == 2
    assert fake_m.attempts == 3

def test_mastery_incorrect_decrement():
    db = MagicMock()
    fake_q = FakeQuestion("q1", "c1", "multiple_choice", "A", None)
    fake_m = FakeMastery(0.50, 1)
    
    def side_effect(*args, **kwargs):
        if "questions" in str(args[0]).lower():
            return fake_q
        return fake_m
    db.scalar.side_effect = side_effect
    
    context_service = MagicMock()
    context_service.derive_learning_level.return_value = "intermediate"
    
    service = MasteryService(context_service=context_service, ai_provider=MagicMock())
    req = PracticeAttemptRequest(student_id="s1", question_id="q1", student_answer="B")
    
    res = service.record_attempt(db, req, [])
    
    assert res.correct is False
    assert res.mastery_score == 0.42
    assert fake_m.consecutive_errors == 2
    assert res.next_action == "review"
    assert res.next_difficulty == "beginner"

def test_mastery_clamping():
    db = MagicMock()
    fake_q = FakeQuestion("q1", "c1", "multiple_choice", "A", "Wrong.")
    fake_m = FakeMastery(0.05, 0)
    
    def side_effect(*args, **kwargs):
        if "questions" in str(args[0]).lower():
            return fake_q
        return fake_m
    db.scalar.side_effect = side_effect
    
    context_service = MagicMock()
    context_service.derive_learning_level.return_value = "beginner"
    
    service = MasteryService(context_service=context_service, ai_provider=MagicMock())
    req = PracticeAttemptRequest(student_id="s1", question_id="q1", student_answer="B")
    
    res = service.record_attempt(db, req, [])
    
    assert res.mastery_score == 0.0 # Clamped

    fake_m.mastery_score = 0.95
    req = PracticeAttemptRequest(student_id="s1", question_id="q1", student_answer="A")
    res = service.record_attempt(db, req, [])
    
    assert res.mastery_score == 1.0 # Clamped
