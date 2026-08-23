import sys
import os

# Add parent directory to path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
from app.db.database import engine, Base
from app.db.models import * # Import all models so they register with Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    if not engine:
        logger.error("Engine not initialized. Check your DATABASE_URL.")
        sys.exit(1)
    
    logger.info("Creating database tables...")
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)
        logger.info("Successfully created database tables.")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        sys.exit(1)

if __name__ == "__main__":
    init_db()
