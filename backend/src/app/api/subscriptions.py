"""
Subscription management endpoints
"""
from fastapi import APIRouter, Body, HTTPException, Depends
from app.models.subscription import Subscription
from app.models.user import User
from app.core.security import get_current_user
from app.db.storage import save_data_to_file
from app.core.logging import application_logger

router = APIRouter(tags=["Subscriptions"])

@router.post("", status_code=201)
def add_subscription(
    new_subscription: Subscription = Body(..., description="Subscription details to add"),
    current_user: User = Depends(get_current_user)
):
    """Add a new subscription for the current user"""
    application_logger.info(
        f"User {current_user.email} adding subscription: {new_subscription.service_name} "
        f"(${new_subscription.monthly_price:.2f}/month, category: {new_subscription.category})"
    )
    
    # Check for duplicate subscriptions (case-insensitive)
    if any(existing_sub.service_name.lower() == new_subscription.service_name.lower() 
           for existing_sub in current_user.subscriptions):
        application_logger.warning(
            f"User {current_user.email} attempted to add duplicate subscription: {new_subscription.service_name}"
        )
        raise HTTPException(status_code=409, detail="Subscription already exists")
    
    # Add subscription to user's list
    current_user.subscriptions.append(new_subscription)
    save_data_to_file()
    
    application_logger.info(f"User {current_user.email} successfully added subscription: {new_subscription.service_name}")
    return {"message": "Subscription added", "service": new_subscription.service_name}

@router.get("")
def list_subscriptions(
    current_user: User = Depends(get_current_user)
):
    """Get all subscriptions for the current user"""
    application_logger.info(f"User {current_user.email} viewed their {len(current_user.subscriptions)} subscriptions")
    return current_user.subscriptions

@router.delete("/{service_name}")
def delete_subscription(
    service_name: str, 
    current_user: User = Depends(get_current_user)
):
    """Delete a subscription by service name"""
    # Find and remove the subscription with matching name
    for index, subscription in enumerate(current_user.subscriptions):
        if subscription.service_name == service_name:
            current_user.subscriptions.pop(index)
            application_logger.info(f"User {current_user.email} deleted subscription: {service_name}")
            save_data_to_file()
            return {"message": f"Subscription {service_name} deleted successfully"}
    
    # If we get here, no matching subscription was found
    application_logger.warning(f"User [{current_user.email}] attempted to delete non-existent subscription: [{service_name}]")
    raise HTTPException(status_code=404, detail=f"Subscription [{service_name}] not found for current user")