import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.database import SessionLocal
from app.db.models.concept import Concept
from sqlalchemy import select

db = SessionLocal()

chapters = [
    {"subject": "Science", "grade": 8, "name": "The Invisible Living World: Beyond Our Naked Eye", "difficulty": "beginner"},
    {"subject": "Science", "grade": 8, "name": "Health: The Ultimate Treasure", "difficulty": "beginner"},
    {"subject": "Science", "grade": 8, "name": "Exploring the Investigative World of Science", "difficulty": "beginner"},
]

for ch in chapters:
    existing = db.scalar(select(Concept).where(Concept.name == ch["name"]))
    if not existing:
        db.add(Concept(**ch))
        print("Added:", ch["name"])
    else:
        print("Already exists:", ch["name"])

db.commit()
db.close()
print("Done")
