"""Authentication dependencies for FastAPI endpoints."""

from typing import Optional

from fastapi import Header, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.cache_client import get_cache_client
from src.adapters.db_client import get_db_session
from src.core.exceptions import AuthenticationError, RateLimitExceededError
from src.core.logging_config import get_logger
from src.models.database import APIKey
from src.services.api_key_service import APIKeyService
from src.services.rate_limiter import RateLimiter

logger = get_logger(__name__)

# Security scheme for Swagger UI
security = HTTPBearer(
    scheme_name="API Key Authentication",
    description="Use your API key in the format: `Bearer sp_your_api_key_here`",
)


async def get_api_key_from_header(
    authorization: Optional[str] = Header(None),
) -> str:
    """
    Extract API key from Authorization header.

    Supports two formats:
    1. Bearer token: "Authorization: Bearer sp_..."
    2. Direct key: "Authorization: sp_..."

    Args:
        authorization: Authorization header value

    Returns:
        Raw API key string

    Raises:
        HTTPException: If authorization header is missing or invalid
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Handle "Bearer <key>" format
    if authorization.lower().startswith("bearer "):
        api_key = authorization[7:].strip()  # Remove "Bearer " prefix
    else:
        # Handle direct key format
        api_key = authorization.strip()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return api_key


async def get_current_api_key(
    api_key: str = Header(None, alias="X-API-Key"),
    authorization: Optional[str] = Header(None),
    db: AsyncSession = None,
) -> APIKey:
    """
    Validate API key and return the associated APIKey record.

    Supports two authentication methods:
    1. X-API-Key header: "X-API-Key: sp_..."
    2. Authorization header: "Authorization: Bearer sp_..."

    Args:
        api_key: API key from X-API-Key header
        authorization: API key from Authorization header
        db: Database session (injected)

    Returns:
        APIKey instance if valid

    Raises:
        HTTPException: If authentication fails
    """
    # Get database session if not provided
    if db is None:
        async for session in get_db_session():
            db = session
            break

    # Try X-API-Key header first
    raw_key = api_key

    # Fall back to Authorization header
    if not raw_key and authorization:
        raw_key = await get_api_key_from_header(authorization)

    if not raw_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Provide via X-API-Key or Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Validate key
    service = APIKeyService(db)
    try:
        validated_key = await service.validate_key(raw_key)
        return validated_key
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


async def require_api_key(
    request: Request,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    authorization: Optional[str] = Header(None),
) -> APIKey:
    """
    FastAPI dependency that requires valid API key authentication and checks rate limits.

    Use this in route dependencies to protect endpoints.

    Example:
        @app.get("/protected")
        async def protected_route(
            api_key: APIKey = Depends(require_api_key)
        ):
            return {"message": f"Hello {api_key.name}"}

    Args:
        request: FastAPI request object
        x_api_key: X-API-Key header
        authorization: Authorization header

    Returns:
        Validated APIKey instance

    Raises:
        HTTPException: If authentication fails
        RateLimitExceededError: If rate limit is exceeded
    """
    async for db in get_db_session():
        # Authenticate user
        api_key = await get_current_api_key(
            api_key=x_api_key,
            authorization=authorization,
            db=db,
        )

        # Check rate limit
        try:
            cache_client = await get_cache_client()
            rate_limiter = RateLimiter(cache_client._client)

            # Check if request is allowed
            allowed, remaining, reset_timestamp = await rate_limiter.check_rate_limit(
                api_key_id=api_key.id,
                limit=api_key.rate_limit_per_hour,
            )

            # Record the request
            await rate_limiter.record_request(api_key.id)

            # Store rate limit info in request state for response headers
            request.state.rate_limit_info = {
                "limit": api_key.rate_limit_per_hour,
                "remaining": remaining - 1,  # -1 for current request
                "reset": reset_timestamp,
            }

            logger.debug(
                "Rate limit check passed",
                extra={
                    "api_key_id": str(api_key.id),
                    "remaining": remaining - 1,
                    "limit": api_key.rate_limit_per_hour,
                },
            )

        except RateLimitExceededError:
            # Re-raise to be caught by exception handler
            raise
        except Exception as e:
            # Log error but don't block request if rate limiting fails
            logger.error(
                "Rate limiting error - allowing request",
                extra={"error": str(e), "api_key_id": str(api_key.id)},
            )

        return api_key


async def optional_api_key(
    authorization: Optional[str] = Header(None),
) -> Optional[APIKey]:
    """
    FastAPI dependency for optional API key authentication.

    Returns None if no API key is provided, validates if present.

    Args:
        authorization: Authorization header

    Returns:
        APIKey if provided and valid, None otherwise
    """
    if not authorization:
        return None

    try:
        return await require_api_key(authorization)
    except HTTPException:
        return None
