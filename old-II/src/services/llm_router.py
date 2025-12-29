"""LLM router for provider selection, retries, and fallbacks."""

import time
from typing import Any, Dict, List, Optional, Tuple

from src.core.exceptions import (
    LLMException,
    LLMProviderUnavailableError,
    LLMRateLimitError,
    LLMTimeoutError,
)
from src.core.logging_config import get_logger
from src.schemas.requests import AnalyzeRequest, LLMProvider
from src.services.llm_client import LLMClient
from src.services.prompt_builder import PromptBuilder

logger = get_logger(__name__)


class LLMRouter:
    """
    Routes LLM requests to appropriate providers with retry and fallback logic.

    Features:
    - Provider selection (auto or explicit)
    - Retry logic with exponential backoff
    - Fallback to alternative providers
    - Error handling and logging
    """

    # Fallback chain when auto-selection is enabled
    PROVIDER_FALLBACK_CHAIN = [
        LLMProvider.GEMINI,
        LLMProvider.CLAUDE,
        LLMProvider.GPT4,
    ]

    # Retry configuration
    MAX_RETRIES = 3
    INITIAL_RETRY_DELAY = 1.0  # seconds
    MAX_RETRY_DELAY = 10.0  # seconds
    BACKOFF_MULTIPLIER = 2.0

    def __init__(self):
        """Initialize the LLM router."""
        self.client = LLMClient()
        self.prompt_builder = PromptBuilder()

    def route_request(
        self,
        request: AnalyzeRequest,
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Route an analyze request to the appropriate LLM provider.

        Args:
            request: The analyze request

        Returns:
            Tuple of (parsed_response, metadata)

        Raises:
            LLMException: If all providers fail
        """
        # Build the meta-prompt
        if request.schema_definition:
            prompt = self.prompt_builder.build_custom_schema_prompt(
                request, request.schema_definition
            )
        else:
            prompt = self.prompt_builder.build_meta_prompt(request)

        # Add confidence scoring if not using custom schema
        if not request.schema_definition:
            prompt = self.prompt_builder.add_confidence_scoring(prompt)

        # Determine provider(s) to try
        if request.llm_provider == LLMProvider.AUTO:
            providers = self.PROVIDER_FALLBACK_CHAIN
            logger.info("Using auto provider selection", extra={"chain": [p.value for p in providers]})
        else:
            providers = [request.llm_provider]
            logger.info("Using explicit provider", extra={"provider": request.llm_provider.value})

        # Try providers in order
        last_exception = None
        for provider in providers:
            try:
                logger.info(
                    "Attempting provider",
                    extra={"provider": provider.value},
                )

                # Try with retries
                result, metadata = self._try_with_retries(
                    prompt=prompt,
                    provider=provider,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                )

                logger.info(
                    "Provider succeeded",
                    extra={
                        "provider": provider.value,
                        "latency_ms": metadata["latency_ms"],
                    },
                )

                return result, metadata

            except (LLMProviderUnavailableError, LLMTimeoutError, LLMRateLimitError) as e:
                # These errors are retryable, try next provider in fallback chain
                logger.warning(
                    "Provider failed, trying next in chain",
                    extra={
                        "provider": provider.value,
                        "error_type": type(e).__name__,
                        "error": str(e),
                    },
                )
                last_exception = e
                continue

            except LLMException as e:
                # Other LLM exceptions are not retryable (auth, invalid request, etc.)
                logger.error(
                    "Provider failed with non-retryable error",
                    extra={
                        "provider": provider.value,
                        "error_type": type(e).__name__,
                        "error": str(e),
                    },
                )
                raise

        # All providers failed
        logger.error(
            "All providers failed",
            extra={
                "providers_tried": [p.value for p in providers],
                "last_error": str(last_exception) if last_exception else "Unknown",
            },
        )

        if last_exception:
            raise last_exception
        else:
            raise LLMProviderUnavailableError(
                provider="all",
                message="All LLM providers failed",
            )

    def _try_with_retries(
        self,
        prompt: str,
        provider: LLMProvider,
        temperature: float,
        max_tokens: int,
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Try to get a response from a provider with exponential backoff retries.

        Args:
            prompt: The meta-prompt
            provider: Provider to use
            temperature: Temperature parameter
            max_tokens: Max tokens parameter

        Returns:
            Tuple of (parsed_response, metadata)

        Raises:
            LLMException: If all retries fail
        """
        delay = self.INITIAL_RETRY_DELAY
        last_exception = None

        for attempt in range(self.MAX_RETRIES):
            try:
                logger.debug(
                    "Attempting LLM request",
                    extra={
                        "provider": provider.value,
                        "attempt": attempt + 1,
                        "max_attempts": self.MAX_RETRIES,
                    },
                )

                result, metadata = self.client.generate(
                    prompt=prompt,
                    provider=provider,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )

                # Add attempt info to metadata
                metadata["attempts"] = attempt + 1

                return result, metadata

            except (LLMProviderUnavailableError, LLMTimeoutError, LLMRateLimitError) as e:
                last_exception = e

                if attempt < self.MAX_RETRIES - 1:
                    logger.warning(
                        "LLM request failed, retrying",
                        extra={
                            "provider": provider.value,
                            "attempt": attempt + 1,
                            "retry_delay": delay,
                            "error": str(e),
                        },
                    )

                    # Exponential backoff
                    time.sleep(delay)
                    delay = min(delay * self.BACKOFF_MULTIPLIER, self.MAX_RETRY_DELAY)
                else:
                    logger.error(
                        "LLM request failed after all retries",
                        extra={
                            "provider": provider.value,
                            "attempts": self.MAX_RETRIES,
                            "error": str(e),
                        },
                    )

            except LLMException:
                # Non-retryable errors - raise immediately
                raise

        # All retries exhausted
        if last_exception:
            raise last_exception
        else:
            raise LLMProviderUnavailableError(
                provider=provider.value,
                message=f"Failed after {self.MAX_RETRIES} attempts",
            )

    def get_available_providers(self) -> List[Dict[str, Any]]:
        """
        Get information about all available providers.

        Returns:
            List of provider info dictionaries
        """
        providers = []
        for provider in [LLMProvider.GEMINI, LLMProvider.CLAUDE, LLMProvider.GPT4]:
            try:
                info = self.client.get_provider_info(provider)
                info["available"] = True
                providers.append(info)
            except Exception as e:
                providers.append({
                    "provider": provider.value,
                    "available": False,
                    "error": str(e),
                })

        return providers

    def test_provider(self, provider: LLMProvider) -> bool:
        """
        Test if a specific provider is available.

        Args:
            provider: Provider to test

        Returns:
            True if provider is available and responding

        Raises:
            LLMException: If provider test fails
        """
        logger.info("Testing provider", extra={"provider": provider.value})

        try:
            result = self.client.test_connection(provider)
            logger.info("Provider test successful", extra={"provider": provider.value})
            return result
        except Exception as e:
            logger.error(
                "Provider test failed",
                extra={"provider": provider.value, "error": str(e)},
            )
            raise

    def get_fallback_chain(self, primary_provider: LLMProvider) -> List[LLMProvider]:
        """
        Get the fallback chain for a given primary provider.

        Args:
            primary_provider: The primary provider

        Returns:
            List of providers in fallback order
        """
        if primary_provider == LLMProvider.AUTO:
            return self.PROVIDER_FALLBACK_CHAIN.copy()

        # Put primary provider first, then add others
        chain = [primary_provider]
        for provider in self.PROVIDER_FALLBACK_CHAIN:
            if provider != primary_provider:
                chain.append(provider)

        return chain
