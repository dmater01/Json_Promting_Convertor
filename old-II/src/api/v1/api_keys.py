"""API key management endpoints."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.db_client import get_db_session
from src.core.logging_config import get_logger
from src.models.database import APIKey
from src.schemas.api_keys import (
    APIKeyCreate,
    APIKeyCreatedResponse,
    APIKeyListResponse,
    APIKeyResponse,
    APIKeyRevokeResponse,
)
from src.services.api_key_service import APIKeyService

logger = get_logger(__name__)

router = APIRouter()


@router.post(
    "/",
    response_model=APIKeyCreatedResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new API key",
    description="""
    Create a new API key for authenticating requests.

    **IMPORTANT**: The actual API key is only returned once during creation.
    Store it securely - it cannot be retrieved later.

    The API key will be in the format: `sp_<64_hex_characters>`
    """,
)
async def create_api_key(
    key_data: APIKeyCreate,
    db: AsyncSession = Depends(get_db_session),
) -> APIKeyCreatedResponse:
    """
    Create a new API key.

    Args:
        key_data: API key creation parameters
        db: Database session

    Returns:
        Created API key with the raw key (only shown once)
    """
    logger.info(
        "Creating API key",
        extra={
            "key_name": key_data.name,
            "team": key_data.team,
            "rate_limit": key_data.rate_limit_per_hour,
        },
    )

    service = APIKeyService(db)
    created_key, raw_key = await service.create_key(
        name=key_data.name,
        team=key_data.team,
        rate_limit_per_hour=key_data.rate_limit_per_hour,
        expires_in_days=key_data.expires_in_days,
    )

    return APIKeyCreatedResponse(
        api_key=raw_key,
        key_info=APIKeyResponse.model_validate(created_key),
    )


@router.get(
    "/",
    response_model=APIKeyListResponse,
    summary="List all API keys",
    description="Retrieve a list of all API keys with pagination support.",
)
async def list_api_keys(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db_session),
) -> APIKeyListResponse:
    """
    List all API keys.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session

    Returns:
        List of API keys
    """
    service = APIKeyService(db)
    keys = await service.list_keys(skip=skip, limit=limit)

    return APIKeyListResponse(
        keys=[APIKeyResponse.model_validate(k) for k in keys],
        total=len(keys),
    )


@router.get(
    "/{key_id}",
    response_model=APIKeyResponse,
    summary="Get API key by ID",
    description="Retrieve details of a specific API key by its UUID.",
)
async def get_api_key(
    key_id: UUID,
    db: AsyncSession = Depends(get_db_session),
) -> APIKeyResponse:
    """
    Get API key by ID.

    Args:
        key_id: UUID of the API key
        db: Database session

    Returns:
        API key details

    Raises:
        HTTPException: If key not found
    """
    service = APIKeyService(db)
    api_key = await service.get_key(key_id)

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"API key with ID {key_id} not found",
        )

    return APIKeyResponse.model_validate(api_key)


@router.delete(
    "/{key_id}",
    response_model=APIKeyRevokeResponse,
    summary="Revoke an API key",
    description="""
    Revoke (deactivate) an API key.

    This is a soft delete - the key record remains in the database but can no longer be used.
    Use this instead of hard delete to maintain audit trails.
    """,
)
async def revoke_api_key(
    key_id: UUID,
    db: AsyncSession = Depends(get_db_session),
) -> APIKeyRevokeResponse:
    """
    Revoke an API key.

    Args:
        key_id: UUID of the API key to revoke
        db: Database session

    Returns:
        Revocation status

    Raises:
        HTTPException: If key not found
    """
    service = APIKeyService(db)
    success = await service.revoke_key(key_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"API key with ID {key_id} not found",
        )

    logger.info("API key revoked", extra={"key_id": str(key_id)})

    return APIKeyRevokeResponse(
        success=True,
        message=f"API key {key_id} has been revoked",
    )


@router.post(
    "/{key_id}/activate",
    response_model=APIKeyResponse,
    summary="Reactivate an API key",
    description="Reactivate a previously revoked API key.",
)
async def activate_api_key(
    key_id: UUID,
    db: AsyncSession = Depends(get_db_session),
) -> APIKeyResponse:
    """
    Reactivate an API key.

    Args:
        key_id: UUID of the API key to reactivate
        db: Database session

    Returns:
        Updated API key

    Raises:
        HTTPException: If key not found
    """
    service = APIKeyService(db)
    api_key = await service.get_key(key_id)

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"API key with ID {key_id} not found",
        )

    # Reactivate the key
    api_key.is_active = True
    await service.repo.update(api_key)
    await db.commit()

    logger.info("API key reactivated", extra={"key_id": str(key_id)})

    return APIKeyResponse.model_validate(api_key)
