import pytest
from unittest.mock import MagicMock
from app.services.teacher_insights import TeacherInsightService
from app.db.models.mastery import StudentMastery
from app.db.models.attempt import Attempt

def test_status_at_risk():
    service = TeacherInsightService()
    
    # 1. mastery < 0.30
    status, _, _ = service._determine_status(mastery_score=0.20, consecutive_errors=0, recent_accuracy=0.8, trend="stable")
    assert status == "at_risk"
    
    # 2. consecutive_errors >= 3
    status, _, _ = service._determine_status(mastery_score=0.60, consecutive_errors=3, recent_accuracy=0.8, trend="stable")
    assert status == "at_risk"

def test_status_needs_attention():
    service = TeacherInsightService()
    
    # 1. 0.30 <= mastery < 0.50
    status, _, _ = service._determine_status(mastery_score=0.40, consecutive_errors=1, recent_accuracy=0.8, trend="stable")
    assert status == "needs_attention"
    
    # 2. recent_accuracy < 0.50
    status, _, _ = service._determine_status(mastery_score=0.60, consecutive_errors=1, recent_accuracy=0.4, trend="stable")
    assert status == "needs_attention"

def test_status_improving():
    service = TeacherInsightService()
    
    status, _, _ = service._determine_status(mastery_score=0.60, consecutive_errors=0, recent_accuracy=0.8, trend="improving")
    assert status == "improving"

def test_status_on_track():
    service = TeacherInsightService()
    
    status, _, _ = service._determine_status(mastery_score=0.60, consecutive_errors=1, recent_accuracy=0.8, trend="stable")
    assert status == "on_track"

def test_calculate_metrics_empty():
    service = TeacherInsightService()
    acc, trend = service._calculate_metrics([])
    assert acc is None
    assert trend == "unknown"

def test_calculate_metrics_less_than_6():
    service = TeacherInsightService()
    
    # 4 attempts: 3 correct, 1 incorrect = 75%
    attempts = [
        MagicMock(correct=True), MagicMock(correct=True),
        MagicMock(correct=False), MagicMock(correct=True)
    ]
    
    acc, trend = service._calculate_metrics(attempts)
    assert acc == 0.75
    assert trend == "unknown"

def test_calculate_metrics_improving():
    service = TeacherInsightService()
    
    # 10 attempts
    # First 5: 1 correct (20%)
    # Last 5: 4 correct (80%)
    attempts = [MagicMock(correct=c) for c in [
        True, False, False, False, False, # Older
        True, True, True, True, False    # Recent
    ]]
    
    acc, trend = service._calculate_metrics(attempts)
    assert acc == 0.80
    assert trend == "improving"

def test_calculate_metrics_declining():
    service = TeacherInsightService()
    
    # 10 attempts
    # First 5: 4 correct (80%)
    # Last 5: 1 correct (20%)
    attempts = [MagicMock(correct=c) for c in [
        True, True, True, True, False,   # Older
        True, False, False, False, False # Recent
    ]]
    
    acc, trend = service._calculate_metrics(attempts)
    assert acc == 0.20
    assert trend == "declining"
