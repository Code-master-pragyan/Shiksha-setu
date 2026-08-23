import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
from app.db.database import engine, verify_db_connection
from sqlalchemy import text

logging.basicConfig(level=logging.INFO, format='%(message)s')

def check_db():
    if not verify_db_connection():
        print("Database connection: FAILED")
        sys.exit(1)
        
    print("Database connection: OK")
    print("\nTables:")
    
    tables = [
        "users",
        "student_profiles",
        "concepts",
        "sources",
        "questions",
        "attempts",
        "student_mastery"
    ]
    
    with engine.connect() as conn:
        # Check database name
        db_name = conn.execute(text("SELECT current_database();")).scalar()
        print(f"Database Name: {db_name}\n")
        
        for table in tables:
            try:
                count = conn.execute(text(f"SELECT COUNT(*) FROM {table};")).scalar()
                print(f"{table}: {count}")
            except Exception as e:
                print(f"{table}: ERROR ({e})")

if __name__ == "__main__":
    check_db()
