"""
API Dependencies for Route Protection

This module contains dependency functions used to protect routes,
such as authentication and premium subscription checks.
"""

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

from app.database import get_db
from app.models.user import User


async def get_current_user(
    token: str,
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user from JWT token

    Args:
        token: JWT bearer token from Authorization header
        db: Database session

    Returns:
        User: Authenticated user object

    Raises:
        HTTPException: If token is invalid or user not found
    """
    try:
        from jose import jwt, JWTError
        from app.core.config import settings

        # Decode JWT token
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user


async def require_premium(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to require active premium subscription

    Checks if user has an active premium subscription.
    Raises 403 if not premium or subscription expired.

    Args:
        current_user: Authenticated user from get_current_user
        db: Database session

    Returns:
        User: User with active premium subscription

    Raises:
        HTTPException: If user doesn't have active premium subscription
    """
    # Refresh user from database to get latest subscription status
    user = db.query(User).filter(User.id == current_user.id).first()

    # Check if user has premium subscription
    if user.subscription_type != 'premium':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "premium_required",
                "message": "This feature requires a premium subscription",
                "upgrade_url": "/api/v2/premium/subscription/upgrade"
            }
        )

    # Check if subscription is still active
    if user.subscription_expires_at and user.subscription_expires_at < datetime.utcnow():
        # Subscription expired
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "subscription_expired",
                "message": "Your premium subscription has expired",
                "renew_url": "/api/v2/premium/subscription/upgrade"
            }
        )

    return user


async def get_optional_premium_user(
    token: Optional[str] = None,
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Dependency to get user if token provided, otherwise None

    Unlike get_current_user, this doesn't raise an exception if no token.
    Useful for optional authentication.

    Args:
        token: Optional JWT bearer token
        db: Database session

    Returns:
        Optional[User]: User if valid token, None otherwise
    """
    if not token:
        return None

    try:
        return await get_current_user(token, db)
    except HTTPException:
        return None
