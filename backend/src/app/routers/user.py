from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.services import user_service
from app.db import get_db
from app.core.security import get_current_user
from app.schemas.user import UserCreate, UserRead, UserUpdate, PasswordChange

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = user_service.get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    return user_service.create_user(db, user)

@router.get("/me", response_model=UserRead)
def read_own_user(current_user: UserRead = Depends(get_current_user)):
    return current_user

@router.patch("/me", response_model=UserRead)
def update_own_user(
    user_update: UserUpdate,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    updated_user = user_service.update_user(db, current_user, user_update)
    return updated_user

@router.delete("/me")
def delete_own_user(
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_service.delete_user(db, current_user)
    return {"message": "User deleted successfully"}

@router.patch("/me/password")
def update_password(
    payload: PasswordChange,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_service.update_password(db, current_user, payload.current_password, payload.new_password)
    return {"message": "Password updated successfully"}
