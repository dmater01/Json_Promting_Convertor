"""Prompt processing service orchestrating all components."""

import time
import uuid
from typing import Any, Dict, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.cache_client import CacheClient
from src.core.exceptions import LLMException, SchemaValidationError
from src.core.logging_config import get_logger
from src.schemas.requests import AnalyzeRequest
from src.schemas.responses import StructuredData
from src.services.llm_router import LLMRouter
from src.services.request_logger import RequestLogger
from src.services.schema_validator import SchemaValidator

logger = get_logger(__name__)


class PromptProcessor:
    """
    Main service for processing prompts through the LLM pipeline.

    Orchestrates:
    - Cache checking
    - LLM routing
    - Schema validation
    - Request logging
    - Error handling

    This is the core business logic that ties everything together.
    """

    def __init__(
        self,
        db: AsyncSession,
        cache: Optional[CacheClient] = None,
    ):
        """
        Initialize the prompt processor.

        Args:
            db: Database session for logging
            cache: Cache client (optional)
        """
        self.db = db
        self.cache = cache
        self.llm_router = LLMRouter()
        self.validator = SchemaValidator()
        self.logger = RequestLogger(db)

    async def process(
        self,
        request: AnalyzeRequest,
        request_id: str,
        api_key_id: Optional[uuid.UUID] = None,
    ) -> Tuple[StructuredData, Dict[str, Any]]:
        """
        Process a prompt analysis request.

        Flow:
        1. Check cache
        2. Route to LLM (if cache miss)
        3. Validate schema
        4. Update cache
        5. Log request
        6. Return results

        Args:
            request: The analyze request
            request_id: Unique request ID
            api_key_id: API key ID (for logging/rate limiting)

        Returns:
            Tuple of (StructuredData, metadata_dict)

        Raises:
            LLMException: If LLM processing fails
            SchemaValidationError: If validation fails
        """
        start_time = time.time()

        logger.info(
            "Processing request",
            extra={
                "request_id": request_id,
                "prompt_length": len(request.prompt),
                "provider": request.llm_provider.value,
                "cache_ttl": request.cache_ttl,
            },
        )

        try:
            # Step 1: Check cache
            cached_response = None
            if self.cache and request.cache_ttl > 0:
                cached_response = await self._check_cache(request)

            if cached_response:
                # Cache hit - return cached response
                latency_ms = int((time.time() - start_time) * 1000)

                metadata = {
                    "request_id": request_id,
                    "provider": cached_response["metadata"]["provider"],
                    "model": cached_response["metadata"]["model"],
                    "tokens_used": cached_response["metadata"].get("tokens_used"),
                    "latency_ms": latency_ms,
                    "cached": True,
                    "validated": True,
                }

                # Log the cached request
                try:
                    await self.logger.log_success(
                        request_id=request_id,
                        api_key_id=api_key_id,
                        prompt=request.prompt,
                        provider=metadata["provider"],
                        model=metadata["model"],
                        response_data=cached_response["data"],
                        tokens_used=metadata["tokens_used"],
                        latency_ms=latency_ms,
                        cached=True,
                        metadata=request.metadata,
                    )
                except Exception as e:
                    # Don't fail request if logging fails
                    logger.warning("Failed to log cached request", extra={"error": str(e)})

                structured_data = StructuredData(**cached_response["data"])
                return structured_data, metadata

            # Step 2: Route to LLM
            llm_response, llm_metadata = await self._route_to_llm(request)

            # Step 3: Validate schema
            validated = await self._validate_response(request, llm_response)

            # Step 4: Sanitize output
            sanitized_data = self.validator.sanitize_output(llm_response)

            # Step 5: Update cache
            if self.cache and request.cache_ttl > 0:
                await self._update_cache(
                    request=request,
                    data=sanitized_data,
                    metadata=llm_metadata,
                )

            # Step 6: Log request
            latency_ms = int((time.time() - start_time) * 1000)
            try:
                await self.logger.log_success(
                    request_id=request_id,
                    api_key_id=api_key_id,
                    prompt=request.prompt,
                    provider=llm_metadata["provider"],
                    model=llm_metadata["model"],
                    response_data=sanitized_data,
                    tokens_used=llm_metadata.get("tokens_used"),
                    latency_ms=latency_ms,
                    cached=False,
                    metadata=request.metadata,
                )
            except Exception as e:
                logger.warning("Failed to log request", extra={"error": str(e)})

            # Step 7: Build response
            metadata = {
                "request_id": request_id,
                "provider": llm_metadata["provider"],
                "model": llm_metadata["model"],
                "tokens_used": llm_metadata.get("tokens_used"),
                "latency_ms": latency_ms,
                "cached": False,
                "validated": validated,
            }

            structured_data = StructuredData(**sanitized_data)

            logger.info(
                "Request processed successfully",
                extra={
                    "request_id": request_id,
                    "latency_ms": latency_ms,
                    "cached": False,
                    "validated": validated,
                },
            )

            return structured_data, metadata

        except LLMException as e:
            # LLM error - log and re-raise
            latency_ms = int((time.time() - start_time) * 1000)

            try:
                await self.logger.log_error(
                    request_id=request_id,
                    api_key_id=api_key_id,
                    prompt=request.prompt,
                    provider=request.llm_provider.value,
                    error=f"{e.error_type}: {e.message}",
                    latency_ms=latency_ms,
                    metadata=request.metadata,
                )
            except Exception as log_error:
                logger.warning("Failed to log error", extra={"error": str(log_error)})

            logger.error(
                "LLM processing failed",
                extra={
                    "request_id": request_id,
                    "error_type": e.error_type,
                    "error": e.message,
                },
            )
            raise

        except SchemaValidationError as e:
            # Validation error - log and re-raise
            latency_ms = int((time.time() - start_time) * 1000)

            try:
                await self.logger.log_error(
                    request_id=request_id,
                    api_key_id=api_key_id,
                    prompt=request.prompt,
                    provider=request.llm_provider.value,
                    error=f"Schema validation failed: {e.message}",
                    latency_ms=latency_ms,
                    metadata=request.metadata,
                )
            except Exception as log_error:
                logger.warning("Failed to log error", extra={"error": str(log_error)})

            logger.error(
                "Schema validation failed",
                extra={
                    "request_id": request_id,
                    "error": e.message,
                },
            )
            raise

        except Exception as e:
            # Unexpected error - log and re-raise
            latency_ms = int((time.time() - start_time) * 1000)

            try:
                await self.logger.log_error(
                    request_id=request_id,
                    api_key_id=api_key_id,
                    prompt=request.prompt,
                    provider=request.llm_provider.value,
                    error=f"Unexpected error: {str(e)}",
                    latency_ms=latency_ms,
                    metadata=request.metadata,
                )
            except Exception as log_error:
                logger.warning("Failed to log error", extra={"error": str(log_error)})

            logger.error(
                "Unexpected processing error",
                extra={
                    "request_id": request_id,
                    "error_type": type(e).__name__,
                    "error": str(e),
                },
            )
            raise

    async def _check_cache(self, request: AnalyzeRequest) -> Optional[Dict[str, Any]]:
        """Check cache for existing response."""
        try:
            cached = await self.cache.get(
                prompt=request.prompt,
                provider=request.llm_provider.value,
                temperature=request.temperature,
                schema=request.schema_definition,
            )

            if cached:
                logger.info("Cache hit")
                return cached

            logger.debug("Cache miss")
            return None

        except Exception as e:
            logger.warning("Cache check failed", extra={"error": str(e)})
            return None

    async def _route_to_llm(self, request: AnalyzeRequest) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Route request to LLM."""
        try:
            return self.llm_router.route_request(request)
        except LLMException:
            raise

    async def _validate_response(
        self,
        request: AnalyzeRequest,
        response: Dict[str, Any],
    ) -> bool:
        """Validate LLM response against schema."""
        try:
            if request.schema_definition:
                # Validate against custom schema
                return self.validator.validate(response, request.schema_definition, strict=True)
            else:
                # Validate against core schema
                return self.validator.validate_core_schema(response)

        except SchemaValidationError:
            raise

    async def _update_cache(
        self,
        request: AnalyzeRequest,
        data: Dict[str, Any],
        metadata: Dict[str, Any],
    ):
        """Update cache with new response."""
        try:
            cache_data = {
                "data": data,
                "metadata": metadata,
            }

            await self.cache.set(
                prompt=request.prompt,
                provider=request.llm_provider.value,
                temperature=request.temperature,
                response=cache_data,
                ttl=request.cache_ttl,
                schema=request.schema_definition,
            )

            logger.debug("Cache updated")

        except Exception as e:
            logger.warning("Cache update failed", extra={"error": str(e)})
