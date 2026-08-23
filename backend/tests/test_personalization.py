import pytest
from unittest.mock import MagicMock
from app.services.student_context import StudentContextService
from app.ai.prompt_builder import PromptBuilder

def test_mastery_classification():
    service = StudentContextService()
    
    assert service.derive_learning_level(0.0) == "beginner"
    assert service.derive_learning_level(0.39) == "beginner"
    assert service.derive_learning_level(0.40) == "intermediate"
    assert service.derive_learning_level(0.69) == "intermediate"
    assert service.derive_learning_level(0.70) == "advanced"
    assert service.derive_learning_level(1.0) == "advanced"

def test_student_context_service_missing_student():
    service = StudentContextService()
    db = MagicMock()
    
    context = service.get_context(db, student_id=None, concept_id=None, default_grade=8, default_language="English")
    
    assert context.grade == 8
    assert context.preferred_language == "English"
    assert context.learning_level == "beginner"
    assert context.mastery_status == "unknown"

def test_student_context_service_with_student_no_concept():
    service = StudentContextService()
    db = MagicMock()
    
    mock_student = MagicMock()
    mock_student.grade = 9
    mock_student.preferred_language = "Hindi"
    
    db.scalar.return_value = mock_student
    
    context = service.get_context(db, student_id="test_id", concept_id=None, default_grade=8, default_language="English")
    
    # It should override default grade and language using the student's profile
    assert context.grade == 9
    assert context.preferred_language == "Hindi"
    assert context.learning_level == "beginner"

def test_personalized_prompt_construction():
    service = StudentContextService()
    context = service.get_context(MagicMock(), student_id=None, concept_id=None, default_grade=8, default_language="Assamese")
    context.learning_level = "intermediate"
    
    prompt = PromptBuilder.build_prompt("What is X?", [], context)
    
    assert "Learning level: INTERMEDIATE" in prompt
    assert "Preferred language: Assamese" in prompt
    
    sys_inst = PromptBuilder.build_system_instruction(context, "Science")
    assert "written in Assamese" in sys_inst
    assert "Grade 8" in sys_inst
