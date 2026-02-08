"""
FastAPI Dependencies

Authentication and authorization dependencies for route protection.
"""

from typing import Optional
from uuid import UUID
from datetime import datetime
from fastapi import Depends, HTTPException, status, Request
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


async def get_optional_user(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Dependency to optionally get user from token (doesn't raise error if no token).

    Useful for endpoints that have different behavior for authenticated vs. anonymous users.

    Args:
        request: FastAPI Request object
        db: Database session

    Returns:
        User object if authenticated, None otherwise
    """
    # Get Authorization header from request
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    try:
        # Extract token
        token = auth_header.split(" ")[1]
        payload = verify_token(token, token_type="access")

        if payload is None:
            return None

        # Extract user ID from token payload
        user_id_str: Optional[str] = payload.get("sub")
        if user_id_str is None:
            return None

        # Convert to UUID and fetch user
        user_id = UUID(user_id_str)
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        return user
    except (ValueError, Exception):
        # Return None on any error instead of raising
        return None


async def verify_quota(
    current_user: User = Depends(get_current_user),
    feature: str = "adaptive-path"
) -> None:
    """
    Dependency to enforce monthly rate limits for premium features.

    Checks and increments quota counter for:
    - 10 adaptive paths per premium user per month
    - 20 assessments per premium user per month

    Raises:
        HTTPException: 429 if user has exceeded monthly quota

    Args:
        current_user: Current authenticated user
        feature: Feature being accessed ("adaptive-path" or "assessment")
    """
    from app.services.rate_limiter import RateLimiter, RateLimitExceededError

    # Create rate limiter instance
    rate_limiter = RateLimiter(db=None)  # We'll set db in a moment

    # Import get_db function (circular import avoidance)
    from app.database import get_db

    # Get database session
    async def get_db_session():
        async for session in get_db():
            yield session
            break

    # Get database session
    async for db in get_db_session():
        rate_limiter.db = db
        break

    try:
        # Check and increment quota
        usage = await rate_limiter.check_and_increment(
            student_id=str(current_user.id),
            feature=feature
        )

        logger.info(
            f"Quota check passed for student {current_user.id[:8]}... "
            f"feature={feature} used={usage['used']}/{usage['limit']}"
        )

        return None

    except RateLimitExceededError as e:
        # Calculate reset date
        next_month = datetime.now().replace(day=1) + timedelta(days=32)
        next_month = next_month.replace(day=1)

        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "code": "RATE_LIMIT_EXCEEDED",
                "message": f"You have exceeded your monthly quota for {e.feature}s.",
                "quota": {
                    "feature": e.feature,
                    "used": e.used,
                    "limit": e.limit,
                    "resets_at": e.resets_at.isoformat()
                },
                "upgrade_option": {
                    "tier": "pro",
                    "benefit": f"Unlimited {e.feature}s and AI features",
                    "price_monthly": 19.99,
                    "upgrade_url": "/api/v1/payments/create-checkout-session"
                }
            }
        )

    except Exception as ex:
        # Log error but don't block request if rate limiting fails
        logger.error(f"Rate limiter error for student {current_user.id[:8]}...: {str(ex)}")
        # Allow request to proceed (fail open)
        return None
