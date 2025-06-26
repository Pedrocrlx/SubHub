"""
Entry point for the SubHub API with exports for test compatibility
"""


# Re-export variables needed by tests
from src.app.db.storage import (
    user_database, 
    active_sessions,
    save_data_to_file,
    load_data_from_file
)

# Re-export security functions needed by tests
from src.app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)

# Re-export settings
from src.app.config import app_settings  # Changed: don't rename this variable

# Ensure setup_logging is available for tests
try:
    from src.app.core.logging import setup_logging
except ImportError:
    # Fallback if not available
    def setup_logging():
        return None, None

# Entry point when running directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.app.main:app", host="0.0.0.0", port=8000, reload=True)