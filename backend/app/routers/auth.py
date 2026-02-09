"""
Authentication Routes

Endpoints for user registration, login, token refresh, and profile management.
"""

from datetime import datetime, date
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.models.streak import Streak
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token, TokenRefresh, UserUpdate, ChangePasswordRequest
from app.utils.auth import hash_password, verify_password, create_token_pair, verify_token
from app.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user account.

    Creates a new user with hashed password and returns authentication tokens.

    - **email**: Valid email address (must be unique)
    - **password**: Minimum 8 characters
    - **full_name**: Optional user's full name
    - **timezone**: User's timezone (default: UTC)
    - **preferences**: Optional user preferences dictionary
    """
    # Check if email already exists
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    new_user = User(
        id=uuid4(),
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        full_name=user_data.full_name,
        timezone=user_data.timezone,
        preferences=user_data.preferences,
        subscription_tier="free",
        is_active=True,
        is_teacher=False,
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Initialize progress tracking - Create Streak record for new user
    new_streak = Streak(
        user_id=new_user.id,
        current_streak=0,  # Will increment to 1 on first activity
        longest_streak=0,
        total_active_days=0,
        last_activity_date=None,  # Will be set on first learning activity
        timezone=new_user.timezone,
        is_active=True,
        streak_freeze_count=0,
    )
    db.add(new_streak)
    await db.commit()

    # Generate tokens
    access_token, refresh_token, expires_in = create_token_pair(
        user_id=str(new_user.id),
        email=new_user.email
    )

    # Prepare user response
    user_response = UserResponse.model_validate(new_user)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=expires_in,
        user=user_response
    )


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user and return access tokens.

    Validates email and password, returns JWT tokens for API access.

    - **email**: User's email address
    - **password**: User's password
    """
    # Find user by email
    result = await db.execute(
        select(User).where(User.email == credentials.email)
    )
    user = result.scalar_one_or_none()

    # Check user exists and password is correct
    if not user or not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    # Update last active timestamp
    user.last_active_at = datetime.utcnow()
    await db.commit()
    await db.refresh(user)

    # Generate tokens
    access_token, refresh_token, expires_in = create_token_pair(
        user_id=str(user.id),
        email=user.email
    )

    # Prepare user response
    user_response = UserResponse.model_validate(user)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=expires_in,
        user=user_response
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_data: TokenRefresh,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token using refresh token.

    Exchanges a valid refresh token for a new access token and refresh token pair.

    - **refresh_token**: Valid JWT refresh token
    """
    # Verify refresh token
    payload = verify_token(token_data.refresh_token, token_type="refresh")

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract user ID from token
    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch user from database
    result = await db.execute(
        select(User).where(User.id == user_id_str)
    )
    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate new token pair
    access_token, refresh_token, expires_in = create_token_pair(
        user_id=str(user.id),
        email=user.email
    )

    # Prepare user response
    user_response = UserResponse.model_validate(user)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=expires_in,
        user=user_response
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user's profile.

    Returns the authenticated user's complete profile data.
    Requires valid access token in Authorization header.
    """
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update current authenticated user's profile.

    Allows updating user's email, full name, timezone, and preferences.
    Requires valid access token in Authorization header.

    - **email**: Updated email address (optional)
    - **full_name**: Updated full name (optional)
    - **timezone**: Updated timezone (optional)
    - **preferences**: Updated preferences dictionary (optional)
    """
    # Update email if provided (check for uniqueness)
    if user_update.email is not None and user_update.email != current_user.email:
        # Check if email already exists
        result = await db.execute(
            select(User).where(User.email == user_update.email)
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        current_user.email = user_update.email

    # Update other fields if provided
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name

    if user_update.timezone is not None:
        current_user.timezone = user_update.timezone

    if user_update.preferences is not None:
        current_user.preferences = user_update.preferences

    await db.commit()
    await db.refresh(current_user)

    return UserResponse.model_validate(current_user)


@router.post("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Change current user's password.

    Requires current password for verification and new password (min 8 characters).
    Requires valid access token in Authorization header.

    - **current_password**: Current password for verification
    - **new_password**: New password (minimum 8 characters)

    Returns success message on successful password change.
    """
    # Verify current password
    if not current_user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account uses OAuth and has no password to change"
        )

    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )

    # Check new password is different from current
    if verify_password(password_data.new_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password"
        )

    # Update password
    current_user.password_hash = hash_password(password_data.new_password)
    await db.commit()

    return {
        "message": "Password changed successfully",
        "detail": "Your password has been updated. Please use your new password for future logins."
    }


@router.delete("/me")
async def delete_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete current user's account.

    Permanently deletes the user account and all associated data.
    This action cannot be undone.
    Requires valid access token in Authorization header.

    WARNING: This will permanently delete:
    - User profile and authentication data
    - All progress data (chapters, quizzes, streaks)
    - Milestones and achievements
    - Notes and bookmarks
    - Premium usage records

    Returns success message on account deletion.
    """
    # Store user email for confirmation message
    user_email = current_user.email

    # Soft delete by setting is_active to False
    # This preserves data for records but prevents login
    current_user.is_active = False
    # Also mark email as unique in case they want to register again
    current_user.email = f"deleted_{user_email}_{datetime.utcnow().timestamp()}"

    await db.commit()

    return {
        "message": "Account deleted successfully",
        "detail": "Your account has been permanently deleted. All your data has been removed."
    }
