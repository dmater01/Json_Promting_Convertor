"""Response schemas for the Structured Prompt Service API."""

from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from src.schemas.requests import LLMProvider, OutputFormat


class StructuredData(BaseModel):
    """
    Core structured data extracted from natural language prompts.

    This schema reflects the extraction pattern from the research CLI tools,
    capturing intent, subject, entities, and language information.
    """

    intent: str = Field(
        ...,
        description="Primary action or intent (e.g., 'create', 'translate', 'analyze')",
        examples=["translate", "create", "analyze", "extract"],
    )

    subject: str = Field(
        ...,
        description="Main topic or object of the prompt",
        examples=["text", "user profile", "product review", "database schema"],
    )

    entities: Dict[str, Any] = Field(
        default_factory=dict,
        description="Key-value pairs of extracted entities and details",
        examples=[
            {"source": "Bonjour le monde", "target_language": "English"},
            {"name": "John Doe", "age": 30, "email": "john@example.com"},
        ],
    )

    output_format: Optional[str] = Field(
        default=None,
        description="Desired result format mentioned in the prompt",
        examples=["JSON", "XML", "CSV", "markdown"],
    )

    original_language: Optional[str] = Field(
        default=None,
        description="ISO 639-1 language code of the subject (not instruction language)",
        examples=["en", "fr", "es", "de"],
    )

    confidence_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Confidence score of the extraction (0.0-1.0)",
        examples=[0.95, 0.87, 0.72],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "intent": "translate",
                    "subject": "text",
                    "entities": {
                        "source": "Bonjour le monde",
                        "target_language": "English",
                    },
                    "output_format": "text",
                    "original_language": "fr",
                    "confidence_score": 0.95,
                },
                {
                    "intent": "create",
                    "subject": "user profile",
                    "entities": {
                        "name": "John Doe",
                        "age": 30,
                        "email": "john@example.com",
                    },
                    "output_format": "JSON",
                    "original_language": "en",
                    "confidence_score": 0.92,
                },
            ]
        }
    }


class AnalyzeResponse(BaseModel):
    """
    Response schema for successful /v1/analyze requests.

    Contains the structured data extracted from the prompt, along with
    metadata about the request processing.
    """

    request_id: str = Field(
        ...,
        description="Unique request identifier (UUID)",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
    )

    data: StructuredData = Field(
        ...,
        description="Structured data extracted from the prompt",
    )

    raw_output: Optional[str] = Field(
        default=None,
        description="Raw LLM output (if requested via query parameter)",
        examples=['{"intent": "translate", "subject": "text", ...}'],
    )

    llm_provider: str = Field(
        ...,
        description="LLM provider used for this request",
        examples=["gemini", "claude", "gpt-4"],
    )

    model_name: str = Field(
        ...,
        description="Specific model used (e.g., gemini-pro, claude-3-sonnet)",
        examples=["gemini-pro-latest", "claude-3-sonnet-20240229", "gpt-4-turbo"],
    )

    tokens_used: Optional[int] = Field(
        default=None,
        description="Total tokens used (prompt + completion)",
        examples=[150, 327, 891],
    )

    latency_ms: int = Field(
        ...,
        description="Request processing latency in milliseconds",
        examples=[234, 456, 1203],
    )

    cached: bool = Field(
        default=False,
        description="Whether the response was served from cache",
        examples=[True, False],
    )

    validated: bool = Field(
        default=False,
        description="Whether the output passed schema validation",
        examples=[True, False],
    )

    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Response timestamp (UTC)",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "request_id": "123e4567-e89b-12d3-a456-426614174000",
                    "data": {
                        "intent": "translate",
                        "subject": "text",
                        "entities": {
                            "source": "Bonjour le monde",
                            "target_language": "English",
                        },
                        "output_format": "text",
                        "original_language": "fr",
                        "confidence_score": 0.95,
                    },
                    "llm_provider": "gemini",
                    "model_name": "gemini-pro-latest",
                    "tokens_used": 234,
                    "latency_ms": 456,
                    "cached": False,
                    "validated": True,
                    "timestamp": "2024-01-15T10:30:00Z",
                }
            ]
        }
    }


class ErrorDetail(BaseModel):
    """Detailed error information following RFC 7807 Problem Details."""

    type: str = Field(
        ...,
        description="Error type identifier (URI or slug)",
        examples=["validation_error", "llm_error", "rate_limit_exceeded"],
    )

    message: str = Field(
        ...,
        description="Human-readable error message",
        examples=["Invalid prompt format", "LLM provider unavailable"],
    )

    field: Optional[str] = Field(
        default=None,
        description="Field name for validation errors",
        examples=["prompt", "schema_definition", "temperature"],
    )

    details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional error context",
        examples=[{"expected": "string", "received": "null"}],
    )


class ErrorResponse(BaseModel):
    """
    Error response schema for all API errors.

    Follows a consistent error format across all endpoints for easy
    client-side error handling.
    """

    error: ErrorDetail = Field(
        ...,
        description="Error details",
    )

    request_id: Optional[str] = Field(
        default=None,
        description="Request ID if available",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
    )

    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Error timestamp (UTC)",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "error": {
                        "type": "validation_error",
                        "message": "Prompt cannot be empty or only whitespace",
                        "field": "prompt",
                    },
                    "request_id": "123e4567-e89b-12d3-a456-426614174000",
                    "timestamp": "2024-01-15T10:30:00Z",
                },
                {
                    "error": {
                        "type": "rate_limit_exceeded",
                        "message": "Rate limit exceeded: 1000 requests per hour",
                        "details": {
                            "limit": 1000,
                            "remaining": 0,
                            "reset_at": "2024-01-15T11:00:00Z",
                        },
                    },
                    "request_id": "456e7890-e89b-12d3-a456-426614174001",
                    "timestamp": "2024-01-15T10:45:00Z",
                },
            ]
        }
    }


class BatchAnalyzeRequest(BaseModel):
    """Request schema for batch analysis endpoint (future enhancement)."""

    prompts: list[str] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="List of prompts to analyze in batch",
    )

    output_format: str = Field(
        default="json",
        description="Output format for all results (json or xml)",
    )

    llm_provider: str = Field(
        default="auto",
        description="LLM provider to use for all requests",
    )


class BatchAnalyzeResponse(BaseModel):
    """Response schema for batch analysis endpoint (future enhancement)."""

    batch_id: UUID = Field(
        ...,
        description="Unique batch identifier",
    )

    total: int = Field(
        ...,
        description="Total number of prompts in batch",
    )

    completed: int = Field(
        ...,
        description="Number of completed analyses",
    )

    failed: int = Field(
        ...,
        description="Number of failed analyses",
    )

    results: list[AnalyzeResponse] = Field(
        default_factory=list,
        description="List of analysis results",
    )

    errors: list[ErrorResponse] = Field(
        default_factory=list,
        description="List of errors for failed analyses",
    )
