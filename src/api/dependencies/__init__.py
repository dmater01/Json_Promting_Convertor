"""API dependencies."""

from src.api.dependencies.auth import optional_api_key, require_api_key

__all__ = ["require_api_key", "optional_api_key"]
