import logging
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from app.db.models.student import StudentProfile
from app.db.models.concept import Concept
from app.db.models.mastery import StudentMastery
from app.db.models.attempt import Attempt
from app.api.schemas.teacher import TeacherInsight, TeacherSummaryResponse, StudentDetailResponse

logger = logging.getLogger(__name__)

class TeacherInsightService:

    def get_class_summary(
        self, 
        db: Session,
        grade: Optional[int] = None,
        subject: Optional[str] = None,
        concept_id: Optional[str] = None,
        status_filter: Optional[str] = None
    ) -> TeacherSummaryResponse:
        
        # We need all masteries, filtered as needed
        query = select(StudentMastery, StudentProfile, Concept).join(
            StudentProfile, StudentMastery.student_id == StudentProfile.id
        ).join(
            Concept, StudentMastery.concept_id == Concept.id
        )
        
        if grade is not None:
            query = query.where(StudentProfile.grade == grade)
        if subject is not None:
            query = query.where(Concept.subject == subject)
        if concept_id:
            query = query.where(Concept.id == concept_id)
            
        rows = db.execute(query).all()
        
        insights = []
        counts = {"at_risk": 0, "needs_attention": 0, "improving": 0, "on_track": 0}
        
        for mastery, student, concept in rows:
            insight = self._compute_insight(db, mastery, concept)
            
            if status_filter and insight.status != status_filter:
                continue
                
            insights.append(insight)
            if insight.status in counts:
                counts[insight.status] += 1
                
        # Total students in these insights (distinct student_ids)
        total_students = len(set(i.student_id for i in insights))
        
        return TeacherSummaryResponse(
            total_students=total_students,
            at_risk=counts["at_risk"],
            needs_attention=counts["needs_attention"],
            improving=counts["improving"],
            on_track=counts["on_track"],
            insights=insights
        )

    def get_student_detail(self, db: Session, student_id: str) -> StudentDetailResponse:
        student = db.scalar(select(StudentProfile).where(StudentProfile.id == student_id))
        if not student:
            raise ValueError("Student not found")
            
        query = select(StudentMastery, Concept).join(
            Concept, StudentMastery.concept_id == Concept.id
        ).where(StudentMastery.student_id == student_id)
        
        rows = db.execute(query).all()
        
        insights = []
        for mastery, concept in rows:
            insight = self._compute_insight(db, mastery, concept)
            insights.append(insight)
            
        return StudentDetailResponse(
            student_id=str(student.id),
            grade=student.grade,
            preferred_language=student.preferred_language or "English",
            insights=insights
        )

    def _compute_insight(self, db: Session, mastery: StudentMastery, concept: Concept) -> TeacherInsight:
        attempts_q = select(Attempt).where(
            Attempt.student_id == mastery.student_id,
            Attempt.concept_id == mastery.concept_id
        ).order_by(desc(Attempt.created_at)).limit(10)
        
        recent_10 = db.scalars(attempts_q).all()
        # reverse so they are chronological
        recent_10 = list(reversed(recent_10))
        
        recent_accuracy, trend = self._calculate_metrics(recent_10)
        status, reason, action = self._determine_status(
            mastery_score=mastery.mastery_score,
            consecutive_errors=mastery.consecutive_errors,
            recent_accuracy=recent_accuracy,
            trend=trend
        )
        
        return TeacherInsight(
            student_id=str(mastery.student_id),
            concept_id=str(mastery.concept_id),
            concept_name=concept.name,
            mastery_score=round(mastery.mastery_score, 2),
            recent_accuracy=round(recent_accuracy, 2) if recent_accuracy is not None else None,
            consecutive_errors=mastery.consecutive_errors,
            status=status,
            trend=trend,
            reason=reason,
            recommended_action=action
        )
        
    def _calculate_metrics(self, attempts: List[Attempt]) -> Tuple[Optional[float], str]:
        if not attempts:
            return None, "unknown"
            
        recent_5 = attempts[-5:]
        recent_acc = sum(1 for a in recent_5 if a.correct) / len(recent_5)
        
        if len(attempts) < 6:
            return recent_acc, "unknown"
            
        older_half = attempts[:-5]
        older_acc = sum(1 for a in older_half if a.correct) / len(older_half)
        
        if recent_acc > older_acc + 0.20:
            trend = "improving"
        elif recent_acc < older_acc - 0.20:
            trend = "declining"
        else:
            trend = "stable"
            
        return recent_acc, trend

    def _determine_status(self, mastery_score: float, consecutive_errors: int, recent_accuracy: Optional[float], trend: str) -> Tuple[str, str, str]:
        
        # 1. AT_RISK
        if mastery_score < 0.30 or consecutive_errors >= 3:
            reason = "Low mastery or frequent consecutive errors."
            if consecutive_errors >= 3:
                reason = "Three or more consecutive errors detected."
            action = "Provide concept review and beginner-level practice."
            return "at_risk", reason, action
            
        # 2. NEEDS_ATTENTION
        if (0.30 <= mastery_score < 0.50) or (recent_accuracy is not None and recent_accuracy < 0.50):
            reason = "Mastery is moderate but recent accuracy is low."
            if (0.30 <= mastery_score < 0.50):
                reason = "Mastery score is below the on-track threshold."
            action = "Assign targeted practice and monitor the next attempts."
            return "needs_attention", reason, action
            
        # 3. IMPROVING
        if trend == "improving":
            reason = "Recent performance is significantly better than earlier performance."
            action = "Continue practice while gradually increasing difficulty."
            return "improving", reason, action
            
        # 4. ON_TRACK
        if mastery_score >= 0.50 and consecutive_errors < 3:
            reason = "Mastery is solid and student is making consistent progress."
            action = "Continue the current learning path."
            return "on_track", reason, action
            
        # Fallback (e.g. unknown trend, high mastery but recent drops)
        return "on_track", "Student is performing acceptably.", "Continue the current learning path."
