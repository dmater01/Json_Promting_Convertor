# Component Architecture
## Structured Prompt Service Platform

**Version**: 1.0
**Last Updated**: 2025-10-13
**Part**: 2 of 8
**Related**: [Overview](01-overview.md) | [Data Architecture](03-data.md)

---

## Component Catalog

| Component | Purpose | Technology | Location |
|-----------|---------|----------|----------|
| **API Gateway** | Entry point, auth, rate limiting | Nginx + Kong | api-gateway/ |
| **FastAPI Service** | Core API logic | FastAPI + Python 3.11 | src/ |
| **Prompt Processor** | Prompt preprocessing | Python | src/services/ |
| **LLM Router** | Multi-provider routing | LiteLLM | src/services/ |
| **Schema Validator** | JSON Schema validation | jsonschema | src/services/ |
| **Cache Service** | Response caching | Redis | src/services/ |
| **Celery Workers** | Async job processing | Celery | src/workers/ |

---

## 1. API Gateway

### Purpose
Single entry point for all client requests, handling cross-cutting concerns before routing to backend services.

### Key Features
- **Authentication**: API key validation against PostgreSQL
- **Rate Limiting**: Token bucket algorithm, limits stored in Redis
- **Input Validation**: Basic request structure validation
- **TLS Termination**: Handles HTTPS, certificates auto-renewed
- **Circuit Breaking**: Fail fast when backend is degraded

### Technology Choice
**Nginx + Kong Gateway** or **AWS API Gateway**

**Rationale**:
- Nginx: Battle-tested, high performance, Lua scripting
- Kong: Built on Nginx, extensive plugin ecosystem
- AWS API Gateway: Managed service, auto-scaling

### Configuration Example

```nginx
upstream fastapi_backend {
    server fastapi:8000 max_fails=3 fail_timeout=30s;
    server fastapi:8001 max_fails=3 fail_timeout=30s;
    keepalive 32;
}

server {
    listen 443 ssl http2;
    server_name api.company.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    # Rate limiting
    limit_req_zone $http_authorization zone=api_limit:10m rate=1000r/h;
    limit_req zone=api_limit burst=20 nodelay;

    location /v1/ {
        proxy_pass http://fastapi_backend;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Request-ID $request_id;
    }
}
```

---

## 2. FastAPI Service (Core API)

### Purpose
Main application logic for prompt processing, LLM interaction, and response validation.

### Architecture Pattern
**Layered Architecture** with dependency injection:

```
┌─────────────────────────┐
│   API Layer (Routes)    │  ← HTTP endpoints
├─────────────────────────┤
│   Service Layer         │  ← Business logic
├─────────────────────────┤
│   Repository Layer      │  ← Data access
├─────────────────────────┤
│   External Adapters     │  ← LLM clients, cache
└─────────────────────────┘
```

### Directory Structure

```
src/
├── api/
│   ├── v1/
│   │   ├── analyze.py         # /v1/analyze endpoints
│   │   ├── jobs.py            # /v1/jobs endpoints
│   │   ├── schemas.py         # /v1/schemas endpoints
│   │   └── health.py          # /v1/health endpoints
│   └── dependencies.py        # Dependency injection
├── core/
│   ├── config.py              # Configuration management
│   ├── security.py            # API key validation
│   └── rate_limiter.py        # Rate limiting logic
├── services/
│   ├── prompt_processor.py    # Prompt preprocessing
│   ├── llm_router.py          # LLM provider routing
│   ├── schema_validator.py    # JSON Schema validation
│   └── cache_service.py       # Cache operations
├── models/
│   ├── request.py             # Pydantic request models
│   ├── response.py            # Pydantic response models
│   └── database.py            # SQLAlchemy models
├── repositories/
│   ├── schema_repo.py         # Schema CRUD
│   ├── request_log_repo.py    # Request logging
│   └── api_key_repo.py        # API key management
├── adapters/
│   ├── llm_client.py          # LiteLLM wrapper
│   ├── cache_client.py        # Redis wrapper
│   └── db_client.py           # PostgreSQL connection
└── utils/
    ├── language_detector.py   # Language detection
    ├── xml_converter.py       # JSON to XML conversion
    └── metrics.py             # Prometheus metrics
```

### Main Application

```python
# src/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
import uvicorn

from api.v1 import analyze, jobs, schemas, health
from core.config import settings

app = FastAPI(
    title="Structured Prompt Service",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Add request ID to all requests
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request.state.request_id = request.headers.get(
        "X-Request-ID",
        str(uuid.uuid4())
    )
    response = await call_next(request)
    response.headers["X-Request-ID"] = request.state.request_id
    return response

# Routes
app.include_router(analyze.router, prefix="/v1/analyze", tags=["analyze"])
app.include_router(jobs.router, prefix="/v1/jobs", tags=["jobs"])
app.include_router(schemas.router, prefix="/v1/schemas", tags=["schemas"])
app.include_router(health.router, prefix="/v1", tags=["health"])

# Prometheus metrics
Instrumentator().instrument(app).expose(app, endpoint="/v1/metrics")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        workers=4,
        log_level="info"
    )
```

### Analyze Endpoint (Core Logic)

```python
# src/api/v1/analyze.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
import time

from models.request import PromptRequest
from models.response import StructuredResponse
from services.prompt_processor import PromptProcessor
from services.llm_router import LLMRouter
from services.schema_validator import SchemaValidator
from services.cache_service import CacheService
from core.security import verify_api_key

router = APIRouter()

@router.post("/", response_model=StructuredResponse)
async def analyze_prompt(
    request: PromptRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key),
    prompt_processor: PromptProcessor = Depends(),
    llm_router: LLMRouter = Depends(),
    validator: SchemaValidator = Depends(),
    cache: CacheService = Depends(),
):
    """Analyze a natural language prompt and return structured data."""
    start_time = time.time()

    # Check cache
    cache_key = cache.generate_key(request)
    cached_response = await cache.get(cache_key)
    if cached_response:
        return cached_response

    # Process prompt
    processed_prompt = await prompt_processor.process(request.prompt)
    language = await prompt_processor.detect_language(request.prompt)
    meta_prompt = prompt_processor.generate_meta_prompt(
        processed_prompt,
        request.schema
    )

    # Route to LLM
    provider_response = await llm_router.route(meta_prompt)

    # Parse and validate
    structured_data = prompt_processor.parse_llm_output(provider_response)
    validation_result = validator.validate(structured_data, request.schema)

    if not validation_result.passed:
        raise HTTPException(
            status_code=422,
            detail={"error": "Validation failed", "errors": validation_result.errors}
        )

    # Build response
    response = StructuredResponse(
        intent=structured_data["intent"],
        subject=structured_data["subject"],
        entities=structured_data["entities"],
        output_format=request.format,
        original_language=language,
        confidence=structured_data.get("confidence", 0.9),
        validation_status="passed",
        processing_time_ms=int((time.time() - start_time) * 1000),
        provider_used=provider_response.provider
    )

    # Cache and log
    await cache.set(cache_key, response.dict())
    background_tasks.add_task(log_request, api_key, request, response)

    return response
```

---

## 3. Prompt Processor Service

### Purpose
Preprocess prompts, detect language, generate meta-prompts, and parse LLM responses.

### Implementation

```python
# src/services/prompt_processor.py
from langdetect import detect
import re

class PromptProcessor:
    """Processes prompts before sending to LLM."""

    def __init__(self):
        self.meta_prompt_template = """
You are a structured data extraction assistant.
Extract the following from the user's prompt:
- intent: Primary action (create, analyze, extract, translate, etc.)
- subject: Main topic or object
- entities: Key details as a JSON object with:
  - key_details: List of key information
  - source: Source of information (if applicable)
  - target: Target of action (if applicable)
- output_format: Desired output format
- original_language: ISO 639-1 code of the subject language

Return ONLY valid JSON matching this structure:
{schema}

User prompt: {prompt}
"""

    async def process(self, prompt: str) -> str:
        """Preprocess prompt text."""
        # Strip whitespace
        prompt = prompt.strip()

        # Remove extra whitespace
        prompt = re.sub(r'\s+', ' ', prompt)

        # Truncate if too long
        if len(prompt) > 10000:
            prompt = prompt[:10000]

        return prompt

    async def detect_language(self, text: str) -> str:
        """Detect language of text."""
        try:
            lang = detect(text)
            return lang
        except:
            return "en"  # Default to English

    def generate_meta_prompt(self, prompt: str, schema: dict = None) -> str:
        """Generate meta-prompt with instructions."""
        schema_str = str(schema) if schema else "default structure"
        return self.meta_prompt_template.format(
            schema=schema_str,
            prompt=prompt
        )

    def parse_llm_output(self, response: dict) -> dict:
        """Parse LLM response, removing markdown code fences."""
        text = response["text"]

        # Remove markdown code fences
        text = re.sub(r'```json\n?', '', text)
        text = re.sub(r'```\n?', '', text)

        # Parse JSON
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM output: {e}")
```

---

## 4. LLM Router

### Purpose
Abstract LLM provider interaction, handle routing, fallback, and retry logic.

### Implementation

```python
# src/services/llm_router.py
from typing import Optional, Dict, Any
import litellm
from litellm import Router

class LLMRouter:
    """Routes prompts to optimal LLM provider."""

    def __init__(self):
        self.router = Router(
            model_list=[
                {
                    "model_name": "gemini",
                    "litellm_params": {
                        "model": "gemini/gemini-pro",
                        "api_key": settings.GEMINI_API_KEY,
                    }
                },
                {
                    "model_name": "claude",
                    "litellm_params": {
                        "model": "claude-3-opus-20240229",
                        "api_key": settings.ANTHROPIC_API_KEY,
                    }
                },
                {
                    "model_name": "gpt-4",
                    "litellm_params": {
                        "model": "gpt-4-turbo-preview",
                        "api_key": settings.OPENAI_API_KEY,
                    }
                }
            ],
            routing_strategy="least-busy",
            retry_after=5,
            allowed_fails=3,
            num_retries=2
        )

    async def route(
        self,
        prompt: str,
        provider: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 2048
    ) -> Dict[str, Any]:
        """Route prompt to appropriate LLM provider."""
        try:
            response = await self.router.acompletion(
                model=provider or "gemini",
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )

            return {
                "text": response.choices[0].message.content,
                "provider": response.model,
                "tokens_used": response.usage.total_tokens,
                "latency_ms": response.response_ms
            }

        except Exception as e:
            # Fallback logic
            if provider == "gemini":
                return await self.route(prompt, provider="claude")
            elif provider == "claude":
                return await self.route(prompt, provider="gpt-4")
            else:
                raise Exception(f"All providers failed: {str(e)}")
```

### Provider Selection Strategy

```
┌────────────────────────────────────────────────┐
│  Routing Strategies                            │
├────────────────────────────────────────────────┤
│  1. Least Busy (default)                       │
│     - Route to provider with fewest active     │
│       requests                                 │
│                                                │
│  2. Cost-Based                                 │
│     - Gemini ($0.01/1K) → Claude ($0.015/1K)  │
│       → GPT-4 ($0.03/1K)                       │
│                                                │
│  3. Latency-Based                              │
│     - Route based on historical p95 latency    │
│                                                │
│  4. Quality-Based                              │
│     - Complex prompts → better models          │
│     - Simple prompts → cheaper models          │
└────────────────────────────────────────────────┘
```

---

## 5. Schema Validator

### Purpose
Validate LLM outputs against JSON schemas to ensure reliability.

### Implementation

```python
# src/services/schema_validator.py
from typing import Dict, Any, Optional
from jsonschema import validate, Draft7Validator
from pydantic import BaseModel

class ValidationResult(BaseModel):
    passed: bool
    errors: Optional[list] = None

class SchemaValidator:
    """Validates structured data against JSON schemas."""

    def __init__(self):
        self.default_schema = {
            "type": "object",
            "properties": {
                "intent": {"type": "string"},
                "subject": {"type": "string"},
                "entities": {"type": "object"},
                "output_format": {"type": "string"},
                "original_language": {"type": "string", "pattern": "^[a-z]{2}$"}
            },
            "required": ["intent", "subject", "entities"]
        }

    def validate(
        self,
        data: Dict[str, Any],
        schema: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """Validate data against JSON schema."""
        schema_to_use = schema or self.default_schema
        validator = Draft7Validator(schema_to_use)

        errors = list(validator.iter_errors(data))

        if errors:
            return ValidationResult(
                passed=False,
                errors=[
                    {
                        "path": ".".join(str(p) for p in error.path),
                        "message": error.message,
                    }
                    for error in errors
                ]
            )

        return ValidationResult(passed=True)
```

---

## 6. Cache Service (Redis)

### Purpose
Reduce LLM API costs and latency by caching responses.

### Implementation

```python
# src/services/cache_service.py
import hashlib
import json
from typing import Optional, Dict, Any
import redis.asyncio as redis

class CacheService:
    """Redis-based caching service."""

    def __init__(self):
        self.redis = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )

    def generate_key(self, request: Dict[str, Any]) -> str:
        """Generate cache key using SHA256."""
        cache_input = {
            "prompt": request["prompt"],
            "format": request.get("format", "json"),
            "schema": request.get("schema"),
        }
        key_string = json.dumps(cache_input, sort_keys=True)
        key_hash = hashlib.sha256(key_string.encode()).hexdigest()
        return f"cache:response:{key_hash}"

    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached response."""
        cached = await self.redis.get(key)
        if cached:
            await self.redis.incr("cache:hits")
            return json.loads(cached)

        await self.redis.incr("cache:misses")
        return None

    async def set(
        self,
        key: str,
        value: Dict[str, Any],
        ttl: int = 3600
    ) -> None:
        """Cache response with TTL."""
        await self.redis.setex(key, ttl, json.dumps(value))
```

---

## 7. Celery Workers (Async Processing)

### Purpose
Handle long-running tasks, batch processing, and webhook callbacks.

### Architecture

```python
# src/workers/celery_app.py
from celery import Celery

celery_app = Celery(
    "structured_prompt_service",
    broker=settings.RABBITMQ_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    task_time_limit=600,  # 10 minutes
)

# src/workers/tasks.py
@celery_app.task(bind=True, max_retries=3)
def process_async_job(self, job_id: str):
    """Process an asynchronous job."""
    job = job_repo.get(job_id)
    job_repo.update_status(job_id, "processing")

    try:
        result = _process_job(job.request_params)
        job_repo.update(job_id, {"status": "completed", "result": result})

        # Send webhook if configured
        if job.webhook_url:
            send_webhook.delay(job.webhook_url, result)

        return result

    except Exception as e:
        job_repo.update(job_id, {"status": "failed", "error": str(e)})
        raise self.retry(exc=e, countdown=60)
```

---

## Component Interaction Diagram

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ HTTP Request
       ▼
┌─────────────┐
│ API Gateway │ ─────── Auth Check (Redis Cache)
└──────┬──────┘
       │ Validated Request
       ▼
┌─────────────┐
│  FastAPI    │
│  Service    │
└──────┬──────┘
       │
       ├─────────► PromptProcessor ──► LLM Router ──► LLM Provider
       │                                    │
       │                                    ▼
       │                           SchemaValidator
       │                                    │
       ├─────────► CacheService ◄──────────┤
       │              (Redis)               │
       │                                    │
       └─────────► RequestLog ──────────────┘
                  (PostgreSQL)
```

---

## Related Documents

- **[Data Architecture](03-data.md)**: Database schemas and models
- **[API Design](04-api.md)**: REST API specifications
- **[Security](06-security.md)**: Security implementation details
- **[Monitoring](07-monitoring.md)**: Observability implementation
