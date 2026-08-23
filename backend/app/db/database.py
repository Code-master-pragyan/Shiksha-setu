import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from app.core.config import settings

logger = logging.getLogger(__name__)

engine = None
SessionLocal = None
Base = declarative_base()

import sys

if settings.DATABASE_URL:
    db_url = settings.DATABASE_URL
    is_pytest = "pytest" in sys.modules
    
    if is_pytest:
        if settings.ENVIRONMENT == "production":
            logger.error("FATAL: Tests CANNOT run against production environment!")
            raise RuntimeError("Test execution blocked: ENVIRONMENT is 'production'.")
        
        if settings.TEST_DATABASE_URL:
            db_url = settings.TEST_DATABASE_URL
            logger.info("Using TEST_DATABASE_URL for database connection.")
        else:
            logger.warning("Running tests without TEST_DATABASE_URL. Falling back to DATABASE_URL.")

    try:
        engine = create_engine(db_url, pool_pre_ping=True)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    except Exception as e:
        logger.error(f"Failed to initialize database engine: {e}")
else:
    logger.warning("DATABASE_URL is not set. Database functionality will not work.")

def get_db():
    if not SessionLocal:
        raise RuntimeError("Database is not configured.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_db_connection() -> bool:
    """Helper to test database connectivity."""
    if not engine:
        return False
    try:
        with engine.connect() as connection:
            connection.exec_driver_sql("SELECT 1")
        return True
    except SQLAlchemyError as e:
        logger.error(f"Database connection failed: {e}")
        return False
