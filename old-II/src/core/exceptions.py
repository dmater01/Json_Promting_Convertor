"""Custom exceptions for the Structured Prompt Service."""

from typing import Any, Dict, Optional


class ServiceException(Exception):
    """Base exception for all service errors."""

    def __init__(
        self,
        message: str,
        error_type: str = "service_error",
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.error_type = error_type
        self.details = details or {}
        super().__init__(self.message)


class LLMException(ServiceException):
    """Base exception for LLM-related errors."""

    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        error_type: str = "llm_error",
        details: Optional[Dict[str, Any]] = None,
    ):
        details = details or {}
        if provider:
            details["provider"] = provider
        if model:
            details["model"] = model
        super().__init__(message, error_type, details)
        self.provider = provider
        self.model = model


class LLMProviderUnavailableError(LLMException):
    """Raised when an LLM provider is unavailable or returns 5xx errors."""

    def __init__(
        self,
        provider: str,
        message: Optional[str] = None,
        status_code: Optional[int] = None,
        retry_after: Optional[int] = None,
    ):
        message = message or f"{provider} API is temporarily unavailable"
        details = {}
        if status_code:
            details["status_code"] = status_code
        if retry_after:
            details["retry_after"] = retry_after
        super().__init__(
            message,
            provider=provider,
            error_type="llm_provider_unavailable",
            details=details,
        )


class LLMRateLimitError(LLMException):
    """Raised when LLM provider rate limits are exceeded."""

    def __init__(
        self,
        provider: str,
        message: Optional[str] = None,
        limit: Optional[int] = None,
        reset_at: Optional[str] = None,
    ):
        message = message or f"{provider} rate limit exceeded"
        details = {}
        if limit:
            details["limit"] = limit
        if reset_at:
            details["reset_at"] = reset_at
        super().__init__(
            message,
            provider=provider,
            error_type="llm_rate_limit_exceeded",
            details=details,
        )


class LLMAuthenticationError(LLMException):
    """Raised when LLM API authentication fails."""

    def __init__(self, provider: str, message: Optional[str] = None):
        message = message or f"{provider} authentication failed - check API key"
        super().__init__(
            message,
            provider=provider,
            error_type="llm_authentication_error",
        )


class LLMInvalidRequestError(LLMException):
    """Raised when the request to the LLM is invalid (4xx errors)."""

    def __init__(
        self,
        provider: str,
        message: str,
        field: Optional[str] = None,
    ):
        details = {}
        if field:
            details["field"] = field
        super().__init__(
            message,
            provider=provider,
            error_type="llm_invalid_request",
            details=details,
        )


class LLMResponseParsingError(LLMException):
    """Raised when LLM response cannot be parsed as valid JSON."""

    def __init__(
        self,
        provider: str,
        raw_response: str,
        parse_error: str,
    ):
        message = f"Failed to parse {provider} response as JSON"
        super().__init__(
            message,
            provider=provider,
            error_type="llm_response_parsing_error",
            details={
                "raw_response": raw_response[:500],  # Truncate for logging
                "parse_error": str(parse_error),
            },
        )


class LLMTimeoutError(LLMException):
    """Raised when LLM request times out."""

    def __init__(
        self,
        provider: str,
        timeout_seconds: int,
    ):
        message = f"{provider} request timed out after {timeout_seconds}s"
        super().__init__(
            message,
            provider=provider,
            error_type="llm_timeout_error",
            details={"timeout_seconds": timeout_seconds},
        )


class SchemaValidationError(ServiceException):
    """Raised when LLM output doesn't match the provided JSON schema."""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        expected: Optional[str] = None,
        received: Optional[str] = None,
    ):
        details = {}
        if expected:
            details["expected"] = expected
        if received:
            details["received"] = received
        super().__init__(
            message,
            error_type="schema_validation_error",
            details=details,
        )
        self.field = field


class CacheError(ServiceException):
    """Raised when cache operations fail."""

    def __init__(self, message: str, operation: str):
        super().__init__(
            message,
            error_type="cache_error",
            details={"operation": operation},
        )


class DatabaseError(ServiceException):
    """Raised when database operations fail."""

    def __init__(self, message: str, operation: Optional[str] = None):
        details = {}
        if operation:
            details["operation"] = operation
        super().__init__(
            message,
            error_type="database_error",
            details=details,
        )


class AuthenticationError(ServiceException):
    """Raised when API key authentication fails."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message,
            error_type="authentication_error",
        )


class RateLimitExceededError(ServiceException):
    """Raised when API key rate limits are exceeded."""

    def __init__(
        self,
        message: str,
        limit: int,
        remaining: int = 0,
        reset_at: Optional[str] = None,
    ):
        details = {
            "limit": limit,
            "remaining": remaining,
        }
        if reset_at:
            details["reset_at"] = reset_at
        super().__init__(
            message,
            error_type="rate_limit_exceeded",
            details=details,
        )


class ValidationError(ServiceException):
    """Raised for request validation errors."""

    def __init__(
        self,
        message: str,
        field: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        details = details or {}
        details["field"] = field
        super().__init__(
            message,
            error_type="validation_error",
            details=details,
        )
        self.field = field


class ConfigurationError(ServiceException):
    """Raised when service configuration is invalid."""

    def __init__(self, message: str, config_key: Optional[str] = None):
        details = {}
        if config_key:
            details["config_key"] = config_key
        super().__init__(
            message,
            error_type="configuration_error",
            details=details,
        )
