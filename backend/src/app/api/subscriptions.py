"""
Subscription management endpoints
"""
from fastapi import APIRouter, Body, HTTPException, Depends, status
from typing import List, Dict, Any, Optional, Tuple

from src.app.models.subscription import Subscription
from src.app.models.user import User
from src.app.core.security import get_current_user
from src.app.db.storage import save_data_to_file
from src.app.core.logging import application_logger

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
    
    application_logger.info(f"User [{current_user.email}] successfully added subscription: [{new_subscription.service_name}]")
    return {
        "message": "Subscription added", 
        "service": new_subscription.service_name
    }

@router.get("", response_model=List[Subscription])
def list_subscriptions(current_user: User = Depends(get_current_user)) -> List[Subscription]:
    """
    Get all subscriptions for the current user
    
    Returns a list of all subscription objects for the authenticated user.
    Returns an empty list if the user has no subscriptions.
    """
    subscription_count = len(current_user.subscriptions)
    application_logger.info(f"User [{current_user.email}] viewed their [{subscription_count}] subscriptions")
    return current_user.subscriptions

@router.put("/{service_name}", response_model=Dict[str, str])
def update_subscription(
    service_name: str,
    updated_subscription: dict = Body(..., description="Updated subscription details"),
    current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Update an existing subscription
    
    Locates the specified subscription by service name and updates its details.
    If no matching subscription is found, returns a 404 error.
    If the updated name would create a duplicate, returns a 409 error.
    
    Returns a success message indicating the subscription was updated.
    """
    application_logger.info(f"User [{current_user.email}] updating subscription: [{service_name}]")
    
    # Validate category if provided - centralized validation
    if "category" in updated_subscription:
        if not isinstance(updated_subscription["category"], str):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Category must be a string"
            )
        elif not updated_subscription["category"].strip():
            application_logger.warning(f"User [{current_user.email}] attempted to update subscription with empty category")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Category cannot be empty"
            )
    
    # Find the subscription using helper function
    index, existing_subscription = find_subscription_by_name(current_user, service_name)
    
    # If subscription not found
    if existing_subscription is None:
        application_logger.warning(f"User [{current_user.email}] attempted to update non-existent subscription: [{service_name}]")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subscription [{service_name}] not found for current user"
        )
    
    # Check for name conflicts if name is being updated
    if "service_name" in updated_subscription:
        new_name = updated_subscription["service_name"]
        if new_name.lower() != service_name.lower() and check_duplicate_subscription(current_user, new_name):
            application_logger.warning(
                f"User [{current_user.email}] attempted to update subscription to existing name: [{new_name}]"
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Subscription with name '{new_name}' already exists"
            )
    
    # Update and validate in a single step using model methods
    updated_data = existing_subscription.model_dump()
    updated_data.update(updated_subscription)
    
    try:
        # Create and validate updated subscription object
        validated_subscription = Subscription(**updated_data)
        
        # Update the subscription
        current_user.subscriptions[index] = validated_subscription
        
        # Save changes
        save_data_to_file()
        
        application_logger.info(f"User [{current_user.email}] successfully updated subscription: [{service_name}]")
        return {
            "message": f"Subscription {service_name} updated successfully",
            "service": validated_subscription.service_name
        }
    except ValueError as e:
        # Handle validation errors from Pydantic
        application_logger.warning(f"User [{current_user.email}] update validation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )

@router.delete("/{service_name}", response_model=Dict[str, str])
def delete_subscription(
    service_name: str, 
    current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Delete a subscription by service name
    
    Removes the specified subscription from the user's subscription list.
    If no matching subscription is found, returns a 404 error.
    
    Returns a success message indicating the subscription was deleted.
    """
    # Find the subscription first to provide better error messages
    index, subscription = find_subscription_by_name(current_user, service_name)
    
    if subscription is None:
        application_logger.warning(f"User [{current_user.email}] attempted to delete non-existent subscription: [{service_name}]")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Subscription [{service_name}] not found for current user"
        )
    
    # More efficient deletion when we already know the index
    exact_name = subscription.service_name  # Preserve exact case for response
    current_user.subscriptions.pop(index)
    
    # Save changes and return success message
    save_data_to_file()
    application_logger.info(f"User [{current_user.email}] deleted subscription: [{exact_name}]")
    
    return {
        "message": f"Subscription {exact_name} deleted successfully",
        "service": exact_name
    }
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
