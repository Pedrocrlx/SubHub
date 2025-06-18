"""
Entry point for the SubHub API with exports for test compatibility
"""
# Import the app
from app.main import app

# Re-export variables needed by tests
from app.db.storage import (
    user_database, 
    password_storage, 
    active_sessions,
    save_data_to_file,
    load_data_from_file
)

# Re-export security functions needed by tests
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)

# Re-export settings
from app.config import app_settings  # Changed: don't rename this variable

# Ensure setup_logging is available for tests
try:
    from app.core.logging import setup_logging
except ImportError:
    # Fallback if not available
    def setup_logging():
        return None, None

# Entry point when running directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)