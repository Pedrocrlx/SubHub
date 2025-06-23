from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db import get_db
from app.services import subscription_service
from app.routers.user import get_current_user, UserRead  # To extract user from JWT | For type hinting (Giulio)
from app.schemas.subscription import SubscriptionCreate, SubscriptionRead, SubscriptionUpdate

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])

@router.post("/", response_model=SubscriptionRead, status_code=status.HTTP_201_CREATED)
def create_subscription(
    subscription: SubscriptionCreate,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return subscription_service.create_subscription(db, current_user.id, subscription)

@router.get("/", response_model=List[SubscriptionRead])
def read_subscriptions(
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return subscription_service.get_subscriptions(db, current_user.id)

@router.get("/{sub_id}", response_model=SubscriptionRead)
def read_subscription(
    sub_id: int,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sub = subscription_service.get_subscription_by_id(db, current_user.id, sub_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return sub

@router.patch("/{sub_id}", response_model=SubscriptionRead)
def update_subscription(
    sub_id: int,
    sub_update: SubscriptionUpdate,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sub = subscription_service.update_subscription(db, current_user.id, sub_id, sub_update)
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return sub

@router.delete("/{sub_id}")
def delete_subscription(
    sub_id: int,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sub = subscription_service.delete_subscription(db, current_user.id, sub_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return {"message": "Subscription deleted successfully"}