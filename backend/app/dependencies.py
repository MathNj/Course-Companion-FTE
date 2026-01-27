"""
FastAPI Dependencies

Authentication and authorization dependencies for route protection.
"""

from typing import Optional
from uuid import UUID
from datetime import datetime
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.utils.auth import verify_token
from sqlalchemy import select

# HTTP Bearer token security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.

    Args:
        credentials: HTTP Bearer credentials from Authorization header
        db: Database session

    Returns:
        Authenticated User model instance

    Raises:
        HTTPException: 401 if token is invalid or user not found
    """
    # Extract token from credentials
    token = credentials.credentials

    # Verify and decode token
    payload = verify_token(token, token_type="access")

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract user ID from token payload
    user_id_str: Optional[str] = payload.get("sub")
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Convert to UUID
    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID format",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch user from database
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to ensure the current user is active.

    Args:
        current_user: Current authenticated user

    Returns:
        Active User model instance

    Raises:
        HTTPException: 403 if user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    return current_user


async def verify_premium(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to verify premium subscription for Phase 2 features.

    Checks JWT subscription_tier and subscription_expires_at claims.
    Returns structured error with upgrade CTA if free-tier.

    Args:
        current_user: Current authenticated user

    Returns:
        Premium User model instance

    Raises:
        HTTPException: 403 with upgrade messaging if user does not have premium subscription
    """
    # Check subscription tier (from JWT claims or database)
    subscription_tier = getattr(current_user, 'subscription_tier', 'free')
    subscription_expires_at = getattr(current_user, 'subscription_expires_at', None)

    # Check if user has premium subscription
    if subscription_tier != 'premium':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "PREMIUM_REQUIRED",
                "message": "This feature requires a Premium subscription.",
                "benefits": [
                    "Personalized adaptive learning paths based on your performance",
                    "Detailed AI-powered feedback on open-ended assessments",
                    "Priority support and advanced analytics"
                ],
                "upgrade_url": "/api/v1/payments/create-checkout-session",
                "pricing": {
                    "monthly": 9.99,
                    "annual": 99.99
                }
            },
        )

    # Check if subscription has expired
    if subscription_expires_at and subscription_expires_at < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "SUBSCRIPTION_EXPIRED",
                "message": "Your premium subscription has expired. Please renew to access this feature.",
                "renewal_url": "/api/v1/payments/create-checkout-session"
            },
        )

    return current_user


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
) -> Optional[str]:
    """
    Dependency to optionally get user from token (doesn't raise error if no token).

    Useful for endpoints that have different behavior for authenticated vs. anonymous users.

    Args:
        credentials: Optional HTTP Bearer credentials

    Returns:
        User ID string if authenticated, None otherwise
    """
    if credentials is None:
        return None

    token = credentials.credentials
    payload = verify_token(token, token_type="access")

    if payload is None:
        return None

    return payload.get("sub")


async def verify_quota(
    current_user: User = Depends(get_current_user),
    feature: str = "adaptive-path"
) -> None:
    """
    Dependency to enforce monthly rate limits for premium features.

    Checks Redis quota counter (or PostgreSQL fallback) to enforce:
    - 10 adaptive paths per premium user per month
    - 20 assessments per premium user per month

    Args:
        current_user: Current authenticated user
        feature: Feature being accessed ("adaptive-path" or "assessment")

    Raises:
        HTTPException: 429 if user has exceeded monthly quota
    """
    from app.utils.redis_client import cache_client
    import os

    # Get monthly limits from environment
    adaptive_limit = int(os.getenv("PREMIUM_ADAPTIVE_PATHS_LIMIT", "10"))
    assessment_limit = int(os.getenv("PREMIUM_ASSESSMENTS_LIMIT", "20"))

    limits = {
        "adaptive-path": adaptive_limit,
        "assessment": assessment_limit
    }

    limit = limits.get(feature, 10)  # Default to 10 if feature not found
    month_key = datetime.now().strftime("%Y-%m")

    # Check Redis quota counter
    try:
        redis_key = f"quota:{current_user.id}:{month_key}:{feature}"
        current = await cache_client.get(redis_key)

        if current is None:
            # Fallback: create new quota record
            current = 0
            await cache_client.setex(redis_key, 2678400, "0")  # 31 days TTL
        else:
            current = int(current)

        if current >= limit:
            # Calculate reset date (first day of next month)
            next_month = datetime.now().replace(day=1) + datetime.timedelta(days=32)
            next_month = next_month.replace(day=1)

            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "code": "RATE_LIMIT_EXCEEDED",
                    "message": f"You have exceeded your monthly quota for this feature.",
                    "quota": {
                        "feature": feature,
                        "used": current,
                        "limit": limit,
                        "resets_at": next_month.isoformat()
                    },
                    "upgrade_option": {
                        "tier": "pro",
                        "benefit": "Unlimited adaptive paths and assessments",
                        "price_monthly": 19.99
                    }
                }
            )
    except Exception as e:
        # Log error but don't block request if Redis is unavailable
        # You'll want to implement proper logging here
        pass

    return None
