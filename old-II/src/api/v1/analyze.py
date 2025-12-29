"""Core /v1/analyze endpoint for prompt analysis."""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.cache_client import get_cache_client, CacheClient
from src.adapters.db_client import get_db_session
from src.api.dependencies import require_api_key
from src.core.exceptions import LLMException, SchemaValidationError, ServiceException
from src.core.logging_config import get_logger
from src.models.database import APIKey
from src.schemas.requests import AnalyzeRequest
from src.schemas.responses import AnalyzeResponse, ErrorDetail, ErrorResponse
from src.services.prompt_processor import PromptProcessor

logger = get_logger(__name__)

router = APIRouter()


async def get_prompt_processor(
    db: AsyncSession = Depends(get_db_session),
) -> PromptProcessor:
    """
    Dependency for getting prompt processor instance.

    Args:
        db: Database session

    Returns:
        PromptProcessor instance
    """
    cache = await get_cache_client()
    return PromptProcessor(db=db, cache=cache)


@router.post("/", response_model=AnalyzeResponse, status_code=200)
async def analyze_prompt(
    request_body: AnalyzeRequest,
    request: Request,
    api_key: APIKey = Depends(require_api_key),
    processor: PromptProcessor = Depends(get_prompt_processor),
) -> AnalyzeResponse:
    """
    Analyze a natural language prompt and extract structured data.

    This endpoint accepts a natural language prompt and uses LLMs to extract
    structured information including intent, subject, entities, and language.

    **Flow:**
    1. Check cache for existing response
    2. Route to LLM provider (with retries and fallbacks)
    3. Validate schema
    4. Update cache
    5. Log request
    6. Return structured response

    **Example Request:**
    ```json
    {
        "prompt": "Translate 'Bonjour le monde' to English",
        "output_format": "json",
        "llm_provider": "gemini",
        "temperature": 0.1
    }
    ```

    **Example Response:**
    ```json
    {
        "request_id": "123e4567-e89b-12d3-a456-426614174000",
        "data": {
            "intent": "translate",
            "subject": "text",
            "entities": {
                "source": "Bonjour le monde",
                "target_language": "English"
            },
            "output_format": "text",
            "original_language": "fr",
            "confidence_score": 0.95
        },
        "llm_provider": "gemini",
        "model_name": "gemini-pro-latest",
        "tokens_used": 234,
        "latency_ms": 456,
        "cached": false,
        "validated": true,
        "timestamp": "2024-01-15T10:30:00Z"
    }
    ```

    Args:
        request_body: The analyze request
        request: FastAPI request object
        processor: Prompt processor dependency

    Returns:
        AnalyzeResponse with structured data and metadata

    Raises:
        HTTPException: On validation, LLM, or processing errors
    """
    # Get request ID from state (set by middleware)
    request_id = request.state.request_id

    logger.info(
        "Analyze request received",
        extra={
            "request_id": request_id,
            "api_key_id": str(api_key.id),
            "api_key_name": api_key.name,
            "prompt_length": len(request_body.prompt),
            "provider": request_body.llm_provider.value,
        },
    )

    # API key is now validated via dependency injection
    api_key_id = api_key.id

    # Process the request
    structured_data, metadata = await processor.process(
        request=request_body,
        request_id=request_id,
        api_key_id=api_key_id,
    )

    # Build response
    response = AnalyzeResponse(
        request_id=request_id,
        data=structured_data,
        llm_provider=metadata["provider"],
        model_name=metadata["model"],
        tokens_used=metadata.get("tokens_used"),
        latency_ms=metadata["latency_ms"],
        cached=metadata["cached"],
        validated=metadata["validated"],
    )

    logger.info(
        "Analyze request completed",
        extra={
            "request_id": request_id,
            "cached": response.cached,
            "latency_ms": response.latency_ms,
        },
    )

    return response


@router.get("/providers", response_model=dict)
async def list_providers() -> dict:
    """
    List available LLM providers and their status.

    Returns:
        Dictionary with provider information

    **Example Response:**
    ```json
    {
        "providers": [
            {
                "provider": "gemini",
                "model": "gemini-pro-latest",
                "available": true,
                "max_tokens": 8000
            },
            {
                "provider": "claude",
                "model": "claude-3-sonnet-20240229",
                "available": true,
                "max_tokens": 8000
            },
            {
                "provider": "gpt-4",
                "model": "gpt-4-turbo",
                "available": true,
                "max_tokens": 8000
            }
        ]
    }
    ```
    """
    from src.services.llm_router import LLMRouter

    router = LLMRouter()
    providers = router.get_available_providers()

    return {"providers": providers}


@router.get("/cache/stats", response_model=dict)
async def cache_stats() -> dict:
    """
    Get cache statistics.

    Returns:
        Cache statistics dictionary

    **Example Response:**
    ```json
    {
        "available": true,
        "total_keys": 1234,
        "prompt_cache_keys": 567,
        "hits": 8900,
        "misses": 1100,
        "hit_rate": 89.0
    }
    ```
    """
    cache = await get_cache_client()
    stats = await cache.get_stats()

    return stats
