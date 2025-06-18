from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.db import Base

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    service_name = Column(String, nullable=False)
    category = Column(String, nullable=True)    # ex. "Streaming", "Cloud", etc.
    monthly_cost = Column(Float, nullable=True)
    renewal_date = Column(Date, nullable=True)  # Optional: auto-renew marker
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="subscriptions")
