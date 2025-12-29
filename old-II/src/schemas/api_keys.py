"""Pydantic schemas for API key management."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class APIKeyCreate(BaseModel):
    """Request schema for creating a new API key."""

    name: str = Field(..., min_length=1, max_length=255, description="Descriptive name for the API key")
    team: Optional[str] = Field(None, max_length=255, description="Team or project name")
    rate_limit_per_hour: int = Field(1000, ge=1, le=100000, description="Hourly request limit")
    expires_in_days: Optional[int] = Field(None, ge=1, le=365, description="Days until expiration (None = no expiration)")


class APIKeyResponse(BaseModel):
    """Response schema for API key information (without the actual key)."""

    id: UUID = Field(..., description="Unique API key identifier")
    name: str = Field(..., description="API key name")
    team: Optional[str] = Field(None, description="Team name")
    rate_limit_per_hour: int = Field(..., description="Hourly rate limit")
    is_active: bool = Field(..., description="Whether the key is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp")

    class Config:
        from_attributes = True


class APIKeyCreatedResponse(BaseModel):
    """Response schema when creating a new API key (includes the actual key)."""

    api_key: str = Field(..., description="The actual API key - SAVE THIS! It will only be shown once")
    key_info: APIKeyResponse = Field(..., description="API key metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "api_key": "sp_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
                "key_info": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "name": "Production API",
                    "team": "backend-team",
                    "rate_limit_per_hour": 1000,
                    "is_active": True,
                    "created_at": "2025-10-15T12:00:00",
                    "expires_at": None,
                },
            }
        }


class APIKeyListResponse(BaseModel):
    """Response schema for listing API keys."""

    keys: list[APIKeyResponse] = Field(..., description="List of API keys")
    total: int = Field(..., description="Total number of keys")


class APIKeyRevokeResponse(BaseModel):
    """Response schema for revoking an API key."""

    success: bool = Field(..., description="Whether the key was revoked")
    message: str = Field(..., description="Status message")
