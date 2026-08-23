import pytest
from app.core.config import settings
from app.db.database import verify_db_connection

def test_settings_loaded():
    """Verify that settings can be loaded properly."""
    assert settings.ENVIRONMENT in ["development", "production", "test"]
    assert isinstance(settings.CORS_ORIGINS, str)

@pytest.mark.skipif(not verify_db_connection(), reason="Database is not configured or not running")
def test_database_connection():
    """Explicitly test the database connection if available."""
    assert verify_db_connection() is True
