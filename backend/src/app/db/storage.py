"""
Data storage and persistence functionality for SubHub API

This module provides:
- In-memory data stores for users and sessions
- Functions to save application state to disk
- Functions to load application state from disk
- Safe operation wrappers with error handling
"""
import json
import os
import traceback
from typing import Dict, Any, Callable, TypeVar, Optional
from datetime import date
from pathlib import Path

from src.app.models.user import User
from src.app.models.subscription import Subscription
from src.app.config import app_settings
from src.app.core.logging import application_logger

# Type variable for generic function return types
T = TypeVar('T')

# ===== GLOBAL DATA STORES =====

# Store user objects indexed by email
user_database: Dict[str, User] = {}

# Store active user sessions indexed by token
active_sessions: Dict[str, Any] = {}

# ===== SAFE OPERATION WRAPPER =====

def safe_operation(operation: Callable[..., T], error_message: str, *args, **kwargs) -> Optional[T]:
    """
    Execute an operation with proper error handling and logging
    
    Args:
        operation: Function to execute safely
        error_message: Human-readable message to log if an error occurs
        *args, **kwargs: Arguments to pass to the operation
        
    Returns:
        The result of the operation or None if it failed
        
    Example:
        result = safe_operation(
            json.loads, 
            "Failed to parse JSON configuration", 
            config_string
        )
    """
    try:
        return operation(*args, **kwargs)
    except Exception as error:
        application_logger.error(f"{error_message}: {str(error)}")
        application_logger.debug(traceback.format_exc())
        return None

# ===== FILE OPERATIONS =====

def ensure_data_directory_exists() -> bool:
    """
    Ensure the directory for data storage exists
    
    Returns:
        True if directory exists or was created, False on failure
    """
    data_dir = os.path.dirname(app_settings.DATA_FILEPATH)
    
    try:
        # Use pathlib for more reliable directory creation
        Path(data_dir).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as error:
        application_logger.error(f"Failed to create data directory: {str(error)}")
        return False

def save_data_to_file() -> bool:
    """
    Save all application data to disk as JSON
    
    Stores user data with password hashes directly in the user objects.
    Session data is deliberately not persisted for security reasons.
    
    Returns:
        True if save was successful, False otherwise
    """
    # Ensure the data directory exists before attempting to save
    if not ensure_data_directory_exists():
        return False
        
    def perform_save():
        # Prepare data structure for serialization
        data_to_save = {
            "users": {email: user.model_dump() for email, user in user_database.items()}
            # Note: active sessions are deliberately not saved to disk for security
        }
        
        # Write data to file with pretty formatting
        with open(app_settings.DATA_FILEPATH, "w") as data_file:
            json.dump(data_to_save, data_file, default=str, indent=2)
            
        application_logger.info(f"Data successfully saved to {app_settings.DATA_FILEPATH}")
        return True
    
    result = safe_operation(perform_save, "Failed to save application data")
    return result is not None

def load_data_from_file() -> bool:
    """
    Load application data from disk if available
    
    Restores user data from the JSON file with password hashes included in each user object.
    
    Returns:
        True if load was successful, False if file doesn't exist or load failed
    """
    # Check if data file exists
    if not os.path.exists(app_settings.DATA_FILEPATH):
        application_logger.info(f"No data file found at {app_settings.DATA_FILEPATH}")
        return False
    
    def perform_load():
        application_logger.info(f"Loading data from {app_settings.DATA_FILEPATH}")
        
        with open(app_settings.DATA_FILEPATH, "r") as data_file:
            loaded_data = json.load(data_file)
            
            # Clear existing data stores
            user_database.clear()
            # Don't clear active sessions - let them remain valid
            
            # Restore user data with proper date conversion
            for email, user_data in loaded_data.get("users", {}).items():
                # Process subscriptions to convert date strings to date objects
                if "subscriptions" in user_data:
                    for subscription in user_data["subscriptions"]:
                        if "starting_date" in subscription and isinstance(subscription["starting_date"], str):
                            try:
                                # Convert ISO format string to date object
                                subscription["starting_date"] = date.fromisoformat(subscription["starting_date"])
                            except ValueError:
                                # If conversion fails, use current date as fallback
                                application_logger.warning(
                                    f"Invalid date format in subscription for user {email}, using today's date"
                                )
                                subscription["starting_date"] = date.today()
                
                # Create user object from loaded data
                try:
                    # Password hash is now stored directly in the user object as 'passhash'
                    user_database[email] = User(**user_data)
                except Exception as e:
                    application_logger.error(f"Failed to load user {email}: {str(e)}")
                    continue
            
            user_count = len(user_database)
            application_logger.info(f"Successfully loaded {user_count} users from data file")
            return True
            
    return safe_operation(perform_load, "Failed to load application data") or False

def store_password_hash(username: str, password_hash: str) -> None:
    """
    Store password hash directly in the user object
    
    Args:
        username: User's username
        password_hash: Hashed password to store
        
    Note:
        This function assumes the user already exists in user_database
    """
    try:
        # Find the user by username
        for email, user in user_database.items():
            if user.username == username:
                # Store the hash directly in the user object
                user.passhash = password_hash
                application_logger.debug(f"Stored password hash for user {username}")
                return
        
        application_logger.warning(f"Attempted to store password hash for non-existent user: {username}")
    except Exception as e:
        application_logger.error(f"Failed to store password hash: {str(e)}")
        raise
