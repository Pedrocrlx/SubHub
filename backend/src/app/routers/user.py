from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.db import get_db, SessionLocal
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.services import user_service

router = APIRouter(prefix="/users", tags=["users"])

# Helper to extract the current user from JWT token
def get_current_user(request: Request, db: Session) -> UserRead:
    email = request.state.user
    user = user_service.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

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
def read_own_user(request: Request, db: Session = Depends(get_db)):
    return get_current_user(request, db)

@router.patch("/me", response_model=UserRead)
def update_own_user(
    user_update: UserUpdate,
    request: Request,
    db: Session = Depends(get_db)
):
    user = get_current_user(request, db)
    updated_user = user_service.update_user(db, user, user_update)
    return updated_user

@router.delete("/me")
def delete_own_user(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    user_service.delete_user(db, user)
    return {"message": "User deleted successfully"}