"""Request schemas for the Structured Prompt Service API."""

from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, field_validator


class OutputFormat(str, Enum):
    """Supported output formats for structured data."""

    JSON = "json"
    XML = "xml"


class LLMProvider(str, Enum):
    """Supported LLM providers."""

    GEMINI = "gemini"
    CLAUDE = "claude"
    GPT4 = "gpt-4"
    AUTO = "auto"  # Automatic provider selection


class AnalyzeRequest(BaseModel):
    """
    Request schema for the /v1/analyze endpoint.

    This endpoint accepts a natural language prompt and extracts structured
    information including intent, subject, entities, and language detection.
    """

    prompt: str = Field(
        ...,
        description="Natural language prompt to analyze and structure",
        min_length=1,
        max_length=10000,
        examples=[
            "Translate 'Bonjour le monde' to English",
            "Create a JSON schema for a user profile with name, email, and age",
            "Analyze the sentiment of this product review: 'Best phone ever!'",
        ],
    )

    output_format: OutputFormat = Field(
        default=OutputFormat.JSON,
        description="Desired output format (json or xml)",
        examples=["json", "xml"],
    )

    schema_definition: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional JSON Schema to validate the structured output against",
        examples=[
            {
                "type": "object",
                "properties": {
                    "intent": {"type": "string"},
                    "subject": {"type": "string"},
                    "entities": {"type": "object"},
                },
                "required": ["intent", "subject"],
            }
        ],
    )

    llm_provider: LLMProvider = Field(
        default=LLMProvider.AUTO,
        description="LLM provider to use (auto, gemini, claude, gpt-4)",
        examples=["auto", "gemini", "claude"],
    )

    temperature: Optional[float] = Field(
        default=0.1,
        ge=0.0,
        le=2.0,
        description="LLM temperature for response randomness (0.0-2.0)",
        examples=[0.1, 0.7, 1.0],
    )

    max_tokens: Optional[int] = Field(
        default=2000,
        ge=50,
        le=8000,
        description="Maximum tokens in LLM response",
        examples=[1000, 2000, 4000],
    )

    cache_ttl: Optional[int] = Field(
        default=3600,
        ge=0,
        le=86400,
        description="Cache TTL in seconds (0 to disable caching)",
        examples=[0, 300, 3600],
    )

    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional metadata to attach to the request for logging/tracking",
        examples=[{"user_id": "123", "session_id": "abc", "source": "web_app"}],
    )

    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, v: str) -> str:
        """Validate prompt is not empty after stripping whitespace."""
        stripped = v.strip()
        if not stripped:
            raise ValueError("Prompt cannot be empty or only whitespace")
        return stripped

    @field_validator("schema_definition")
    @classmethod
    def validate_schema_definition(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Validate schema_definition is a valid JSON Schema structure."""
        if v is not None:
            # Basic validation - must have a 'type' field
            if "type" not in v:
                raise ValueError("schema_definition must contain a 'type' field")

            # Validate type is a supported JSON Schema type
            valid_types = ["object", "array", "string", "number", "integer", "boolean", "null"]
            if v["type"] not in valid_types:
                raise ValueError(f"schema_definition type must be one of {valid_types}")

        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "prompt": "Translate 'Bonjour le monde' to English",
                    "output_format": "json",
                    "llm_provider": "gemini",
                    "temperature": 0.1,
                },
                {
                    "prompt": "Create a user profile for John Doe, age 30, email john@example.com",
                    "output_format": "json",
                    "schema_definition": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "age": {"type": "integer"},
                            "email": {"type": "string", "format": "email"},
                        },
                        "required": ["name", "email"],
                    },
                    "llm_provider": "auto",
                },
            ]
        }
    }
