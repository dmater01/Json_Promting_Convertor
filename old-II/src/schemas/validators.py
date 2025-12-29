"""Custom validators and validation utilities for schema models."""

import re
from typing import Any, Dict

import jsonschema


def validate_json_schema(schema: Dict[str, Any]) -> bool:
    """
    Validate that a dictionary is a valid JSON Schema.

    Args:
        schema: Dictionary to validate as JSON Schema

    Returns:
        True if valid JSON Schema

    Raises:
        ValueError: If schema is invalid
    """
    try:
        # Use jsonschema's Draft7Validator to check schema validity
        jsonschema.Draft7Validator.check_schema(schema)
        return True
    except jsonschema.SchemaError as e:
        raise ValueError(f"Invalid JSON Schema: {e.message}")


def validate_language_code(code: str) -> bool:
    """
    Validate ISO 639-1 language code format.

    Args:
        code: Language code to validate (e.g., 'en', 'fr', 'es')

    Returns:
        True if valid format

    Raises:
        ValueError: If code is invalid
    """
    # ISO 639-1 codes are exactly 2 lowercase letters
    pattern = r"^[a-z]{2}$"
    if not re.match(pattern, code):
        raise ValueError(f"Invalid ISO 639-1 language code: {code}. Must be 2 lowercase letters.")
    return True


def validate_prompt_content(prompt: str) -> str:
    """
    Validate and sanitize prompt content.

    Args:
        prompt: Raw prompt text

    Returns:
        Sanitized prompt text

    Raises:
        ValueError: If prompt is invalid
    """
    # Strip whitespace
    cleaned = prompt.strip()

    # Check not empty
    if not cleaned:
        raise ValueError("Prompt cannot be empty or only whitespace")

    # Check length constraints
    if len(cleaned) < 1:
        raise ValueError("Prompt must be at least 1 character")

    if len(cleaned) > 10000:
        raise ValueError("Prompt must be at most 10,000 characters")

    # Check for potential injection attacks (basic check)
    suspicious_patterns = [
        r"<script[^>]*>",  # Script tags
        r"javascript:",  # JavaScript protocol
        r"on\w+\s*=",  # Event handlers
    ]

    for pattern in suspicious_patterns:
        if re.search(pattern, cleaned, re.IGNORECASE):
            raise ValueError("Prompt contains potentially malicious content")

    return cleaned


def validate_temperature(temp: float) -> bool:
    """
    Validate LLM temperature parameter.

    Args:
        temp: Temperature value

    Returns:
        True if valid

    Raises:
        ValueError: If temperature is out of range
    """
    if not 0.0 <= temp <= 2.0:
        raise ValueError(f"Temperature must be between 0.0 and 2.0, got {temp}")
    return True


def validate_max_tokens(tokens: int) -> bool:
    """
    Validate max_tokens parameter.

    Args:
        tokens: Maximum tokens value

    Returns:
        True if valid

    Raises:
        ValueError: If max_tokens is out of range
    """
    if not 50 <= tokens <= 8000:
        raise ValueError(f"max_tokens must be between 50 and 8000, got {tokens}")
    return True


def validate_cache_ttl(ttl: int) -> bool:
    """
    Validate cache TTL parameter.

    Args:
        ttl: Cache TTL in seconds

    Returns:
        True if valid

    Raises:
        ValueError: If TTL is out of range
    """
    if not 0 <= ttl <= 86400:  # 0 to 24 hours
        raise ValueError(f"cache_ttl must be between 0 and 86400 seconds, got {ttl}")
    return True


def validate_metadata(metadata: Dict[str, Any]) -> bool:
    """
    Validate metadata dictionary.

    Args:
        metadata: Metadata dictionary

    Returns:
        True if valid

    Raises:
        ValueError: If metadata is invalid
    """
    # Check max size (prevent abuse)
    max_metadata_keys = 20
    if len(metadata) > max_metadata_keys:
        raise ValueError(f"Metadata cannot have more than {max_metadata_keys} keys")

    # Check key names (alphanumeric + underscore)
    key_pattern = r"^[a-zA-Z0-9_]+$"
    for key in metadata.keys():
        if not re.match(key_pattern, key):
            raise ValueError(f"Invalid metadata key: {key}. Must be alphanumeric with underscores.")

        # Check key length
        if len(key) > 50:
            raise ValueError(f"Metadata key too long: {key}. Max 50 characters.")

    return True


class ValidationError(Exception):
    """Custom validation error for schema validation."""

    def __init__(self, field: str, message: str, details: Dict[str, Any] = None):
        self.field = field
        self.message = message
        self.details = details or {}
        super().__init__(f"{field}: {message}")
