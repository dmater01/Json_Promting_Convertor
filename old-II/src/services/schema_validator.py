"""Schema validation service for validating LLM outputs."""

from typing import Any, Dict, Optional

import jsonschema
from jsonschema import Draft7Validator

from src.core.exceptions import SchemaValidationError
from src.core.logging_config import get_logger

logger = get_logger(__name__)


class SchemaValidator:
    """
    Validates LLM outputs against JSON schemas.

    Features:
    - JSON Schema Draft 7 validation
    - Custom error messages
    - Validation reporting
    """

    def __init__(self):
        """Initialize the schema validator."""
        pass

    def validate(
        self,
        data: Dict[str, Any],
        schema: Dict[str, Any],
        strict: bool = True,
    ) -> bool:
        """
        Validate data against a JSON schema.

        Args:
            data: Data to validate
            schema: JSON Schema to validate against
            strict: If True, raise exception on validation failure

        Returns:
            True if validation passes

        Raises:
            SchemaValidationError: If validation fails and strict=True
        """
        try:
            # Create validator
            validator = Draft7Validator(schema)

            # Validate
            errors = list(validator.iter_errors(data))

            if errors:
                # Format error messages
                error_messages = []
                for error in errors:
                    field_path = ".".join(str(p) for p in error.path) if error.path else "root"
                    error_messages.append(f"{field_path}: {error.message}")

                error_summary = "; ".join(error_messages[:3])  # First 3 errors
                if len(error_messages) > 3:
                    error_summary += f" (and {len(error_messages) - 3} more errors)"

                logger.warning(
                    "Schema validation failed",
                    extra={
                        "error_count": len(errors),
                        "errors": error_messages[:5],
                    },
                )

                if strict:
                    raise SchemaValidationError(
                        message=f"Schema validation failed: {error_summary}",
                        expected="Data matching provided schema",
                        received=f"{len(errors)} validation error(s)",
                    )

                return False

            logger.debug("Schema validation passed")
            return True

        except jsonschema.SchemaError as e:
            logger.error(
                "Invalid JSON schema",
                extra={"error": str(e)},
            )
            raise SchemaValidationError(
                message=f"Invalid JSON schema: {e.message}",
            )

    def validate_core_schema(self, data: Dict[str, Any]) -> bool:
        """
        Validate data against the core structured data schema.

        This is the default schema used by the prompt builder.

        Args:
            data: Data to validate

        Returns:
            True if validation passes

        Raises:
            SchemaValidationError: If validation fails
        """
        core_schema = {
            "type": "object",
            "properties": {
                "intent": {"type": "string", "minLength": 1},
                "subject": {"type": "string", "minLength": 1},
                "entities": {"type": "object"},
                "output_format": {"type": ["string", "null"]},
                "original_language": {
                    "type": ["string", "null"],
                    "pattern": "^[a-z]{2}$",  # ISO 639-1
                },
                "confidence_score": {
                    "type": ["number", "null"],
                    "minimum": 0.0,
                    "maximum": 1.0,
                },
            },
            "required": ["intent", "subject"],
            "additionalProperties": True,
        }

        return self.validate(data, core_schema, strict=True)

    def validate_partial(
        self,
        data: Dict[str, Any],
        schema: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Validate data and return validation report.

        Args:
            data: Data to validate
            schema: JSON Schema

        Returns:
            Validation report dictionary
        """
        try:
            validator = Draft7Validator(schema)
            errors = list(validator.iter_errors(data))

            if not errors:
                return {
                    "valid": True,
                    "error_count": 0,
                    "errors": [],
                }

            error_details = []
            for error in errors:
                field_path = ".".join(str(p) for p in error.path) if error.path else "root"
                error_details.append({
                    "field": field_path,
                    "message": error.message,
                    "validator": error.validator,
                })

            return {
                "valid": False,
                "error_count": len(errors),
                "errors": error_details,
            }

        except jsonschema.SchemaError as e:
            return {
                "valid": False,
                "error_count": 1,
                "errors": [{
                    "field": "schema",
                    "message": f"Invalid schema: {e.message}",
                    "validator": "schema",
                }],
            }

    def check_required_fields(
        self,
        data: Dict[str, Any],
        required_fields: list[str],
    ) -> tuple[bool, list[str]]:
        """
        Check if data contains all required fields.

        Args:
            data: Data to check
            required_fields: List of required field names

        Returns:
            Tuple of (all_present, missing_fields)
        """
        missing = []

        for field in required_fields:
            if field not in data or data[field] is None:
                missing.append(field)

        return len(missing) == 0, missing

    def sanitize_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize LLM output to ensure it's safe and clean.

        Args:
            data: Raw LLM output

        Returns:
            Sanitized data
        """
        # Remove any null values
        sanitized = {k: v for k, v in data.items() if v is not None}

        # Ensure entities is a dict
        if "entities" in sanitized and not isinstance(sanitized["entities"], dict):
            sanitized["entities"] = {}

        # Validate language code format if present
        if "original_language" in sanitized and sanitized["original_language"]:
            lang = sanitized["original_language"].lower()
            if len(lang) == 2 and lang.isalpha():
                sanitized["original_language"] = lang
            else:
                logger.warning(
                    "Invalid language code, removing",
                    extra={"value": sanitized["original_language"]},
                )
                del sanitized["original_language"]

        # Clamp confidence score if present
        if "confidence_score" in sanitized and sanitized["confidence_score"] is not None:
            score = float(sanitized["confidence_score"])
            sanitized["confidence_score"] = max(0.0, min(1.0, score))

        return sanitized
