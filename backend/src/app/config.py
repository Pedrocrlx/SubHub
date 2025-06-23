import os
import secrets
from pathlib import Path

class Settings:
    APP_NAME = "SubHub API"  
    VERSION = "1.0"
    MIN_PASSWORD_LENGTH = 8
    PASSWORD_REQUIRES_UPPERCASE = True
    PASSWORD_REQUIRES_NUMBER = True
    PASSWORD_REQUIRES_SYMBOL = True
    SECRET_KEY = os.environ.get("SECRET_KEY", secrets.token_hex(32))
    
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_FILEPATH = os.path.join(BASE_DIR, "subhub_data.json")

app_settings = Settings()