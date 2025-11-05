"""Exception handlers for API errors."""

from datetime import datetime

from fastapi import Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from src.core.exceptions import (
    LLMAuthenticationError,
    LLMException,
    LLMProviderUnavailableError,
    LLMRateLimitError,
    RateLimitExceededError,
    SchemaValidationError,
    ServiceException,
    ValidationError as CustomValidationError,
)
from src.core.logging_config import get_logger
from src.schemas.responses import ErrorDetail, ErrorResponse

logger = get_logger(__name__)


def create_error_response(
    error_type: str,
    message: str,
    request_id: str,
    field: str = None,
    details: dict = None,
    status_code: int = 500,
) -> JSONResponse:
    """
    Create a standardized error response.

    Args:
        error_type: Error type identifier
        message: Human-readable error message
        request_id: Request ID
        field: Field name for validation errors
        details: Additional error details
        status_code: HTTP status code

    Returns:
        JSONResponse with error details
    """
    error_response = ErrorResponse(
        error=ErrorDetail(
            type=error_type,
            message=message,
            field=field,
            details=details,
        ),
        request_id=request_id,
        timestamp=datetime.utcnow(),
    )

    return JSONResponse(
        status_code=status_code,
        content=error_response.model_dump(mode="json"),
    )


async def llm_exception_handler(request: Request, exc: LLMException) -> JSONResponse:
    """Handle LLM-related exceptions."""
    request_id = getattr(request.state, "request_id", "unknown")

    logger.error(
        "LLM error",
        extra={
            "request_id": request_id,
            "error_type": exc.error_type,
            "provider": exc.provider,
            "error_message": exc.message,
        },
    )

    # Map LLM errors to HTTP status codes
    if isinstance(exc, LLMAuthenticationError):
        status_code = status.HTTP_401_UNAUTHORIZED
    elif isinstance(exc, LLMRateLimitError):
        status_code = status.HTTP_429_TOO_MANY_REQUESTS
    elif isinstance(exc, LLMProviderUnavailableError):
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    else:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    return create_error_response(
        error_type=exc.error_type,
        message=exc.message,
        request_id=request_id,
        details=exc.details,
        status_code=status_code,
    )


async def schema_validation_exception_handler(
    request: Request, exc: SchemaValidationError
) -> JSONResponse:
    """Handle schema validation exceptions."""
    request_id = getattr(request.state, "request_id", "unknown")

    logger.warning(
        "Schema validation error",
        extra={
            "request_id": request_id,
            "error_message": exc.message,
            "field": exc.field,
        },
    )

    return create_error_response(
        error_type="schema_validation_error",
        message=exc.message,
        request_id=request_id,
        field=exc.field,
        details=exc.details,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


async def rate_limit_exception_handler(
    request: Request, exc: RateLimitExceededError
) -> JSONResponse:
    """Handle rate limit exceptions."""
    request_id = getattr(request.state, "request_id", "unknown")

    logger.warning(
        "Rate limit exceeded",
        extra={
            "request_id": request_id,
            "error_message": exc.message,
        },
    )

    response = create_error_response(
        error_type="rate_limit_exceeded",
        message=exc.message,
        request_id=request_id,
        details=exc.details,
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
    )

    # Add Retry-After header if reset_at is available
    if exc.details and "reset_at" in exc.details:
        from datetime import datetime
        try:
            reset_at = datetime.fromisoformat(exc.details["reset_at"])
            retry_after = int((reset_at - datetime.utcnow()).total_seconds())
            response.headers["Retry-After"] = str(max(0, retry_after))
        except (ValueError, TypeError):
            pass

    # Add rate limit headers
    if exc.details:
        if "limit" in exc.details:
            response.headers["X-RateLimit-Limit"] = str(exc.details["limit"])
        if "remaining" in exc.details:
            response.headers["X-RateLimit-Remaining"] = str(exc.details["remaining"])

    return response


async def validation_exception_handler(
    request: Request, exc: ValidationError
) -> JSONResponse:
    """Handle Pydantic validation exceptions."""
    request_id = getattr(request.state, "request_id", "unknown")

    # Extract validation errors
    errors = []
    for error in exc.errors():
        field = ".".join(str(x) for x in error["loc"])
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"],
        })

    logger.warning(
        "Request validation error",
        extra={
            "request_id": request_id,
            "error_count": len(errors),
            "errors": errors[:3],  # First 3 errors
        },
    )

    # Format error message
    if len(errors) == 1:
        message = f"{errors[0]['field']}: {errors[0]['message']}"
        field = errors[0]["field"]
    else:
        message = f"Validation failed for {len(errors)} field(s)"
        field = None

    return create_error_response(
        error_type="validation_error",
        message=message,
        request_id=request_id,
        field=field,
        details={"errors": errors},
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


async def service_exception_handler(
    request: Request, exc: ServiceException
) -> JSONResponse:
    """Handle general service exceptions."""
    request_id = getattr(request.state, "request_id", "unknown")

    logger.error(
        "Service error",
        extra={
            "request_id": request_id,
            "error_type": exc.error_type,
            "error_message": exc.message,
        },
    )

    return create_error_response(
        error_type=exc.error_type,
        message=exc.message,
        request_id=request_id,
        details=exc.details,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    request_id = getattr(request.state, "request_id", "unknown")

    logger.error(
        "Unexpected error",
        extra={
            "request_id": request_id,
            "error_type": type(exc).__name__,
            "error": str(exc),
        },
        exc_info=True,
    )

    return create_error_response(
        error_type="internal_error",
        message="An unexpected error occurred",
        request_id=request_id,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def register_exception_handlers(app):
    """
    Register all exception handlers with the FastAPI app.

    Args:
        app: FastAPI application instance
    """
    # LLM exceptions
    app.add_exception_handler(LLMException, llm_exception_handler)

    # Validation exceptions
    app.add_exception_handler(SchemaValidationError, schema_validation_exception_handler)
    app.add_exception_handler(ValidationError, validation_exception_handler)

    # Rate limiting
    app.add_exception_handler(RateLimitExceededError, rate_limit_exception_handler)

    # Service exceptions
    app.add_exception_handler(ServiceException, service_exception_handler)

    # Catch-all for unexpected errors
    app.add_exception_handler(Exception, generic_exception_handler)

    logger.info("Exception handlers registered")
