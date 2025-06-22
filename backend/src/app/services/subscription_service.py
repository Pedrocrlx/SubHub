from sqlalchemy.orm import Session
from app.models.subscription import Subscription
from app.schemas.subscription import SubscriptionCreate, SubscriptionUpdate

def create_subscription(db: Session, user_id: int, subscription_in: SubscriptionCreate):
    sub = Subscription(**subscription_in.dict(), user_id=user_id)
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub

def get_subscriptions(db: Session, user_id: int):
    return db.query(Subscription).filter(Subscription.user_id == user_id).all()

def get_subscription_by_id(db: Session, user_id: int, sub_id: int):
    return db.query(Subscription).filter(Subscription.id == sub_id, Subscription.user_id == user_id).first()

def update_subscription(db: Session, user_id: int, sub_id: int, sub_update: SubscriptionUpdate):
    sub = get_subscription_by_id(db, user_id, sub_id)
    if sub:
        for field, value in sub_update.dict(exclude_unset=True).items():
            setattr(sub, field, value)
        db.commit()
        db.refresh(sub)
    return sub

def delete_subscription(db: Session, user_id: int, sub_id: int):
    sub = get_subscription_by_id(db, user_id, sub_id)
    if sub:
        db.delete(sub)
        db.commit()
    return sub
