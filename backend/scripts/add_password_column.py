import os
import sys
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import engine

def main():
    print("Adding hashed_password column to users table...")
    with engine.begin() as conn:
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN hashed_password VARCHAR;"))
            print("Column successfully added!")
        except Exception as e:
            if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
                print("Column already exists. Skipping.")
            else:
                print(f"Error adding column: {e}")
                raise

if __name__ == "__main__":
    main()
