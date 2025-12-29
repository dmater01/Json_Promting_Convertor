"""LLM client for interacting with multiple LLM providers via LiteLLM."""

import json
import time
from typing import Any, Dict, Optional, Tuple

import litellm
from litellm import completion

from src.core.config import settings
from src.core.exceptions import (
    LLMAuthenticationError,
    LLMInvalidRequestError,
    LLMProviderUnavailableError,
    LLMRateLimitError,
    LLMResponseParsingError,
    LLMTimeoutError,
)
from src.core.logging_config import get_logger
from src.schemas.requests import LLMProvider
from src.services.prompt_builder import PromptBuilder

logger = get_logger(__name__)


class LLMClient:
    """
    Client for interacting with LLM providers.

    Uses LiteLLM for unified interface across Gemini, Claude, GPT-4, and other providers.
    Handles retries, error handling, and response parsing.
    """

    # Provider-specific model mappings
    MODEL_MAP = {
        LLMProvider.GEMINI: "gemini/gemini-pro-latest",
        LLMProvider.CLAUDE: "claude-3-sonnet-20240229",
        LLMProvider.GPT4: "gpt-4-turbo",
    }

    # Default timeout for LLM requests (seconds)
    DEFAULT_TIMEOUT = 30

    def __init__(self):
        """Initialize the LLM client."""
        self.prompt_builder = PromptBuilder()
        self._configure_litellm()

    def _configure_litellm(self):
        """Configure LiteLLM with API keys and settings."""
        # Set LiteLLM to not cache responses (we handle caching separately)
        litellm.cache = None

        # Set timeout
        litellm.request_timeout = self.DEFAULT_TIMEOUT

        # Suppress verbose logging in production
        if not settings.debug:
            litellm.suppress_debug_info = True

        # Log configuration
        logger.info(
            "LiteLLM configured",
            extra={
                "timeout": self.DEFAULT_TIMEOUT,
                "debug": settings.debug,
            },
        )

    def generate(
        self,
        prompt: str,
        provider: LLMProvider = LLMProvider.GEMINI,
        temperature: float = 0.1,
        max_tokens: int = 2000,
        **kwargs,
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Generate a completion from an LLM provider.

        Args:
            prompt: The meta-prompt to send to the LLM
            provider: LLM provider to use
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters for the LLM

        Returns:
            Tuple of (parsed_response_dict, metadata_dict)

        Raises:
            LLMAuthenticationError: If API key is invalid
            LLMRateLimitError: If rate limit is exceeded
            LLMProviderUnavailableError: If provider is down
            LLMResponseParsingError: If response cannot be parsed
            LLMTimeoutError: If request times out
        """
        start_time = time.time()
        model = self._get_model_for_provider(provider)

        logger.info(
            "Sending request to LLM",
            extra={
                "provider": provider.value,
                "model": model,
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
        )

        try:
            # Call LiteLLM completion API
            response = completion(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )

            # Extract response text
            response_text = response.choices[0].message.content
            latency_ms = int((time.time() - start_time) * 1000)

            # Parse JSON from response
            cleaned_text = self.prompt_builder.extract_json_from_response(response_text)
            parsed_data = json.loads(cleaned_text)

            # Extract metadata
            metadata = {
                "provider": provider.value,
                "model": model,
                "tokens_used": response.usage.total_tokens if hasattr(response, "usage") else None,
                "latency_ms": latency_ms,
                "raw_response": response_text,
            }

            logger.info(
                "LLM request successful",
                extra={
                    "provider": provider.value,
                    "latency_ms": latency_ms,
                    "tokens_used": metadata["tokens_used"],
                },
            )

            return parsed_data, metadata

        except json.JSONDecodeError as e:
            logger.error(
                "Failed to parse LLM response as JSON",
                extra={
                    "provider": provider.value,
                    "error": str(e),
                    "response_preview": response_text[:200] if "response_text" in locals() else "N/A",
                },
            )
            raise LLMResponseParsingError(
                provider=provider.value,
                raw_response=response_text if "response_text" in locals() else "",
                parse_error=str(e),
            )

        except litellm.AuthenticationError as e:
            logger.error(
                "LLM authentication failed",
                extra={"provider": provider.value, "error": str(e)},
            )
            raise LLMAuthenticationError(provider=provider.value, message=str(e))

        except litellm.RateLimitError as e:
            logger.warning(
                "LLM rate limit exceeded",
                extra={"provider": provider.value, "error": str(e)},
            )
            raise LLMRateLimitError(provider=provider.value, message=str(e))

        except litellm.ServiceUnavailableError as e:
            logger.error(
                "LLM provider unavailable",
                extra={"provider": provider.value, "error": str(e)},
            )
            raise LLMProviderUnavailableError(provider=provider.value, message=str(e))

        except litellm.Timeout as e:
            logger.error(
                "LLM request timed out",
                extra={"provider": provider.value, "timeout": self.DEFAULT_TIMEOUT},
            )
            raise LLMTimeoutError(provider=provider.value, timeout_seconds=self.DEFAULT_TIMEOUT)

        except litellm.BadRequestError as e:
            logger.error(
                "Invalid LLM request",
                extra={"provider": provider.value, "error": str(e)},
            )
            raise LLMInvalidRequestError(provider=provider.value, message=str(e))

        except Exception as e:
            logger.error(
                "Unexpected LLM error",
                extra={
                    "provider": provider.value,
                    "error_type": type(e).__name__,
                    "error": str(e),
                },
            )
            raise LLMProviderUnavailableError(
                provider=provider.value,
                message=f"Unexpected error: {str(e)}",
            )

    def _get_model_for_provider(self, provider: LLMProvider) -> str:
        """
        Get the model identifier for a given provider.

        Args:
            provider: LLM provider enum

        Returns:
            Model identifier string for LiteLLM

        Raises:
            ValueError: If provider is not supported
        """
        if provider == LLMProvider.AUTO:
            # Default to Gemini for auto selection
            provider = LLMProvider.GEMINI

        model = self.MODEL_MAP.get(provider)
        if not model:
            raise ValueError(f"Unsupported provider: {provider}")

        return model

    def test_connection(self, provider: LLMProvider = LLMProvider.GEMINI) -> bool:
        """
        Test connection to an LLM provider.

        Args:
            provider: Provider to test

        Returns:
            True if connection is successful

        Raises:
            LLMException: If connection fails
        """
        test_prompt = "Respond with a single word: 'success'"

        try:
            model = self._get_model_for_provider(provider)
            response = completion(
                model=model,
                messages=[{"role": "user", "content": test_prompt}],
                max_tokens=10,
            )

            logger.info(
                "LLM connection test successful",
                extra={"provider": provider.value},
            )
            return True

        except Exception as e:
            logger.error(
                "LLM connection test failed",
                extra={"provider": provider.value, "error": str(e)},
            )
            raise

    def get_provider_info(self, provider: LLMProvider) -> Dict[str, Any]:
        """
        Get information about a specific provider.

        Args:
            provider: Provider to query

        Returns:
            Dictionary with provider information
        """
        model = self._get_model_for_provider(provider)

        return {
            "provider": provider.value,
            "model": model,
            "supports_streaming": False,  # Not implemented yet
            "max_tokens": 8000,  # Default, varies by model
            "timeout_seconds": self.DEFAULT_TIMEOUT,
        }
