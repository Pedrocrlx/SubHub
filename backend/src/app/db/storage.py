"""
Data storage and persistence functionality for SubHub API
"""
import json
import os
import traceback
from typing import Dict, Any, Callable
from datetime import date
from app.models.user import User
from app.config import app_settings
from app.core.logging import application_logger

# ===== DATA STORAGE =====

# Global data stores
user_database: Dict[str, User] = {}
password_storage: Dict[str, str] = {}
active_sessions: Dict[str, Any] = {}

# ===== FILE OPERATIONS =====

def safe_operation(operation: Callable, error_message: str, *args, **kwargs):
    """Execute an operation safely with error handling"""
    try:
        return operation(*args, **kwargs)
    except Exception as error:
        application_logger.error(f"{error_message}: {str(error)}")
        application_logger.debug(traceback.format_exc())
        return None

def save_data_to_file():
    """Save all application data to disk as JSON"""
    def perform_save():
        data_to_save = {
            "users": {email: user.model_dump() for email, user in user_database.items()},
            "passwords": password_storage
        }
        with open(app_settings.DATA_FILEPATH, "w") as data_file:
            json.dump(data_to_save, data_file, default=str, indent=2)
    
    safe_operation(perform_save, "Could not save data to file")

def load_data_from_file():
    """Load application data from disk if available"""
    if not os.path.exists(app_settings.DATA_FILEPATH):
        return
    
    def perform_load():
        with open(app_settings.DATA_FILEPATH, "r") as data_file:
            loaded_data = json.load(data_file)
            
            # Clear existing data
            user_database.clear()
            password_storage.clear()
            active_sessions.clear()
            
            # Restore user data
            for email, user_data in loaded_data.get("users", {}).items():
                # Convert date strings back to date objects
                for subscription in user_data.get("subscriptions", []):
                    if "starting_date" in subscription:
                        subscription["starting_date"] = date.fromisoformat(subscription["starting_date"])
                # Recreate user object
                user_database[email] = User(**user_data)
                
            # Restore password hashes
            password_storage.update(loaded_data.get("passwords", {}))
            
    safe_operation(perform_load, "Could not load data from file")