from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from app.db import get_db
from app.models.user import User
from app.services import user_service
from app.services.auth import SECRET_KEY, ALGORITHM

# OAuth2 scheme declaration
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token: no subject")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = user_service.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
