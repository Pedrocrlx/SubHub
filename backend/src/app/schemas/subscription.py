from pydantic import BaseModel
from typing import Optional
from datetime import date

class SubscriptionBase(BaseModel):
    service_name: str
    category: Optional[str] = None
    monthly_cost: Optional[float] = None
    renewal_date: Optional[date] = None

class SubscriptionCreate(SubscriptionBase):
    pass

class SubscriptionUpdate(SubscriptionBase):
    pass

class SubscriptionRead(SubscriptionBase):
    id: int
    service_name: str
    category: Optional[str] = None
    monthly_cost: float
    renewal_date: Optional[date] = None
    user_id: int

    class Config:
        from_attributes = True
