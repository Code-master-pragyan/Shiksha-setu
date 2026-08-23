import pytest
from app.db.database import verify_db_connection, Base, SessionLocal
from app.db.models import User, StudentProfile, Concept, Source, Question, Attempt, StudentMastery
from sqlalchemy.exc import IntegrityError
import uuid

@pytest.fixture(scope="module")
def db_session():
    if not verify_db_connection():
        pytest.skip("Database is not available")
        
    # Bind engine and create tables if they don't exist
    from app.db.database import engine
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_user_creation(db_session):
    test_uuid = uuid.uuid4()
    email = f"test_{test_uuid}@example.com"
    user = User(name="Test User", email=email, role="student")
    db_session.add(user)
    db_session.commit()
    
    db_user = db_session.query(User).filter_by(email=email).first()
    assert db_user is not None
    assert db_user.name == "Test User"
    assert db_user.role == "student"

def test_student_profile_creation(db_session):
    user = User(name="Profile Test", email=f"profile_{uuid.uuid4()}@example.com", role="student")
    db_session.add(user)
    db_session.commit()
    
    profile = StudentProfile(user_id=user.id, grade=5)
    db_session.add(profile)
    db_session.commit()
    
    db_profile = db_session.query(StudentProfile).filter_by(user_id=user.id).first()
    assert db_profile is not None
    assert db_profile.grade == 5
    assert db_profile.preferred_language == "English"
    
    # Check relationship
    assert db_profile.user.id == user.id

def test_unique_email_constraint(db_session):
    email = f"duplicate_{uuid.uuid4()}@example.com"
    u1 = User(name="U1", email=email, role="student")
    db_session.add(u1)
    db_session.commit()
    
    u2 = User(name="U2", email=email, role="teacher")
    db_session.add(u2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

def test_concept_mastery_unique_constraint(db_session):
    user = User(name="Mastery Test", email=f"mastery_{uuid.uuid4()}@example.com", role="student")
    db_session.add(user)
    db_session.commit()
    
    profile = StudentProfile(user_id=user.id, grade=10)
    db_session.add(profile)
    db_session.commit()
    
    concept = Concept(subject="Math", grade=10, name=f"Algebra_{uuid.uuid4()}")
    db_session.add(concept)
    db_session.commit()
    
    m1 = StudentMastery(student_id=profile.id, concept_id=concept.id, mastery_score=0.5)
    db_session.add(m1)
    db_session.commit()
    
    m2 = StudentMastery(student_id=profile.id, concept_id=concept.id, mastery_score=0.8)
    db_session.add(m2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()
