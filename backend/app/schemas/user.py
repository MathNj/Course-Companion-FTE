"""
User Schemas

Pydantic schemas for user authentication, registration, and profile management.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    """Base user schema with common fields."""

    email: EmailStr = Field(..., description="User's email address")
    full_name: Optional[str] = Field(None, max_length=255, description="User's full name")
    timezone: str = Field(default="UTC", max_length=50, description="User's timezone")
    preferences: dict = Field(default_factory=dict, description="User preferences (UI settings, notifications, etc.)")


class UserCreate(UserBase):
    """Schema for user registration."""

    password: str = Field(..., min_length=8, max_length=100, description="User's password (min 8 characters)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "student@example.com",
                "password": "SecurePass123!",
                "full_name": "Jane Doe",
                "timezone": "America/New_York",
                "preferences": {
                    "theme": "dark",
                    "notifications": True
                }
            }
        }
    )


class UserUpdate(BaseModel):
    """Schema for updating user profile."""

    full_name: Optional[str] = Field(None, max_length=255)
    timezone: Optional[str] = Field(None, max_length=50)
    preferences: Optional[dict] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "full_name": "Jane Smith",
                "timezone": "Europe/London",
                "preferences": {
                    "theme": "light",
                    "language": "en"
                }
            }
        }
    )


class UserResponse(UserBase):
    """Schema for user data in API responses."""

    id: UUID = Field(..., description="User's unique identifier")
    subscription_tier: str = Field(..., description="Current subscription tier (free/premium/pro)")
    subscription_expires_at: Optional[datetime] = Field(None, description="Subscription expiration timestamp")
    is_active: bool = Field(..., description="Whether the user account is active")
    is_teacher: bool = Field(..., description="Whether the user has teacher privileges")
    last_active_at: Optional[datetime] = Field(None, description="Last activity timestamp")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    is_premium: bool = Field(..., description="Computed: whether user has active premium subscription")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "student@example.com",
                "full_name": "Jane Doe",
                "subscription_tier": "premium",
                "subscription_expires_at": "2026-12-31T23:59:59Z",
                "timezone": "America/New_York",
                "preferences": {"theme": "dark"},
                "is_active": True,
                "last_active_at": "2026-01-24T19:30:00Z",
                "created_at": "2026-01-01T10:00:00Z",
                "updated_at": "2026-01-24T19:30:00Z",
                "is_premium": True
            }
        }
    )


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "student@example.com",
                "password": "SecurePass123!"
            }
        }
    )


class Token(BaseModel):
    """Schema for JWT token response."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration time in seconds")
    user: UserResponse = Field(..., description="Authenticated user data")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 2592000,
                "user": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "email": "student@example.com",
                    "subscription_tier": "free",
                    "is_premium": False
                }
            }
        }
    )


class TokenRefresh(BaseModel):
    """Schema for refreshing access token."""

    refresh_token: str = Field(..., description="JWT refresh token")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }
    )
