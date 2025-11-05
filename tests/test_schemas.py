"""Tests for Pydantic schema models."""

import pytest
from datetime import datetime

from src.schemas.requests import AnalyzeRequest, LLMProvider, OutputFormat
from src.schemas.responses import (
    AnalyzeResponse,
    ErrorDetail,
    ErrorResponse,
    StructuredData,
)


class TestAnalyzeRequest:
    """Tests for AnalyzeRequest schema."""

    def test_minimal_valid_request(self):
        """Test minimal valid request with defaults."""
        request = AnalyzeRequest(prompt="Translate 'hello' to French")

        assert request.prompt == "Translate 'hello' to French"
        assert request.output_format == OutputFormat.JSON
        assert request.llm_provider == LLMProvider.AUTO
        assert request.temperature == 0.1
        assert request.max_tokens == 2000
        assert request.cache_ttl == 3600
        assert request.schema_definition is None
        assert request.metadata is None

    def test_full_valid_request(self):
        """Test fully populated valid request."""
        schema = {
            "type": "object",
            "properties": {
                "intent": {"type": "string"},
                "subject": {"type": "string"},
            },
            "required": ["intent"],
        }

        request = AnalyzeRequest(
            prompt="Create a user profile",
            output_format=OutputFormat.JSON,
            schema_definition=schema,
            llm_provider=LLMProvider.GEMINI,
            temperature=0.7,
            max_tokens=1000,
            cache_ttl=300,
            metadata={"user_id": "123", "source": "web"},
        )

        assert request.prompt == "Create a user profile"
        assert request.output_format == OutputFormat.JSON
        assert request.schema_definition == schema
        assert request.llm_provider == LLMProvider.GEMINI
        assert request.temperature == 0.7
        assert request.max_tokens == 1000
        assert request.cache_ttl == 300
        assert request.metadata == {"user_id": "123", "source": "web"}

    def test_prompt_whitespace_stripping(self):
        """Test that prompt whitespace is stripped."""
        request = AnalyzeRequest(prompt="  hello world  ")
        assert request.prompt == "hello world"

    def test_empty_prompt_validation(self):
        """Test that empty prompts are rejected."""
        with pytest.raises(ValueError, match="Prompt cannot be empty"):
            AnalyzeRequest(prompt="   ")

    def test_invalid_schema_definition(self):
        """Test that invalid JSON schema is rejected."""
        with pytest.raises(ValueError, match="schema_definition must contain a 'type' field"):
            AnalyzeRequest(
                prompt="test",
                schema_definition={"invalid": "schema"},
            )

    def test_invalid_schema_type(self):
        """Test that invalid schema type is rejected."""
        with pytest.raises(ValueError, match="type must be one of"):
            AnalyzeRequest(
                prompt="test",
                schema_definition={"type": "invalid_type"},
            )

    def test_temperature_range_validation(self):
        """Test temperature bounds validation."""
        # Valid temperatures
        AnalyzeRequest(prompt="test", temperature=0.0)
        AnalyzeRequest(prompt="test", temperature=1.0)
        AnalyzeRequest(prompt="test", temperature=2.0)

        # Invalid temperatures
        with pytest.raises(ValueError):
            AnalyzeRequest(prompt="test", temperature=-0.1)

        with pytest.raises(ValueError):
            AnalyzeRequest(prompt="test", temperature=2.1)

    def test_max_tokens_range_validation(self):
        """Test max_tokens bounds validation."""
        # Valid max_tokens
        AnalyzeRequest(prompt="test", max_tokens=50)
        AnalyzeRequest(prompt="test", max_tokens=8000)

        # Invalid max_tokens
        with pytest.raises(ValueError):
            AnalyzeRequest(prompt="test", max_tokens=49)

        with pytest.raises(ValueError):
            AnalyzeRequest(prompt="test", max_tokens=8001)

    def test_cache_ttl_range_validation(self):
        """Test cache_ttl bounds validation."""
        # Valid cache_ttl
        AnalyzeRequest(prompt="test", cache_ttl=0)  # Caching disabled
        AnalyzeRequest(prompt="test", cache_ttl=86400)  # 24 hours

        # Invalid cache_ttl
        with pytest.raises(ValueError):
            AnalyzeRequest(prompt="test", cache_ttl=-1)

        with pytest.raises(ValueError):
            AnalyzeRequest(prompt="test", cache_ttl=86401)


class TestStructuredData:
    """Tests for StructuredData schema."""

    def test_minimal_valid_data(self):
        """Test minimal valid structured data."""
        data = StructuredData(
            intent="translate",
            subject="text",
        )

        assert data.intent == "translate"
        assert data.subject == "text"
        assert data.entities == {}
        assert data.output_format is None
        assert data.original_language is None
        assert data.confidence_score is None

    def test_full_valid_data(self):
        """Test fully populated structured data."""
        data = StructuredData(
            intent="translate",
            subject="text",
            entities={"source": "Bonjour", "target": "English"},
            output_format="JSON",
            original_language="fr",
            confidence_score=0.95,
        )

        assert data.intent == "translate"
        assert data.subject == "text"
        assert data.entities == {"source": "Bonjour", "target": "English"}
        assert data.output_format == "JSON"
        assert data.original_language == "fr"
        assert data.confidence_score == 0.95

    def test_confidence_score_range(self):
        """Test confidence score bounds validation."""
        # Valid scores
        StructuredData(intent="test", subject="test", confidence_score=0.0)
        StructuredData(intent="test", subject="test", confidence_score=0.5)
        StructuredData(intent="test", subject="test", confidence_score=1.0)

        # Invalid scores
        with pytest.raises(ValueError):
            StructuredData(intent="test", subject="test", confidence_score=-0.1)

        with pytest.raises(ValueError):
            StructuredData(intent="test", subject="test", confidence_score=1.1)


class TestAnalyzeResponse:
    """Tests for AnalyzeResponse schema."""

    def test_valid_response(self):
        """Test valid analyze response."""
        data = StructuredData(
            intent="translate",
            subject="text",
            entities={"source": "Bonjour"},
            original_language="fr",
        )

        response = AnalyzeResponse(
            request_id="123e4567-e89b-12d3-a456-426614174000",
            data=data,
            llm_provider="gemini",
            model_name="gemini-pro-latest",
            tokens_used=150,
            latency_ms=234,
            cached=False,
            validated=True,
        )

        assert response.request_id == "123e4567-e89b-12d3-a456-426614174000"
        assert response.data.intent == "translate"
        assert response.llm_provider == "gemini"
        assert response.model_name == "gemini-pro-latest"
        assert response.tokens_used == 150
        assert response.latency_ms == 234
        assert response.cached is False
        assert response.validated is True
        assert isinstance(response.timestamp, datetime)

    def test_response_with_raw_output(self):
        """Test response with raw LLM output included."""
        data = StructuredData(intent="test", subject="test")

        response = AnalyzeResponse(
            request_id="test-123",
            data=data,
            raw_output='{"intent": "test", "subject": "test"}',
            llm_provider="gemini",
            model_name="gemini-pro",
            latency_ms=100,
        )

        assert response.raw_output == '{"intent": "test", "subject": "test"}'

    def test_cached_response(self):
        """Test cached response flag."""
        data = StructuredData(intent="test", subject="test")

        response = AnalyzeResponse(
            request_id="test-123",
            data=data,
            llm_provider="gemini",
            model_name="gemini-pro",
            latency_ms=10,  # Low latency from cache
            cached=True,
            validated=True,
        )

        assert response.cached is True
        assert response.latency_ms == 10


class TestErrorResponse:
    """Tests for ErrorResponse schema."""

    def test_validation_error(self):
        """Test validation error response."""
        error = ErrorResponse(
            error=ErrorDetail(
                type="validation_error",
                message="Prompt cannot be empty",
                field="prompt",
            ),
            request_id="test-123",
        )

        assert error.error.type == "validation_error"
        assert error.error.message == "Prompt cannot be empty"
        assert error.error.field == "prompt"
        assert error.request_id == "test-123"
        assert isinstance(error.timestamp, datetime)

    def test_llm_error(self):
        """Test LLM provider error response."""
        error = ErrorResponse(
            error=ErrorDetail(
                type="llm_error",
                message="Gemini API unavailable",
                details={"provider": "gemini", "status_code": 503},
            ),
            request_id="test-456",
        )

        assert error.error.type == "llm_error"
        assert error.error.message == "Gemini API unavailable"
        assert error.error.details["provider"] == "gemini"
        assert error.error.details["status_code"] == 503

    def test_rate_limit_error(self):
        """Test rate limit error response."""
        error = ErrorResponse(
            error=ErrorDetail(
                type="rate_limit_exceeded",
                message="Rate limit exceeded: 1000 requests per hour",
                details={
                    "limit": 1000,
                    "remaining": 0,
                    "reset_at": "2024-01-15T11:00:00Z",
                },
            ),
            request_id="test-789",
        )

        assert error.error.type == "rate_limit_exceeded"
        assert error.error.details["limit"] == 1000
        assert error.error.details["remaining"] == 0


class TestEnums:
    """Tests for enum types."""

    def test_output_format_enum(self):
        """Test OutputFormat enum values."""
        assert OutputFormat.JSON == "json"
        assert OutputFormat.XML == "xml"
        assert len(OutputFormat) == 2

    def test_llm_provider_enum(self):
        """Test LLMProvider enum values."""
        assert LLMProvider.GEMINI == "gemini"
        assert LLMProvider.CLAUDE == "claude"
        assert LLMProvider.GPT4 == "gpt-4"
        assert LLMProvider.AUTO == "auto"
        assert len(LLMProvider) == 4


# Example test data for manual testing
EXAMPLE_REQUESTS = [
    {
        "prompt": "Translate 'Bonjour le monde' to English",
        "output_format": "json",
        "llm_provider": "gemini",
    },
    {
        "prompt": "Create a JSON schema for a user with name, email, and age",
        "output_format": "json",
        "llm_provider": "auto",
        "temperature": 0.3,
    },
    {
        "prompt": "Analyze sentiment: 'This product is amazing!'",
        "output_format": "json",
        "metadata": {"source": "product_reviews", "product_id": "P123"},
    },
]
