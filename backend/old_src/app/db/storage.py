import json
import os
import time
import traceback
from typing import Dict, Any, Callable, TypeVar, cast, Optional, Union
from datetime import date
from app.models.user import User
from app.config import app_settings
from app.core.logging import application_logger

# Type definitions
T = TypeVar('T')
SessionData = Dict[str, Union[str, float]]

# Global data stores with specific typing
user_database: Dict[str, User] = {}
password_storage: Dict[str, str] = {}
active_sessions: Dict[str, Union[str, SessionData]] = {}

# Track last save time to prevent excessive disk I/O
_last_save_time: float = 0
_SAVE_THROTTLE_SECONDS: float = 1.0  # Minimum seconds between saves

def safe_operation(operation: Callable[..., T], error_message: str, *args, **kwargs) -> Optional[T]:
    """
    Execute an operation safely with comprehensive error handling
    
    Args:
        operation: The function to execute
        error_message: Message to log if operation fails
        *args: Positional arguments to pass to operation
        **kwargs: Keyword arguments to pass to operation
        
    Returns:
        The return value of the operation or None if it failed
    """
    try:
        return operation(*args, **kwargs)
    except json.JSONDecodeError as e:
        application_logger.error(f"{error_message} - JSON error: [{str(e)}]!")
        application_logger.debug(f"JSON error details: [{traceback.format_exc()}]")
        return None
    except PermissionError as e:
        application_logger.error(f"{error_message} - Permission denied: [{str(e)}]!")
        return None
    except FileNotFoundError as e:
        application_logger.error(f"{error_message} - File not found: [{str(e)}]!")
        return None
    except Exception as e:
        application_logger.error(f"{error_message}: [{str(e)}]!")
        application_logger.debug(f"Exception traceback: [{traceback.format_exc()}]")
        return None

def save_data_to_file(force: bool = False) -> bool:
    """
    Save all application data to disk as JSON
    
    Args:
        force: If True, bypass throttling and save immediately
        
    Returns:
        True if save was successful, False otherwise
    """
    global _last_save_time
    
    # Throttle saves to prevent excessive disk I/O
    current_time = time.time()
    if not force and current_time - _last_save_time < _SAVE_THROTTLE_SECONDS:
        application_logger.debug(f"Skipping save operation (throttled)!")
        return True
    
    def perform_save() -> bool:
        data_to_save = {
            "users": {email: user.model_dump() for email, user in user_database.items()},
            "passwords": password_storage
        }
        
        # First write to a temporary file, then rename to avoid data corruption on crash
        temp_filepath = f"{app_settings.DATA_FILEPATH}.tmp"
        with open(temp_filepath, "w") as data_file:
            json.dump(data_to_save, data_file, default=str, indent=2)
            
        # Ensure the file is written to disk
        data_file.flush()
        os.fsync(data_file.fileno())
        
        # Rename temp file to actual file (atomic operation on most filesystems)
        os.replace(temp_filepath, app_settings.DATA_FILEPATH)
        
        application_logger.debug(f"Data saved successfully to [{app_settings.DATA_FILEPATH}]!")
        return True
    
    result = safe_operation(perform_save, "Could not save data to file")
    
    if result:
        _last_save_time = current_time
        return True
    return False

def load_data_from_file() -> bool:
    """
    Load application data from disk if available
    
    Returns:
        True if data was loaded successfully, False otherwise
    """
    if not os.path.exists(app_settings.DATA_FILEPATH):
        application_logger.info(f"No data file found at [{app_settings.DATA_FILEPATH}], starting with empty database!")
        return False
    
    def perform_load() -> bool:
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
                        try:
                            subscription["starting_date"] = date.fromisoformat(
                                cast(str, subscription["starting_date"])
                            )
                        except ValueError:
                            application_logger.warning(
                                f"Invalid date format in subscription for user [{email}]! Using current date instead!"
                            )
                            subscription["starting_date"] = date.today()
                
                # Recreate user object
                try:
                    user_database[email] = User(**user_data)
                except Exception as e:
                    application_logger.error(f"Failed to create user object for [{email}]: [{str(e)}]!")
                    continue
            
            # Restore password hashes
            password_storage.update(loaded_data.get("passwords", {}))
            
            # Log successful load
            application_logger.info(
                f"Data loaded successfully: [{len(user_database)}] users, [{len(password_storage)}] password records!"
            )
            return True
    
    return bool(safe_operation(perform_load, "Could not load data from file"))

def backup_data_file() -> bool:
    """
    Create a timestamped backup of the data file
    
    Returns:
        True if backup was successful, False otherwise
    """
    if not os.path.exists(app_settings.DATA_FILEPATH):
        return False
    
    def perform_backup() -> bool:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_filepath = f"{app_settings.DATA_FILEPATH}.{timestamp}.bak"
        
        # Use copyfile instead of rename to keep the original
        with open(app_settings.DATA_FILEPATH, "rb") as src, open(backup_filepath, "wb") as dst:
            dst.write(src.read())
            
        application_logger.info(f"Backup created at [{backup_filepath}]!")
        return True
    
    return bool(safe_operation(perform_backup, "Could not create data backup"))