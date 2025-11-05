# System Architecture Document
## Structured Prompt Service Platform

**Version**: 1.0
**Last Updated**: 2025-10-13
**Status**: Final
**Related Documents**: PRD_STRUCTURED_PROMPT_SERVICE.md

---

## 1. Executive Summary

### 1.1 Architectural Approach

The Structured Prompt Service Platform is designed as a **cloud-native, microservices-based API platform** that transforms natural language prompts into validated structured data using Large Language Models (LLMs). The architecture prioritizes:

- **Reliability**: Multi-layer validation, caching, and fallback mechanisms
- **Performance**: Sub-2-second p95 latency through intelligent caching and async processing
- **Scalability**: Horizontal scaling via containerization and stateless services
- **Extensibility**: Provider-agnostic LLM abstraction supporting multiple vendors
- **Observability**: Comprehensive monitoring, tracing, and alerting

### 1.2 Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **FastAPI Framework** | Native async support, automatic OpenAPI docs, high performance (comparable to Node.js/Go) |
| **LiteLLM Client** | Unified interface for 50+ LLM providers, built-in retry/fallback logic |
| **Redis for Caching** | In-memory performance, persistence options, distributed support, pub/sub for invalidation |
| **PostgreSQL for Persistence** | ACID compliance for schemas/logs, JSON support, robust ecosystem |
| **RabbitMQ for Async Jobs** | Reliable message delivery, dead-letter queues, widely adopted |
| **Kubernetes Orchestration** | Industry standard, auto-scaling, self-healing, cloud-agnostic |
| **Pydantic v2 Validation** | Runtime type safety, JSON schema generation, 10x faster than v1 |

### 1.3 Architecture Highlights

```
┌──────────────────────────────────────────────────────────────────────┐
│                         PLATFORM OVERVIEW                            │
│                                                                      │
│  Client Apps → API Gateway → Core Service → LLM Providers          │
│                      ↓           ↓                                   │
│                  Cache Layer  Data Store                             │
│                                                                      │
│  Key Capabilities:                                                   │
│  • 99.9% uptime SLA                                                 │
│  • p95 latency < 2s                                                 │
│  • 10,000+ requests/day                                             │
│  • Multi-LLM provider support                                       │
│  • 40-60% cost reduction via caching                                │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 2. System Overview

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            CLIENT LAYER                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │ Web Apps     │  │ Mobile Apps  │  │ Internal     │  │ Data       │ │
│  │              │  │              │  │ Services     │  │ Pipelines  │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └─────┬──────┘ │
└─────────┼──────────────────┼──────────────────┼─────────────────┼────────┘
          │                  │                  │                 │
          └──────────────────┴──────────────────┴─────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         API GATEWAY LAYER                               │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │  • TLS Termination                  • Rate Limiting               │ │
│  │  • API Key Authentication           • Request/Response Logging    │ │
│  │  • Input Validation                 • Circuit Breaking            │ │
│  └───────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────┬───────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
              ▼                               ▼
┌─────────────────────────┐      ┌──────────────────────────┐
│   SYNCHRONOUS API       │      │   ASYNCHRONOUS WORKER    │
│   (FastAPI Service)     │      │   (Celery/RQ Workers)    │
│                         │      │                          │
│  /v1/analyze            │      │  • Batch Processing      │
│  /v1/analyze/batch      │      │  • Long-running Jobs     │
│  /v1/health             │      │  • Webhook Callbacks     │
│  /v1/metrics            │      │                          │
└───────────┬─────────────┘      └─────────────┬────────────┘
            │                                  │
            └──────────────┬───────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        CORE SERVICE LAYER                               │
│  ┌────────────────────┐  ┌──────────────────┐  ┌────────────────────┐ │
│  │ Prompt Processor   │  │ Schema Validator │  │ LLM Router         │ │
│  │                    │  │                  │  │                    │ │
│  │ • Preprocessing    │  │ • JSON Schema    │  │ • Provider Select  │ │
│  │ • Language Detect  │  │ • Validation     │  │ • Load Balancing   │ │
│  │ • Meta-prompt Gen  │  │ • Error Reports  │  │ • Fallback Logic   │ │
│  └────────────────────┘  └──────────────────┘  └────────────────────┘ │
└───────────┬─────────────────────────┬────────────────────┬──────────────┘
            │                         │                    │
    ┌───────▼────────┐      ┌─────────▼─────────┐   ┌─────▼──────────┐
    │  CACHE LAYER   │      │   DATA STORE      │   │  LLM PROVIDERS │
    │  (Redis)       │      │   (PostgreSQL)    │   │                │
    │                │      │                   │   │  ┌──────────┐  │
    │  • Responses   │      │  • Request Logs   │   │  │ Gemini   │  │
    │  • Schemas     │      │  • User Schemas   │   │  │ Claude   │  │
    │  • Rate Limits │      │  • API Keys       │   │  │ GPT-4    │  │
    │  • Sessions    │      │  • Templates      │   │  │ Llama    │  │
    └────────────────┘      └───────────────────┘   │  └──────────┘  │
                                                     └────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                      OBSERVABILITY LAYER                                │
│  ┌────────────┐  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Prometheus │  │   Grafana   │  │     ELK      │  │ OpenTelemetry│ │
│  │ (Metrics)  │  │ (Dashboards)│  │   (Logs)     │  │   (Traces)   │ │
│  └────────────┘  └─────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Data Flow

#### Synchronous Request Flow
```
1. Client → API Gateway
   - Authenticate via API key
   - Rate limit check
   - Input validation

2. API Gateway → Core Service
   - Cache lookup (Redis)
   - If cache hit: return cached response (latency: ~10ms)
   - If cache miss: proceed to LLM

3. Core Service → LLM Provider
   - Generate meta-prompt
   - Select optimal provider
   - Send request with retry logic

4. LLM Provider → Core Service
   - Receive structured response
   - Parse and clean output

5. Core Service → Schema Validator
   - Validate against JSON schema
   - Generate validation report

6. Core Service → Client
   - Cache response (Redis)
   - Log to database (async)
   - Return to client
   - Record metrics

Total latency (cache miss): 1.5-2.5s
Total latency (cache hit): 10-50ms
```

#### Asynchronous Job Flow
```
1. Client → API Gateway → Job Queue
   - Submit job with webhook URL
   - Return job_id immediately

2. Worker → Job Queue
   - Pick up job from queue
   - Process (potentially long-running)

3. Worker → Client Webhook
   - POST results to callback URL
   - Retry on failure (exponential backoff)

4. Client → GET /v1/jobs/{id}
   - Poll for status updates
   - Retrieve results when complete
```

### 2.3 Component Responsibilities

| Component | Responsibilities | Technologies |
|-----------|-----------------|--------------|
| **API Gateway** | Authentication, rate limiting, routing, TLS termination | Nginx/Kong + Lua scripts |
| **Sync API Service** | Real-time request handling, cache management | FastAPI, Python 3.11+ |
| **Async Workers** | Batch processing, long jobs, webhook callbacks | Celery/RQ, Python 3.11+ |
| **Prompt Processor** | Text preprocessing, language detection, meta-prompt generation | Python, langdetect |
| **Schema Validator** | JSON Schema validation, error reporting | jsonschema, Pydantic |
| **LLM Router** | Provider selection, load balancing, fallback | LiteLLM |
| **Cache Layer** | Response caching, rate limit counters, session storage | Redis 7+ |
| **Data Store** | Request logs, schemas, user data, API keys | PostgreSQL 15+ |
| **Message Queue** | Job queue, task distribution | RabbitMQ |

---

## 3. Component Architecture

### 3.1 API Gateway

#### Purpose
Single entry point for all client requests, handling cross-cutting concerns before routing to backend services.

#### Key Features
- **Authentication**: API key validation against PostgreSQL
- **Rate Limiting**: Token bucket algorithm, limits stored in Redis
- **Input Validation**: Basic request structure validation
- **TLS Termination**: Handles HTTPS, certificates auto-renewed via Let's Encrypt
- **Circuit Breaking**: Fail fast when backend is degraded

#### Technology Choice
**Nginx + Kong Gateway** or **AWS API Gateway**

Rationale:
- Nginx: Battle-tested, high performance, Lua scripting for custom logic
- Kong: Built on Nginx, extensive plugin ecosystem, rate limiting built-in
- AWS API Gateway: Managed service, auto-scaling, integrates with AWS services

#### Configuration Example
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
        # API key validation (via Lua or Kong plugin)
        access_by_lua_block {
            local api_key = ngx.var.http_authorization
            -- Validate against Redis cache or PostgreSQL
        }

        proxy_pass http://fastapi_backend;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Request-ID $request_id;
    }
}
```

### 3.2 Core API Service (FastAPI)

#### Purpose
Main application logic for prompt processing, LLM interaction, and response validation.

#### Architecture Pattern
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

#### Directory Structure
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

#### Key Code Example: Main Application
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
    request.state.request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
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
        log_level="info",
        access_log=True
    )
```

#### Key Code Example: Analyze Endpoint
```python
# src/api/v1/analyze.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Optional
import time

from models.request import PromptRequest
from models.response import StructuredResponse
from services.prompt_processor import PromptProcessor
from services.llm_router import LLMRouter
from services.schema_validator import SchemaValidator
from services.cache_service import CacheService
from repositories.request_log_repo import RequestLogRepository
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
    log_repo: RequestLogRepository = Depends(),
):
    """
    Analyze a natural language prompt and return structured data.

    - **prompt**: The natural language text to analyze
    - **format**: Output format (json or xml)
    - **schema**: Optional JSON Schema for validation
    - **options**: Additional processing options
    """
    start_time = time.time()

    # Check cache
    cache_key = cache.generate_key(request)
    cached_response = await cache.get(cache_key)
    if cached_response and not request.options.bypass_cache:
        cached_response["cached"] = True
        return cached_response

    # Preprocess prompt
    processed_prompt = await prompt_processor.process(request.prompt)

    # Detect language
    language = await prompt_processor.detect_language(request.prompt)

    # Generate meta-prompt
    meta_prompt = prompt_processor.generate_meta_prompt(
        processed_prompt,
        request.schema
    )

    # Route to LLM provider
    provider_response = await llm_router.route(
        meta_prompt,
        provider=request.options.provider
    )

    # Parse LLM output
    structured_data = prompt_processor.parse_llm_output(provider_response)

    # Validate against schema
    validation_result = validator.validate(
        structured_data,
        request.schema
    )

    if not validation_result.passed:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "Schema validation failed",
                "validation_errors": validation_result.errors
            }
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
        provider_used=provider_response.provider,
        cached=False
    )

    # Cache response
    await cache.set(cache_key, response.dict(), ttl=request.options.cache_ttl)

    # Log request (async, don't block response)
    background_tasks.add_task(
        log_repo.create,
        api_key=api_key,
        request=request.dict(),
        response=response.dict(),
        processing_time_ms=response.processing_time_ms
    )

    return response
```

### 3.3 LLM Router

#### Purpose
Abstract LLM provider interaction, handle routing, fallback, and retry logic.

#### Design Pattern
**Strategy Pattern** with provider adapters:
```python
# src/services/llm_router.py
from typing import Optional, Dict, Any
import litellm
from litellm import completion, Router
from core.config import settings

class LLMRouter:
    """
    Routes prompts to optimal LLM provider with fallback and retry.
    """

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
            routing_strategy="least-busy",  # or "latency-based", "cost-based"
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
        """
        Route prompt to appropriate LLM provider.

        Args:
            prompt: The meta-prompt to send to LLM
            provider: Optional specific provider (gemini, claude, gpt-4)
            temperature: LLM temperature (lower = more deterministic)
            max_tokens: Maximum response tokens

        Returns:
            Dict containing response text and metadata
        """
        try:
            response = await self.router.acompletion(
                model=provider or "gemini",  # Default to Gemini
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
                raise Exception(f"All LLM providers failed: {str(e)}")
```

#### Provider Selection Strategy
```
┌────────────────────────────────────────────────┐
│  Routing Strategies                            │
├────────────────────────────────────────────────┤
│  1. Least Busy (default)                       │
│     - Route to provider with fewest active     │
│       requests                                 │
│                                                │
│  2. Cost-Based                                 │
│     - Route to cheapest provider               │
│     - Gemini ($0.01/1K) → Claude ($0.015/1K)  │
│       → GPT-4 ($0.03/1K)                       │
│                                                │
│  3. Latency-Based                              │
│     - Route to fastest provider based on       │
│       historical p95 latency                   │
│                                                │
│  4. Quality-Based                              │
│     - Route complex prompts to better models   │
│     - Use cheaper models for simple tasks      │
└────────────────────────────────────────────────┘
```

### 3.4 Schema Validator

#### Purpose
Validate LLM outputs against JSON schemas to ensure reliability.

#### Implementation
```python
# src/services/schema_validator.py
from typing import Dict, Any, Optional
from jsonschema import validate, ValidationError, Draft7Validator
from pydantic import BaseModel

class ValidationResult(BaseModel):
    passed: bool
    errors: Optional[list] = None
    warnings: Optional[list] = None

class SchemaValidator:
    """
    Validates structured data against JSON schemas.
    """

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
            "required": ["intent", "subject", "entities", "output_format", "original_language"]
        }

    def validate(
        self,
        data: Dict[str, Any],
        schema: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        Validate data against JSON schema.

        Args:
            data: The structured data to validate
            schema: JSON Schema (Draft 7+), uses default if None

        Returns:
            ValidationResult with passed status and errors
        """
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
                        "schema_path": ".".join(str(p) for p in error.schema_path)
                    }
                    for error in errors
                ]
            )

        return ValidationResult(passed=True)

    def validate_with_retry(
        self,
        data: Dict[str, Any],
        schema: Dict[str, Any],
        max_retries: int = 2
    ) -> ValidationResult:
        """
        Validate with automatic schema relaxation on failure.
        Useful for handling minor format issues.
        """
        result = self.validate(data, schema)

        if not result.passed and max_retries > 0:
            # Relax schema (e.g., make some fields optional)
            relaxed_schema = self._relax_schema(schema)
            return self.validate_with_retry(data, relaxed_schema, max_retries - 1)

        return result

    def _relax_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a more permissive version of the schema.
        """
        relaxed = schema.copy()
        if "required" in relaxed:
            # Make half of required fields optional
            relaxed["required"] = relaxed["required"][:len(relaxed["required"])//2]
        return relaxed
```

### 3.5 Cache Layer (Redis)

#### Purpose
Reduce LLM API costs and latency by caching responses.

#### Cache Strategy
```python
# src/services/cache_service.py
import hashlib
import json
from typing import Optional, Dict, Any
import redis.asyncio as redis
from core.config import settings

class CacheService:
    """
    Redis-based caching service for LLM responses.
    """

    def __init__(self):
        self.redis = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )

    def generate_key(self, request: Dict[str, Any]) -> str:
        """
        Generate cache key from request parameters.
        Uses SHA256 hash of prompt + schema + options.
        """
        cache_input = {
            "prompt": request["prompt"],
            "format": request.get("format", "json"),
            "schema": request.get("schema"),
            "language_detection": request.get("options", {}).get("language_detection", True)
        }
        key_string = json.dumps(cache_input, sort_keys=True)
        key_hash = hashlib.sha256(key_string.encode()).hexdigest()
        return f"cache:response:{key_hash}"

    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get cached response.
        """
        cached = await self.redis.get(key)
        if cached:
            await self.redis.incr(f"cache:hits:{key}")
            return json.loads(cached)

        await self.redis.incr("cache:misses")
        return None

    async def set(
        self,
        key: str,
        value: Dict[str, Any],
        ttl: int = 3600
    ) -> None:
        """
        Cache response with TTL.
        """
        await self.redis.setex(
            key,
            ttl,
            json.dumps(value)
        )

    async def invalidate(self, pattern: str = "*") -> int:
        """
        Invalidate cache entries matching pattern.
        Returns number of keys deleted.
        """
        keys = await self.redis.keys(f"cache:response:{pattern}")
        if keys:
            return await self.redis.delete(*keys)
        return 0

    async def get_stats(self) -> Dict[str, int]:
        """
        Get cache performance statistics.
        """
        hits = await self.redis.get("cache:hits") or 0
        misses = await self.redis.get("cache:misses") or 0
        total = int(hits) + int(misses)
        hit_rate = int(hits) / total if total > 0 else 0

        return {
            "hits": int(hits),
            "misses": int(misses),
            "hit_rate": round(hit_rate, 3),
            "total_requests": total
        }
```

#### Cache Key Design
```
Pattern: cache:response:{sha256_hash}

Example:
Input:
{
  "prompt": "Extract invoice details from Invoice #12345",
  "format": "json",
  "schema": {...},
  "language_detection": true
}

Key: cache:response:a3f8b2c1e9d7f4a6b8c2e1d9f7a4b6c8...

TTL: 3600 seconds (1 hour, configurable)
```

### 3.6 Data Store (PostgreSQL)

#### Schema Design
```sql
-- API Keys and Users
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key_hash VARCHAR(64) NOT NULL UNIQUE,  -- SHA256 of API key
    name VARCHAR(255) NOT NULL,
    team VARCHAR(255),
    rate_limit_per_hour INT DEFAULT 1000,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,
    INDEX idx_key_hash (key_hash)
);

-- Request Logs
CREATE TABLE request_logs (
    id BIGSERIAL PRIMARY KEY,
    request_id UUID NOT NULL UNIQUE,
    api_key_id UUID REFERENCES api_keys(id),
    prompt_text TEXT NOT NULL,
    prompt_length INT,
    request_params JSONB,
    response_data JSONB,
    validation_status VARCHAR(50),
    provider_used VARCHAR(50),
    processing_time_ms INT,
    tokens_used INT,
    cached BOOLEAN DEFAULT false,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_api_key (api_key_id),
    INDEX idx_created_at (created_at),
    INDEX idx_provider (provider_used)
);

-- User-defined Schemas
CREATE TABLE schemas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    schema_definition JSONB NOT NULL,
    version INT DEFAULT 1,
    is_public BOOLEAN DEFAULT false,
    created_by UUID REFERENCES api_keys(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_name (name),
    UNIQUE (name, version)
);

-- Prompt Templates
CREATE TABLE prompt_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    template_text TEXT NOT NULL,
    parameters JSONB,  -- List of required parameters
    example_usage JSONB,
    schema_id UUID REFERENCES schemas(id),
    is_public BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_name (name)
);

-- Async Jobs
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    api_key_id UUID REFERENCES api_keys(id),
    job_type VARCHAR(50) NOT NULL,  -- 'analyze', 'batch', etc.
    status VARCHAR(50) DEFAULT 'pending',  -- pending, processing, completed, failed
    request_params JSONB NOT NULL,
    result JSONB,
    error_message TEXT,
    webhook_url VARCHAR(500),
    webhook_status VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    expires_at TIMESTAMP DEFAULT NOW() + INTERVAL '24 hours',
    INDEX idx_api_key (api_key_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);
```

#### Data Retention Policy
```
Request Logs:
- Hot storage (SSD): 30 days
- Warm storage (HDD): 90 days
- Archive (S3): 1 year
- Delete: After 1 year

Jobs:
- Keep for 24 hours after completion
- Delete expired jobs daily (cron job)

Schemas & Templates:
- Keep indefinitely (small data)
- Soft delete with version history
```

### 3.7 Async Worker (Celery/RQ)

#### Purpose
Handle long-running tasks, batch processing, and webhook callbacks.

#### Architecture
```python
# src/workers/celery_app.py
from celery import Celery
from core.config import settings

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
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,  # 10 minutes
    task_soft_time_limit=540,  # 9 minutes (warning)
)

# src/workers/tasks.py
from celery import Task
import httpx
from typing import Dict, Any, List

from services.prompt_processor import PromptProcessor
from services.llm_router import LLMRouter
from repositories.job_repo import JobRepository

@celery_app.task(bind=True, max_retries=3)
def process_async_job(self: Task, job_id: str) -> Dict[str, Any]:
    """
    Process an asynchronous job.
    """
    job_repo = JobRepository()
    job = job_repo.get(job_id)

    if not job:
        raise ValueError(f"Job {job_id} not found")

    job_repo.update_status(job_id, "processing")

    try:
        # Process the job
        result = _process_job(job.request_params)

        # Update job with result
        job_repo.update(job_id, {
            "status": "completed",
            "result": result,
            "completed_at": "NOW()"
        })

        # Send webhook if configured
        if job.webhook_url:
            send_webhook.delay(job.webhook_url, result)

        return result

    except Exception as e:
        job_repo.update(job_id, {
            "status": "failed",
            "error_message": str(e),
            "completed_at": "NOW()"
        })
        raise self.retry(exc=e, countdown=60)

@celery_app.task(max_retries=5)
def send_webhook(url: str, payload: Dict[str, Any]) -> None:
    """
    Send webhook notification.
    """
    try:
        response = httpx.post(
            url,
            json=payload,
            timeout=30,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
    except Exception as e:
        raise self.retry(exc=e, countdown=2 ** self.request.retries)

@celery_app.task
def process_batch(prompts: List[str], options: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Process multiple prompts in parallel.
    """
    from celery import group

    # Create subtasks
    job = group(
        process_single_prompt.s(prompt, options)
        for prompt in prompts
    )

    # Execute in parallel
    result = job.apply_async()

    # Wait for all to complete
    return result.get()

@celery_app.task
def process_single_prompt(prompt: str, options: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a single prompt (used by batch processing).
    """
    processor = PromptProcessor()
    router = LLMRouter()

    # ... processing logic ...

    return result
```

---

## 4. Data Architecture

### 4.1 Data Models (Pydantic)

```python
# src/models/request.py
from pydantic import BaseModel, Field, validator
from typing import Optional, Literal, Dict, Any
from enum import Enum

class OutputFormat(str, Enum):
    JSON = "json"
    XML = "xml"

class PromptOptions(BaseModel):
    include_confidence: bool = True
    language_detection: bool = True
    cache_ttl: int = Field(default=3600, ge=60, le=86400)
    provider: Optional[Literal["gemini", "claude", "gpt-4", "llama"]] = None
    bypass_cache: bool = False
    temperature: float = Field(default=0.1, ge=0.0, le=1.0)
    max_tokens: int = Field(default=2048, ge=100, le=4096)

class PromptRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=10000)
    format: OutputFormat = OutputFormat.JSON
    schema: Optional[Dict[str, Any]] = None
    options: Optional[PromptOptions] = PromptOptions()

    @validator("prompt")
    def validate_prompt(cls, v):
        if not v.strip():
            raise ValueError("Prompt cannot be empty")
        return v.strip()

    class Config:
        schema_extra = {
            "example": {
                "prompt": "Extract invoice details from: Invoice #12345, Date: 2025-01-15",
                "format": "json",
                "options": {
                    "include_confidence": True,
                    "cache_ttl": 3600
                }
            }
        }

# src/models/response.py
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

class EntityExtraction(BaseModel):
    key_details: List[str]
    source: Optional[str] = None
    target: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class StructuredResponse(BaseModel):
    intent: str = Field(..., description="Primary action (create, analyze, extract, etc.)")
    subject: str = Field(..., description="Main topic or object")
    entities: EntityExtraction = Field(..., description="Extracted key information")
    output_format: str
    original_language: str = Field(..., description="ISO 639-1 language code")
    confidence: float = Field(..., ge=0.0, le=1.0)
    validation_status: Literal["passed", "failed", "skipped"]
    processing_time_ms: int
    provider_used: str
    cached: bool = False

    class Config:
        schema_extra = {
            "example": {
                "intent": "extract",
                "subject": "invoice details",
                "entities": {
                    "key_details": ["invoice_number: 12345", "date: 2025-01-15"],
                    "source": "invoice",
                    "target": "structured_data"
                },
                "output_format": "json",
                "original_language": "en",
                "confidence": 0.95,
                "validation_status": "passed",
                "processing_time_ms": 1243,
                "provider_used": "gemini",
                "cached": False
            }
        }

class BatchRequest(BaseModel):
    prompts: List[str] = Field(..., min_items=1, max_items=100)
    format: OutputFormat = OutputFormat.JSON
    schema: Optional[Dict[str, Any]] = None
    options: Optional[PromptOptions] = PromptOptions()

class BatchResponse(BaseModel):
    results: List[StructuredResponse]
    summary: Dict[str, int] = Field(
        ...,
        description="Summary with total, successful, failed counts"
    )
    processing_time_ms: int
```

### 4.2 Database Models (SQLAlchemy)

```python
# src/models/database.py
from sqlalchemy import Column, String, Integer, Boolean, Text, TIMESTAMP, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key_hash = Column(String(64), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    team = Column(String(255))
    rate_limit_per_hour = Column(Integer, default=1000)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    expires_at = Column(TIMESTAMP, nullable=True)

class RequestLog(Base):
    __tablename__ = "request_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    request_id = Column(UUID(as_uuid=True), unique=True, nullable=False)
    api_key_id = Column(UUID(as_uuid=True), ForeignKey("api_keys.id"))
    prompt_text = Column(Text, nullable=False)
    prompt_length = Column(Integer)
    request_params = Column(JSON)
    response_data = Column(JSON)
    validation_status = Column(String(50))
    provider_used = Column(String(50), index=True)
    processing_time_ms = Column(Integer)
    tokens_used = Column(Integer)
    cached = Column(Boolean, default=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), index=True)

class Schema(Base):
    __tablename__ = "schemas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    schema_definition = Column(JSON, nullable=False)
    version = Column(Integer, default=1)
    is_public = Column(Boolean, default=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("api_keys.id"))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
```

### 4.3 Data Flow Diagrams

#### Write Path (New Request)
```
Client Request
     ↓
API Gateway (validate API key, rate limit)
     ↓
FastAPI Service
     ↓
Cache Check (Redis) → [HIT] → Return cached response
     ↓ [MISS]
LLM Router → LLM Provider
     ↓
Response Parsing
     ↓
Schema Validation
     ↓ [PASS]
Cache Write (Redis)
     ↓
Background: Log to PostgreSQL
     ↓
Return to Client
```

#### Read Path (Job Status)
```
Client GET /v1/jobs/{id}
     ↓
API Gateway
     ↓
FastAPI Service
     ↓
PostgreSQL Query (jobs table)
     ↓
Return Job Status + Result
```

---

## 5. API Design

### 5.1 REST API Specification

#### Base URL
```
Production: https://api.company.com
Staging: https://api-staging.company.com
```

#### Authentication
```http
Authorization: Bearer YOUR_API_KEY
```

#### Endpoints

##### POST /v1/analyze
Analyze a single prompt.

**Request:**
```json
{
  "prompt": "Extract key details from this invoice: Invoice #12345, Date: 2025-01-15, Amount: $1,250.00",
  "format": "json",
  "schema": {
    "type": "object",
    "properties": {
      "invoice_number": {"type": "string"},
      "date": {"type": "string", "format": "date"},
      "amount": {"type": "number"}
    },
    "required": ["invoice_number", "date", "amount"]
  },
  "options": {
    "include_confidence": true,
    "language_detection": true,
    "cache_ttl": 3600,
    "provider": "gemini"
  }
}
```

**Response (200 OK):**
```json
{
  "intent": "extract",
  "subject": "invoice details",
  "entities": {
    "key_details": [
      "invoice_number: 12345",
      "date: 2025-01-15",
      "amount: 1250.00"
    ],
    "source": "invoice",
    "target": "structured_data"
  },
  "output_format": "json",
  "original_language": "en",
  "confidence": 0.95,
  "validation_status": "passed",
  "processing_time_ms": 1243,
  "provider_used": "gemini",
  "cached": false
}
```

##### POST /v1/analyze/batch
Analyze multiple prompts in a single request.

**Request:**
```json
{
  "prompts": [
    "Extract invoice details from Invoice #12345",
    "Translate 'Hello World' to Spanish",
    "Summarize this document..."
  ],
  "format": "json",
  "options": {
    "include_confidence": true
  }
}
```

**Response (200 OK):**
```json
{
  "results": [
    { /* result 1 */ },
    { /* result 2 */ },
    { /* result 3 */ }
  ],
  "summary": {
    "total": 3,
    "successful": 3,
    "failed": 0
  },
  "processing_time_ms": 2456
}
```

##### POST /v1/jobs
Submit an asynchronous job.

**Request:**
```json
{
  "job_type": "batch",
  "request_params": {
    "prompts": [ /* 100 prompts */ ],
    "format": "json"
  },
  "webhook_url": "https://yourapp.com/webhooks/job-complete"
}
```

**Response (202 Accepted):**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "created_at": "2025-10-13T10:30:00Z",
  "expires_at": "2025-10-14T10:30:00Z"
}
```

##### GET /v1/jobs/{id}
Get job status and results.

**Response (200 OK):**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "result": { /* batch results */ },
  "created_at": "2025-10-13T10:30:00Z",
  "started_at": "2025-10-13T10:30:05Z",
  "completed_at": "2025-10-13T10:32:15Z",
  "processing_time_ms": 130000
}
```

##### GET /v1/health
Health check endpoint.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "dependencies": {
    "redis": "up",
    "postgres": "up",
    "rabbitmq": "up",
    "gemini": "up"
  },
  "uptime_seconds": 3600
}
```

##### GET /v1/metrics
Prometheus metrics endpoint.

**Response (200 OK):**
```
# HELP requests_total Total number of requests
# TYPE requests_total counter
requests_total{method="POST",endpoint="/v1/analyze",status="200"} 1234

# HELP request_duration_seconds Request duration
# TYPE request_duration_seconds histogram
request_duration_seconds_bucket{le="0.5"} 500
request_duration_seconds_bucket{le="1.0"} 800
request_duration_seconds_bucket{le="2.0"} 950
request_duration_seconds_bucket{le="+Inf"} 1000

# HELP cache_hit_rate Cache hit rate
# TYPE cache_hit_rate gauge
cache_hit_rate 0.45
```

### 5.2 Error Responses

```json
{
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "Schema validation failed",
    "details": {
      "validation_errors": [
        {
          "path": "entities.amount",
          "message": "expected number, got string",
          "schema_path": "properties.entities.properties.amount.type"
        }
      ]
    },
    "request_id": "req_abc123",
    "timestamp": "2025-10-13T10:30:00Z"
  }
}
```

#### Error Codes
| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_REQUEST` | 400 | Malformed request body |
| `UNAUTHORIZED` | 401 | Missing or invalid API key |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `VALIDATION_FAILED` | 422 | Schema validation failed |
| `LLM_PROVIDER_ERROR` | 502 | All LLM providers failed |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

---

## 6. Infrastructure Architecture

### 6.1 Deployment Model

#### Kubernetes Architecture
```yaml
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: structured-prompt-service
  namespace: production
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: structured-prompt-service
  template:
    metadata:
      labels:
        app: structured-prompt-service
    spec:
      containers:
      - name: fastapi
        image: structured-prompt-service:1.0.0
        ports:
        - containerPort: 8000
        env:
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: redis-credentials
              key: url
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: postgres-credentials
              key: url
        - name: GEMINI_API_KEY
          valueFrom:
            secretKeyRef:
              name: llm-credentials
              key: gemini-key
        resources:
          requests:
            cpu: "500m"
            memory: "512Mi"
          limits:
            cpu: "2000m"
            memory: "2Gi"
        livenessProbe:
          httpGet:
            path: /v1/health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /v1/health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
      - name: celery-worker
        image: structured-prompt-service:1.0.0
        command: ["celery", "-A", "workers.celery_app", "worker", "--loglevel=info"]
        env:
        - name: RABBITMQ_URL
          valueFrom:
            secretKeyRef:
              name: rabbitmq-credentials
              key: url
        resources:
          requests:
            cpu: "500m"
            memory: "1Gi"
          limits:
            cpu: "2000m"
            memory: "4Gi"
---
apiVersion: v1
kind: Service
metadata:
  name: structured-prompt-service
  namespace: production
spec:
  type: LoadBalancer
  selector:
    app: structured-prompt-service
  ports:
  - protocol: TCP
    port: 443
    targetPort: 8000
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: structured-prompt-service-hpa
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: structured-prompt-service
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### 6.2 Infrastructure Diagram

```
┌────────────────────────────────────────────────────────────────────┐
│                         CLOUD PROVIDER                             │
│                    (AWS / GCP / Azure)                             │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │               Load Balancer (ALB/NLB)                    │    │
│  │  - SSL Termination                                       │    │
│  │  - Health Checks                                         │    │
│  │  - DDoS Protection (CloudFlare/AWS Shield)             │    │
│  └───────────────────────┬──────────────────────────────────┘    │
│                          │                                        │
│  ┌───────────────────────▼──────────────────────────────────┐    │
│  │          Kubernetes Cluster (EKS/GKE/AKS)                │    │
│  │                                                           │    │
│  │  ┌─────────────────────────────────────────────────┐    │    │
│  │  │  API Pods (3-20 replicas, auto-scaling)        │    │    │
│  │  │  - FastAPI service                              │    │    │
│  │  │  - 500m CPU, 512Mi RAM → 2 CPU, 2Gi RAM       │    │    │
│  │  └─────────────────────────────────────────────────┘    │    │
│  │                                                           │    │
│  │  ┌─────────────────────────────────────────────────┐    │    │
│  │  │  Worker Pods (2-10 replicas, auto-scaling)     │    │    │
│  │  │  - Celery workers                               │    │    │
│  │  │  - 500m CPU, 1Gi RAM → 2 CPU, 4Gi RAM         │    │    │
│  │  └─────────────────────────────────────────────────┘    │    │
│  │                                                           │    │
│  └───────────────────────────────────────────────────────────┘    │
│                                                                    │
│  ┌───────────────────────┐  ┌─────────────────────────────┐     │
│  │  Redis Cluster        │  │  PostgreSQL (RDS/CloudSQL)  │     │
│  │  - 3 nodes            │  │  - Master + 2 Read Replicas │     │
│  │  - 4GB RAM each       │  │  - 4 vCPU, 16GB RAM         │     │
│  │  - Persistence        │  │  - 100GB SSD storage        │     │
│  └───────────────────────┘  └─────────────────────────────┘     │
│                                                                    │
│  ┌───────────────────────────────────────────────────────────┐   │
│  │  RabbitMQ (Managed Service or Self-hosted)               │   │
│  │  - 3 node cluster                                         │   │
│  │  - 2 vCPU, 4GB RAM each                                   │   │
│  └───────────────────────────────────────────────────────────┘   │
│                                                                    │
│  ┌───────────────────────────────────────────────────────────┐   │
│  │  Monitoring Stack                                         │   │
│  │  - Prometheus (metrics collection)                        │   │
│  │  - Grafana (dashboards)                                   │   │
│  │  - ELK Stack (logs: Elasticsearch, Logstash, Kibana)     │   │
│  │  - Jaeger (distributed tracing)                           │   │
│  └───────────────────────────────────────────────────────────┘   │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### 6.3 Scaling Strategy

#### Horizontal Pod Autoscaling (HPA)
```yaml
Trigger Conditions:
- CPU > 70% → Scale up
- Memory > 80% → Scale up
- Custom metric: active_requests > 100/pod → Scale up

Scale Up:
- Add 1 pod at a time
- Wait 30 seconds between additions
- Max: 20 pods

Scale Down:
- Remove 1 pod at a time
- Wait 5 minutes between removals
- Min: 3 pods (for HA)
```

#### Vertical Scaling
```yaml
Resource Limits:
- Start: 500m CPU, 512Mi RAM
- Grow: Up to 2 CPU, 2Gi RAM per pod
- Monitor: If consistently hitting limits, increase base allocation
```

#### Database Scaling
```
PostgreSQL:
- Read Replicas: 2-5 replicas for read-heavy workloads
- Connection Pooling: PgBouncer (100 connections per instance)
- Sharding: Partition request_logs by date (monthly tables)

Redis:
- Cluster Mode: 3-6 shards for > 100GB data
- Read Replicas: 1 replica per shard for HA
- Eviction Policy: allkeys-lru (for caching use case)
```

### 6.4 High Availability & Disaster Recovery

#### Multi-AZ Deployment
```
Region: us-east-1
- AZ1: us-east-1a (API pods, Redis node, Worker pods)
- AZ2: us-east-1b (API pods, Redis node, Worker pods)
- AZ3: us-east-1c (API pods, Redis node, Worker pods)

Database:
- Primary: us-east-1a
- Standby: us-east-1b (synchronous replication)
- Read Replica: us-east-1c

RTO (Recovery Time Objective): < 5 minutes
RPO (Recovery Point Objective): < 1 minute
```

#### Backup Strategy
```
PostgreSQL:
- Automated daily backups (retained 30 days)
- Point-in-time recovery (PITR) enabled
- Backup to S3 with cross-region replication

Redis:
- RDB snapshots every 1 hour
- AOF (Append-Only File) enabled
- Backup to S3 daily

Kubernetes:
- Velero for cluster backups (daily)
- Backup etcd snapshots (hourly)
```

#### Failure Scenarios

| Scenario | Detection | Recovery | Impact |
|----------|-----------|----------|--------|
| Single pod failure | Kubernetes liveness probe | Auto-restart pod | None (load balanced) |
| Node failure | Kubernetes node status | Reschedule pods on healthy nodes | < 30s downtime for affected pods |
| AZ failure | Health checks fail for all pods in AZ | Traffic routed to other AZs | None (multi-AZ) |
| Redis failure | Connection errors | Failover to replica, promote to master | 10-30s cache unavailable, LLM fallback |
| PostgreSQL failure | Connection errors | Promote standby to primary | < 1 minute write unavailable |
| LLM provider outage | API errors from provider | Fallback to alternate provider | Latency +500ms, no downtime |

---

## 7. Security Architecture

### 7.1 Authentication & Authorization

#### API Key Management
```python
# src/core/security.py
import hashlib
import secrets
from fastapi import Security, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from repositories.api_key_repo import APIKeyRepository

security = HTTPBearer()

def generate_api_key() -> tuple[str, str]:
    """
    Generate a new API key and its hash.

    Returns:
        tuple: (api_key, key_hash)
    """
    api_key = f"sk_{''.join(secrets.token_urlsafe(32))}"
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    return api_key, key_hash

async def verify_api_key(
    credentials: HTTPAuthorizationCredentials = Security(security),
    api_key_repo: APIKeyRepository = Depends()
) -> str:
    """
    Verify API key and return key ID.
    """
    api_key = credentials.credentials
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()

    # Check cache first
    cached_key = await redis_client.get(f"apikey:{key_hash}")
    if cached_key:
        return cached_key

    # Query database
    key_record = await api_key_repo.get_by_hash(key_hash)

    if not key_record or not key_record.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive API key"
        )

    # Check expiration
    if key_record.expires_at and key_record.expires_at < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key expired"
        )

    # Cache for 5 minutes
    await redis_client.setex(f"apikey:{key_hash}", 300, str(key_record.id))

    return str(key_record.id)
```

#### Rate Limiting
```python
# src/core/rate_limiter.py
from fastapi import HTTPException, status
from redis import Redis
from datetime import datetime, timedelta

class RateLimiter:
    """
    Token bucket rate limiter using Redis.
    """

    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    async def check_rate_limit(
        self,
        api_key_id: str,
        limit: int = 1000,  # requests per hour
        window: int = 3600  # 1 hour in seconds
    ) -> None:
        """
        Check if request is within rate limit.
        Raises HTTPException if limit exceeded.
        """
        key = f"ratelimit:{api_key_id}:{datetime.now().strftime('%Y%m%d%H')}"

        # Increment counter
        current = await self.redis.incr(key)

        # Set expiration on first request
        if current == 1:
            await self.redis.expire(key, window)

        # Check limit
        if current > limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Rate limit exceeded",
                    "limit": limit,
                    "window": "1 hour",
                    "retry_after": await self.redis.ttl(key)
                }
            )
```

### 7.2 Input Validation & Sanitization

```python
# src/core/validators.py
import re
from typing import Any, Dict
from fastapi import HTTPException

class InputValidator:
    """
    Validate and sanitize user inputs.
    """

    # Disallowed patterns (SQL injection, XSS, etc.)
    DANGEROUS_PATTERNS = [
        r"(?i)(DROP|DELETE|INSERT|UPDATE|CREATE|ALTER|EXEC|EXECUTE)\s+(TABLE|DATABASE|SCHEMA)",
        r"(?i)<script[^>]*>.*?</script>",
        r"(?i)javascript:",
        r"(?i)on(load|error|click|mouse|key)\s*=",
    ]

    @classmethod
    def sanitize_prompt(cls, prompt: str) -> str:
        """
        Sanitize prompt text to prevent injection attacks.
        """
        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, prompt):
                raise HTTPException(
                    status_code=400,
                    detail="Prompt contains disallowed patterns"
                )

        # Remove null bytes
        prompt = prompt.replace("\x00", "")

        # Limit length
        if len(prompt) > 10000:
            raise HTTPException(
                status_code=400,
                detail="Prompt exceeds maximum length of 10,000 characters"
            )

        return prompt.strip()

    @classmethod
    def validate_schema(cls, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate JSON schema structure.
        """
        # Check for excessively nested schemas (DoS prevention)
        max_depth = 10
        if cls._get_schema_depth(schema) > max_depth:
            raise HTTPException(
                status_code=400,
                detail=f"Schema exceeds maximum depth of {max_depth}"
            )

        # Limit schema size
        if len(str(schema)) > 50000:
            raise HTTPException(
                status_code=400,
                detail="Schema exceeds maximum size of 50KB"
            )

        return schema

    @staticmethod
    def _get_schema_depth(schema: Dict[str, Any], current_depth: int = 0) -> int:
        """
        Calculate maximum depth of nested schema.
        """
        if not isinstance(schema, dict):
            return current_depth

        max_depth = current_depth
        for value in schema.values():
            if isinstance(value, dict):
                depth = InputValidator._get_schema_depth(value, current_depth + 1)
                max_depth = max(max_depth, depth)

        return max_depth
```

### 7.3 Data Protection

#### Secrets Management
```yaml
# Use external secret managers
# AWS Secrets Manager, GCP Secret Manager, HashiCorp Vault

Environment Variables (Injected via Kubernetes Secrets):
- GEMINI_API_KEY: [encrypted]
- ANTHROPIC_API_KEY: [encrypted]
- OPENAI_API_KEY: [encrypted]
- DATABASE_URL: [encrypted]
- REDIS_URL: [encrypted]
- RABBITMQ_URL: [encrypted]

Rotation:
- API keys: Every 90 days
- Database passwords: Every 180 days
- TLS certificates: Auto-renewed via Let's Encrypt
```

#### PII Detection & Redaction
```python
# src/utils/pii_detector.py
import re
from typing import Dict, List, Tuple

class PIIDetector:
    """
    Detect and optionally redact PII from prompts.
    """

    # Patterns for common PII
    PATTERNS = {
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "phone": r"\b(\+\d{1,3}[-.]?)?\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}\b",
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
        "credit_card": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
        "ip_address": r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
    }

    @classmethod
    def detect(cls, text: str) -> Dict[str, List[str]]:
        """
        Detect PII in text.

        Returns:
            Dict mapping PII type to list of detected values
        """
        detected = {}
        for pii_type, pattern in cls.PATTERNS.items():
            matches = re.findall(pattern, text)
            if matches:
                detected[pii_type] = matches
        return detected

    @classmethod
    def redact(cls, text: str, pii_types: List[str] = None) -> Tuple[str, Dict]:
        """
        Redact PII from text.

        Args:
            text: Input text
            pii_types: List of PII types to redact (None = all)

        Returns:
            tuple: (redacted_text, redaction_map)
        """
        if pii_types is None:
            pii_types = cls.PATTERNS.keys()

        redacted = text
        redaction_map = {}

        for pii_type in pii_types:
            if pii_type in cls.PATTERNS:
                matches = re.findall(cls.PATTERNS[pii_type], redacted)
                for i, match in enumerate(matches):
                    placeholder = f"[{pii_type.upper()}_{i+1}]"
                    redacted = redacted.replace(match, placeholder)
                    redaction_map[placeholder] = match

        return redacted, redaction_map
```

### 7.4 Audit Logging

```python
# src/utils/audit_logger.py
import logging
import json
from typing import Any, Dict
from datetime import datetime

class AuditLogger:
    """
    Log security-relevant events for compliance.
    """

    def __init__(self):
        self.logger = logging.getLogger("audit")
        self.logger.setLevel(logging.INFO)

        # JSON formatter for structured logs
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(handler)

    def log_event(
        self,
        event_type: str,
        api_key_id: str,
        details: Dict[str, Any],
        request_id: str = None
    ) -> None:
        """
        Log an audit event.
        """
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "api_key_id": api_key_id,
            "request_id": request_id,
            "details": details
        }
        self.logger.info(json.dumps(event))

# Usage examples:
audit_logger = AuditLogger()

# Log authentication attempt
audit_logger.log_event(
    "AUTH_SUCCESS",
    api_key_id="key_123",
    details={"ip": "192.168.1.1", "user_agent": "..."},
    request_id="req_abc"
)

# Log rate limit exceeded
audit_logger.log_event(
    "RATE_LIMIT_EXCEEDED",
    api_key_id="key_123",
    details={"limit": 1000, "window": "1 hour"},
    request_id="req_xyz"
)

# Log PII detection
audit_logger.log_event(
    "PII_DETECTED",
    api_key_id="key_123",
    details={"pii_types": ["email", "phone"], "redacted": True},
    request_id="req_def"
)
```

---

## 8. Performance & Scalability

### 8.1 Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| **API Latency (p95)** | < 2 seconds | From gateway to response |
| **API Latency (p99)** | < 5 seconds | From gateway to response |
| **Cache Hit Latency** | < 50ms | From gateway to response |
| **Throughput** | 10,000 req/day (Phase 1) → 100,000 req/day (Phase 3) | Daily API calls |
| **Cache Hit Rate** | > 40% | Cache hits / total requests |
| **Database Query Time** | < 100ms (p95) | PostgreSQL query execution |
| **LLM Provider Latency** | 1.5-3s (varies by provider) | External API call |
| **Error Rate** | < 1% | Failed requests / total |

### 8.2 Optimization Strategies

#### Caching Strategy
```python
# Multi-layer caching

Layer 1: In-memory (per-pod)
- LRU cache for schemas, templates
- TTL: Until pod restart
- Size: 100MB per pod

Layer 2: Redis (distributed)
- LLM responses
- TTL: 1 hour (configurable)
- Eviction: allkeys-lru

Layer 3: CDN (for static assets)
- OpenAPI spec, documentation
- TTL: 24 hours

Cache Invalidation:
- Manual: DELETE /v1/cache/{pattern}
- Automatic: On schema updates
- TTL-based: Expired keys auto-removed
```

#### Database Optimization
```sql
-- Indexes for common queries

-- Request logs: Query by API key and date
CREATE INDEX idx_request_logs_api_key_created
ON request_logs(api_key_id, created_at DESC);

-- Request logs: Query by provider and status
CREATE INDEX idx_request_logs_provider_status
ON request_logs(provider_used, validation_status);

-- Request logs: Full-text search on prompts
CREATE INDEX idx_request_logs_prompt_fts
ON request_logs USING gin(to_tsvector('english', prompt_text));

-- Schemas: Query by name
CREATE INDEX idx_schemas_name ON schemas(name);

-- Jobs: Query by status and created date
CREATE INDEX idx_jobs_status_created
ON jobs(status, created_at DESC);

-- Partitioning strategy (for scaling)
-- Partition request_logs by month
CREATE TABLE request_logs_2025_10 PARTITION OF request_logs
FOR VALUES FROM ('2025-10-01') TO ('2025-11-01');

-- Retention policy (delete old partitions)
DROP TABLE request_logs_2025_01;  -- After retention period
```

#### Connection Pooling
```python
# src/adapters/db_client.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from core.config import settings

# Create async engine with connection pooling
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=10,  # Connections per pod
    max_overflow=20,  # Extra connections when pool exhausted
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600,  # Recycle connections after 1 hour
    echo=False
)

# Session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Usage with dependency injection
async def get_db_session():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

### 8.3 Load Testing Results

#### Test Configuration
```python
# locust/locustfile.py
from locust import HttpUser, task, between

class StructuredPromptUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)  # Weight: 3x more common
    def analyze_prompt(self):
        self.client.post(
            "/v1/analyze",
            json={
                "prompt": "Extract invoice details from Invoice #12345",
                "format": "json"
            },
            headers={"Authorization": f"Bearer {self.api_key}"}
        )

    @task(1)
    def batch_analyze(self):
        self.client.post(
            "/v1/analyze/batch",
            json={
                "prompts": [f"Prompt {i}" for i in range(10)],
                "format": "json"
            },
            headers={"Authorization": f"Bearer {self.api_key}"}
        )

    def on_start(self):
        self.api_key = "sk_test_key_123"
```

#### Expected Results (Phase 1)
```
Test: 1,000 concurrent users, 10,000 requests

Without caching:
- RPS: ~50 req/s (limited by LLM provider)
- p50: 1.8s
- p95: 3.2s
- p99: 6.5s
- Error rate: 2% (provider timeouts)

With 40% cache hit rate:
- RPS: ~100 req/s
- p50: 0.8s (50% hits → 50ms, 50% misses → 1.5s)
- p95: 2.1s
- p99: 4.8s
- Error rate: 1.2%

With 60% cache hit rate:
- RPS: ~150 req/s
- p50: 0.5s
- p95: 1.8s
- p99: 3.5s
- Error rate: 0.8%
```

---

## 9. Monitoring & Observability

### 9.1 Metrics (Prometheus)

```python
# src/utils/metrics.py
from prometheus_client import Counter, Histogram, Gauge, Summary

# Request metrics
requests_total = Counter(
    "api_requests_total",
    "Total API requests",
    ["method", "endpoint", "status"]
)

request_duration = Histogram(
    "api_request_duration_seconds",
    "API request duration",
    ["method", "endpoint"],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

# LLM provider metrics
llm_requests_total = Counter(
    "llm_requests_total",
    "Total LLM provider requests",
    ["provider", "status"]
)

llm_request_duration = Histogram(
    "llm_request_duration_seconds",
    "LLM request duration",
    ["provider"],
    buckets=[0.5, 1.0, 2.0, 3.0, 5.0, 10.0]
)

llm_tokens_used = Counter(
    "llm_tokens_total",
    "Total tokens consumed",
    ["provider"]
)

# Cache metrics
cache_operations = Counter(
    "cache_operations_total",
    "Cache operations",
    ["operation", "result"]  # get/set, hit/miss
)

cache_hit_rate = Gauge(
    "cache_hit_rate",
    "Current cache hit rate"
)

# Validation metrics
validation_results = Counter(
    "validation_results_total",
    "Schema validation results",
    ["status"]  # passed/failed
)

# Database metrics
db_query_duration = Histogram(
    "db_query_duration_seconds",
    "Database query duration",
    ["query_type"],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0]
)

# System metrics
active_requests = Gauge(
    "active_requests",
    "Number of requests currently being processed"
)

# Usage in middleware
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    active_requests.inc()
    start_time = time.time()

    try:
        response = await call_next(request)

        # Record metrics
        duration = time.time() - start_time
        requests_total.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()

        request_duration.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)

        return response
    finally:
        active_requests.dec()
```

### 9.2 Logging Strategy

```python
# src/core/logging_config.py
import logging
import json
import sys
from pythonjsonlogger import jsonlogger

# Structured JSON logging
class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        log_record['timestamp'] = record.created
        log_record['level'] = record.levelname
        log_record['logger'] = record.name

        # Add contextual info if available
        if hasattr(record, 'request_id'):
            log_record['request_id'] = record.request_id
        if hasattr(record, 'api_key_id'):
            log_record['api_key_id'] = record.api_key_id

def setup_logging():
    """
    Configure logging for the application.
    """
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Console handler with JSON formatting
    console_handler = logging.StreamHandler(sys.stdout)
    formatter = CustomJsonFormatter(
        '%(timestamp)s %(level)s %(logger)s %(message)s'
    )
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Separate logger for audit events
    audit_logger = logging.getLogger("audit")
    audit_logger.setLevel(logging.INFO)
    audit_handler = logging.StreamHandler(sys.stdout)
    audit_handler.setFormatter(formatter)
    audit_logger.addHandler(audit_handler)

# Example log messages
logger = logging.getLogger(__name__)

# Info log
logger.info(
    "Processing prompt",
    extra={
        "request_id": "req_abc123",
        "api_key_id": "key_456",
        "prompt_length": 150,
        "provider": "gemini"
    }
)

# Error log
logger.error(
    "LLM provider failed",
    extra={
        "request_id": "req_abc123",
        "provider": "gemini",
        "error": "Timeout after 10s"
    },
    exc_info=True
)
```

### 9.3 Distributed Tracing (OpenTelemetry)

```python
# src/core/tracing.py
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

def setup_tracing(app):
    """
    Configure distributed tracing with Jaeger.
    """
    # Set up tracer provider
    trace.set_tracer_provider(TracerProvider())
    tracer = trace.get_tracer(__name__)

    # Jaeger exporter
    jaeger_exporter = JaegerExporter(
        agent_host_name="jaeger",
        agent_port=6831,
    )

    # Span processor
    span_processor = BatchSpanProcessor(jaeger_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)

    # Auto-instrument FastAPI
    FastAPIInstrumentor.instrument_app(app)

    # Auto-instrument HTTP requests (for LLM calls)
    RequestsInstrumentor().instrument()

    # Auto-instrument SQLAlchemy
    SQLAlchemyInstrumentor().instrument()

    return tracer

# Manual tracing for custom operations
tracer = trace.get_tracer(__name__)

async def process_prompt(prompt: str):
    with tracer.start_as_current_span("process_prompt") as span:
        span.set_attribute("prompt_length", len(prompt))

        # Language detection span
        with tracer.start_as_current_span("detect_language"):
            language = await detect_language(prompt)
            span.set_attribute("language", language)

        # LLM call span
        with tracer.start_as_current_span("llm_request") as llm_span:
            llm_span.set_attribute("provider", "gemini")
            response = await llm_router.route(prompt)
            llm_span.set_attribute("tokens_used", response.tokens_used)

        # Validation span
        with tracer.start_as_current_span("validate_response"):
            validation = validator.validate(response)
            span.set_attribute("validation_passed", validation.passed)

        return response
```

### 9.4 Dashboards (Grafana)

#### Dashboard 1: System Overview
```
Panels:
1. Request Rate (requests/second)
   - Query: rate(api_requests_total[5m])
   - Visualization: Time series graph

2. Error Rate (%)
   - Query: (rate(api_requests_total{status=~"5.."}[5m]) / rate(api_requests_total[5m])) * 100
   - Visualization: Time series graph
   - Alert: > 1% for 5 minutes

3. Latency (p50, p95, p99)
   - Query: histogram_quantile(0.95, rate(api_request_duration_seconds_bucket[5m]))
   - Visualization: Time series graph
   - Alert: p95 > 2s for 5 minutes

4. Cache Hit Rate (%)
   - Query: (cache_operations_total{result="hit"} / cache_operations_total) * 100
   - Visualization: Gauge
   - Target: > 40%

5. Active Requests
   - Query: active_requests
   - Visualization: Gauge
```

#### Dashboard 2: LLM Provider Performance
```
Panels:
1. Requests by Provider
   - Query: sum by (provider) (rate(llm_requests_total[5m]))
   - Visualization: Stacked area chart

2. Provider Latency Comparison
   - Query: histogram_quantile(0.95, rate(llm_request_duration_seconds_bucket[5m])) by (provider)
   - Visualization: Bar chart

3. Token Usage by Provider
   - Query: sum by (provider) (rate(llm_tokens_total[1h]))
   - Visualization: Pie chart

4. Provider Error Rate
   - Query: rate(llm_requests_total{status="error"}[5m]) by (provider)
   - Visualization: Time series graph
```

#### Dashboard 3: Business Metrics
```
Panels:
1. Daily Request Volume
   - Query: sum(increase(api_requests_total[24h]))
   - Visualization: Single stat

2. Top API Keys by Usage
   - Query: topk(10, sum by (api_key_id) (rate(api_requests_total[24h])))
   - Visualization: Table

3. Cost Savings from Cache
   - Calculation: cache_hit_rate * daily_requests * avg_llm_cost
   - Visualization: Single stat

4. Validation Pass Rate
   - Query: (validation_results_total{status="passed"} / validation_results_total) * 100
   - Visualization: Gauge
   - Target: > 95%
```

### 9.5 Alerting Rules

```yaml
# alertmanager/alerts.yaml
groups:
  - name: api_alerts
    interval: 30s
    rules:
      # High error rate
      - alert: HighErrorRate
        expr: (rate(api_requests_total{status=~"5.."}[5m]) / rate(api_requests_total[5m])) > 0.01
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High API error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }}"

      # High latency
      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(api_request_duration_seconds_bucket[5m])) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "API latency above SLA"
          description: "p95 latency is {{ $value }}s (target: <2s)"

      # Low cache hit rate
      - alert: LowCacheHitRate
        expr: cache_hit_rate < 0.3
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "Cache hit rate below target"
          description: "Cache hit rate is {{ $value | humanizePercentage }} (target: >40%)"

      # LLM provider down
      - alert: LLMProviderDown
        expr: rate(llm_requests_total{status="error"}[5m]) > 0.5
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "LLM provider experiencing high error rate"
          description: "{{ $labels.provider }} error rate: {{ $value | humanizePercentage }}"

      # Database connection issues
      - alert: DatabaseConnectionIssues
        expr: rate(db_query_duration_seconds_count{status="error"}[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Database connection errors detected"

      # Pod restarts
      - alert: FrequentPodRestarts
        expr: rate(kube_pod_container_status_restarts_total[15m]) > 0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Pods restarting frequently"
```

---

## 10. Technology Stack Summary

### 10.1 Complete Technology List

| Layer | Technology | Version | Purpose | Alternatives Considered |
|-------|-----------|---------|---------|------------------------|
| **API Framework** | FastAPI | 0.104+ | REST API server | Flask (less async), Django (heavier) |
| **Language** | Python | 3.11+ | Application code | Go (steeper learning curve), Node.js (less LLM libs) |
| **Validation** | Pydantic | 2.5+ | Request/response validation | marshmallow, dataclasses |
| | jsonschema | 4.20+ | JSON Schema validation | - |
| **LLM Client** | LiteLLM | 1.20+ | Multi-provider abstraction | Direct API clients (more code) |
| **Cache** | Redis | 7.2+ | Response caching, rate limiting | Memcached (less features), DragonflyDB |
| **Database** | PostgreSQL | 15+ | Persistent storage | MySQL (less JSON support), MongoDB (schema management harder) |
| **Message Queue** | RabbitMQ | 3.12+ | Async job queue | Kafka (overkill), SQS (vendor lock-in) |
| **Task Queue** | Celery | 5.3+ | Background workers | RQ (simpler, less features), Dramatiq |
| **Web Server** | Uvicorn | 0.24+ | ASGI server | Gunicorn + uvicorn workers, Hypercorn |
| **API Gateway** | Nginx + Kong | Latest | Routing, auth, rate limiting | AWS API Gateway, Traefik, Envoy |
| **Container** | Docker | 24+ | Containerization | Podman |
| **Orchestration** | Kubernetes | 1.28+ | Container orchestration | Docker Swarm (less adoption), ECS/Fargate |
| **IaC** | Terraform | 1.6+ | Infrastructure as code | Pulumi, CloudFormation, Ansible |
| **Metrics** | Prometheus | 2.48+ | Metrics collection | InfluxDB, Datadog |
| **Dashboards** | Grafana | 10.2+ | Visualization | Kibana, Datadog |
| **Logging** | ELK Stack | 8.11+ | Log aggregation | Loki, Splunk, CloudWatch |
| | Filebeat | 8.11+ | Log shipping | Fluentd, Logstash |
| **Tracing** | OpenTelemetry | 1.21+ | Distributed tracing | - |
| | Jaeger | 1.51+ | Trace storage/visualization | Zipkin, Tempo |
| **Testing** | pytest | 7.4+ | Unit/integration tests | unittest |
| | locust | 2.17+ | Load testing | JMeter, k6, Gatling |
| **CI/CD** | GitHub Actions | - | Automation | GitLab CI, CircleCI, Jenkins |
| **Documentation** | MkDocs | 1.5+ | Documentation site | Sphinx, Docusaurus |
| | Swagger UI | 5.9+ | API documentation (auto-generated) | Redoc, RapiDoc |

### 10.2 Rationale for Key Choices

**FastAPI over Flask/Django:**
- Native async/await support (critical for I/O-bound LLM calls)
- Automatic OpenAPI docs generation
- Built-in Pydantic validation
- Performance comparable to Node.js/Go

**LiteLLM over Direct APIs:**
- Unified interface for 50+ providers
- Built-in retry, fallback, load balancing
- Easy to add new providers without code changes
- Cost tracking and budgeting features

**PostgreSQL over MongoDB:**
- ACID guarantees for request logs and schemas
- Native JSON support (JSONB) for flexibility
- Mature ecosystem and tooling
- Better for structured data with relationships

**Redis over Memcached:**
- Persistence options (RDB, AOF)
- Rich data structures (hashes, lists, sets)
- Pub/sub for cache invalidation
- Lua scripting for complex operations

**Kubernetes over Docker Swarm:**
- Industry standard with massive ecosystem
- Rich feature set (auto-scaling, rollouts, service mesh)
- Cloud-agnostic (EKS, GKE, AKS)
- Better for long-term scalability

---

## 11. Implementation Considerations

### 11.1 Development Phases

#### Phase 1: Foundation (Weeks 1-2)
**Goal**: Working MVP with core functionality

**Components to Build:**
1. FastAPI service with `/v1/analyze` endpoint
2. Basic LLM integration (Gemini only)
3. JSON Schema validation (Pydantic + jsonschema)
4. Redis caching (basic)
5. PostgreSQL setup (request logs, API keys)
6. Docker containerization
7. Basic Prometheus metrics
8. Health check endpoint

**Success Criteria:**
- API accepts requests and returns structured JSON
- 90%+ validation pass rate on test prompts
- Docker image builds and runs
- Metrics endpoint exposes basic stats

**Estimated Effort**: 80 hours (2 weeks × 1 engineer)

#### Phase 2: Production Hardening (Weeks 3-4)
**Goal**: Production-ready with SLAs

**Components to Build:**
1. API key authentication system
2. Rate limiting (Redis-based)
3. Advanced error handling + retry logic
4. Grafana dashboards
5. Alerting rules (Alertmanager)
6. Load testing (Locust)
7. Security audit + penetration testing
8. Kubernetes deployment manifests

**Success Criteria:**
- 99.9% uptime during testing period
- p95 latency < 2s under load
- Security vulnerabilities addressed
- Passing load test (1000 concurrent users)

**Estimated Effort**: 80 hours (2 weeks × 1 engineer)

#### Phase 3: Advanced Features (Weeks 5-8)
**Goal**: Multi-provider intelligence

**Components to Build:**
1. LiteLLM integration (Claude, GPT-4, Llama)
2. Intelligent provider routing
3. Batch processing API (`/v1/analyze/batch`)
4. Async job processing (Celery workers)
5. Python SDK
6. Schema registry (`/v1/schemas`)
7. Prompt template library
8. OpenTelemetry tracing

**Success Criteria:**
- 3+ LLM providers integrated with fallback
- Batch processing 2x faster than sequential
- Python SDK published to PyPI
- Distributed tracing working end-to-end

**Estimated Effort**: 160 hours (4 weeks × 1-2 engineers)

#### Phase 4: Ecosystem (Weeks 9-12)
**Goal**: Full platform with integrations

**Components to Build:**
1. JavaScript/TypeScript SDK
2. Web UI dashboard (prompt tester, analytics)
3. Webhook notifications
4. CLI tool (for testing/debugging)
5. Data pipeline integrations (Airflow, Kafka)
6. PII detection and redaction
7. Cost optimization tools
8. Comprehensive documentation site (MkDocs)

**Success Criteria:**
- 5+ internal apps integrated
- Developer NPS > 50
- 10,000+ requests/day
- Full documentation published

**Estimated Effort**: 160 hours (4 weeks × 2 engineers)

### 11.2 Deployment Strategy

#### Environments
```
1. Development (local)
   - Docker Compose
   - Local PostgreSQL, Redis
   - Mock LLM providers (for testing without API costs)

2. Staging (cloud)
   - Kubernetes cluster (single-zone)
   - Managed PostgreSQL, Redis
   - Real LLM providers (low rate limits)
   - Purpose: Integration testing, demo

3. Production (cloud)
   - Kubernetes cluster (multi-zone)
   - Managed PostgreSQL (with replicas), Redis (cluster mode)
   - Real LLM providers (full rate limits)
   - Purpose: Live traffic
```

#### CI/CD Pipeline
```
GitHub Push → GitHub Actions
  ↓
1. Linting (flake8, black, mypy)
  ↓
2. Unit Tests (pytest) + Coverage Check (>80%)
  ↓
3. Integration Tests (pytest with Docker Compose)
  ↓
4. Build Docker Image
  ↓
5. Push to Container Registry (Docker Hub, ECR, GCR)
  ↓
6. Deploy to Staging (Kubernetes)
  ↓
7. Smoke Tests (basic API checks)
  ↓
8. Manual Approval (for production)
  ↓
9. Deploy to Production (Rolling Update)
  ↓
10. Health Checks + Rollback on Failure
```

### 11.3 Testing Strategy

#### Unit Tests
```python
# tests/test_prompt_processor.py
import pytest
from services.prompt_processor import PromptProcessor

@pytest.fixture
def processor():
    return PromptProcessor()

def test_language_detection(processor):
    assert processor.detect_language("Hello world") == "en"
    assert processor.detect_language("Bonjour le monde") == "fr"
    assert processor.detect_language("Hola mundo") == "es"

def test_sanitize_prompt(processor):
    # Should remove dangerous patterns
    with pytest.raises(ValueError):
        processor.sanitize("DROP TABLE users;")

    # Should allow safe prompts
    result = processor.sanitize("Extract invoice details")
    assert result == "Extract invoice details"

def test_meta_prompt_generation(processor):
    prompt = processor.generate_meta_prompt(
        "Translate 'Hello' to Spanish",
        schema=None
    )
    assert "intent" in prompt
    assert "entities" in prompt
    assert "JSON" in prompt
```

#### Integration Tests
```python
# tests/test_api_integration.py
import pytest
from fastapi.testclient import TestClient
from main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer sk_test_key"}

def test_analyze_endpoint(client, auth_headers):
    response = client.post(
        "/v1/analyze",
        json={"prompt": "Extract details from Invoice #12345"},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "intent" in data
    assert "subject" in data
    assert "entities" in data
    assert data["validation_status"] == "passed"

def test_rate_limiting(client, auth_headers):
    # Make 1001 requests (exceeds limit of 1000/hour)
    for i in range(1001):
        response = client.post(
            "/v1/analyze",
            json={"prompt": f"Test {i}"},
            headers=auth_headers
        )
        if i < 1000:
            assert response.status_code == 200
        else:
            assert response.status_code == 429
            assert "rate limit" in response.json()["error"].lower()
```

#### Load Tests
```python
# locust/load_test.py
from locust import HttpUser, task, between

class LoadTest(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.api_key = "sk_test_key"

    @task(10)  # 10x more common than batch
    def analyze_single(self):
        self.client.post(
            "/v1/analyze",
            json={
                "prompt": "Extract invoice details from Invoice #12345",
                "format": "json"
            },
            headers={"Authorization": f"Bearer {self.api_key}"}
        )

    @task(1)
    def analyze_batch(self):
        self.client.post(
            "/v1/analyze/batch",
            json={
                "prompts": [f"Prompt {i}" for i in range(5)],
                "format": "json"
            },
            headers={"Authorization": f"Bearer {self.api_key}"}
        )

# Run with: locust -f locust/load_test.py --host=https://api-staging.company.com
```

---

## 12. Risk Assessment & Mitigation

### 12.1 Technical Risks

| Risk | Likelihood | Impact | Mitigation | Owner |
|------|-----------|--------|------------|-------|
| **LLM provider outages** | Medium | High | Multi-provider fallback, 60%+ cache hit rate, circuit breakers | Backend Team |
| **Schema validation failures** | Medium | Medium | Graceful degradation, retry with relaxed schema, human review queue | Backend Team |
| **Performance degradation under load** | Low | High | Load testing, auto-scaling (HPA), CDN for static content | DevOps Team |
| **Database bottlenecks** | Medium | Medium | Read replicas, connection pooling, query optimization, partitioning | Database Team |
| **Redis cache failures** | Low | Medium | Redis cluster with replication, graceful fallback to LLM on cache miss | Backend Team |
| **Security vulnerabilities** | Low | Critical | Regular audits, penetration testing, automated vulnerability scanning | Security Team |
| **Kubernetes cluster issues** | Low | High | Multi-AZ deployment, regular backups, disaster recovery plan | DevOps Team |

### 12.2 Business Risks

| Risk | Likelihood | Impact | Mitigation | Owner |
|------|-----------|--------|------------|-------|
| **Low adoption** | Medium | High | Strong documentation, SDKs, pilot programs, developer evangelism | Product Team |
| **Cost overruns** | Medium | High | Budget alerts (80%, 100%), aggressive caching, rate limiting | Finance + Product |
| **Competitive alternatives emerge** | Low | Medium | Differentiate with schema validation, multi-LLM, reliability | Product Team |
| **Vendor lock-in concerns** | Low | Medium | Abstract provider interface, open standards (JSON Schema, OpenAPI) | Architecture Team |
| **Data privacy/compliance issues** | Low | Critical | PII detection/redaction, compliance review (GDPR, CCPA), audit logging | Legal + Security |
| **Team capacity constraints** | Medium | Medium | Prioritize MVP features, hire contractors if needed, phased rollout | Engineering Manager |

---

## 13. Appendices

### Appendix A: Glossary

| Term | Definition |
|------|------------|
| **API Gateway** | Entry point for all client requests, handling auth, rate limiting, routing |
| **Cache Hit Rate** | Percentage of requests served from cache vs. requiring LLM API call |
| **Entity Extraction** | Identifying and extracting key pieces of information from text |
| **HPA** | Horizontal Pod Autoscaler - Kubernetes feature for auto-scaling pods |
| **Intent** | The primary action a user wants to perform (create, analyze, translate, etc.) |
| **JSON Schema** | Specification for describing JSON data structure and validation rules |
| **LiteLLM** | Open-source library providing unified interface for multiple LLM providers |
| **Meta-Prompt** | System prompt sent to LLM instructing how to extract structured data |
| **p95 Latency** | 95th percentile latency - 95% of requests complete faster than this |
| **Provider** | LLM API service (Gemini, Claude, GPT-4, Llama, etc.) |
| **RTO** | Recovery Time Objective - Maximum acceptable downtime |
| **RPO** | Recovery Point Objective - Maximum acceptable data loss |
| **Schema Validation** | Process of verifying LLM outputs conform to predefined JSON schemas |
| **SLA** | Service Level Agreement - Commitment to uptime, latency, etc. |
| **Structured Prompting** | Technique of extracting structured data (JSON/XML) from natural language using LLMs |

### Appendix B: API Request/Response Examples

See section 5.1 (REST API Specification) for detailed examples.

### Appendix C: Infrastructure Cost Estimates

**Monthly Infrastructure Costs (Production at 10,000 req/day):**

| Component | Specifications | Monthly Cost |
|-----------|---------------|--------------|
| **Kubernetes** | 5 nodes (3 API, 2 workers), 4 vCPU, 16GB RAM each | $400 |
| **PostgreSQL** | 4 vCPU, 16GB RAM, 100GB SSD, 2 read replicas | $250 |
| **Redis** | 3-node cluster, 4GB RAM each | $150 |
| **RabbitMQ** | 3-node cluster, 2 vCPU, 4GB RAM each | $100 |
| **Load Balancer** | Application Load Balancer | $30 |
| **Monitoring** | Prometheus + Grafana + ELK Stack | $100 |
| **LLM API Calls** | 300K requests/month, 50% cache hit = 150K LLM calls @ $0.015/call | $2,250 |
| **Data Transfer** | 500GB outbound | $50 |
| **Backups & Storage** | S3 for backups, 200GB | $20 |
| **Total** | | **$3,350/month** |

**With 60% cache hit rate**: ~$2,600/month (40% reduction in LLM costs)

**At scale (100,000 req/day)**: ~$15,000/month (with optimizations)

### Appendix D: Reference Architecture Diagram

See section 2.1 (High-Level Architecture) for complete diagram.

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-10-13 | AI Architect | Initial architecture document |

---

**End of Architecture Document**

This architecture provides a comprehensive blueprint for building a production-grade Structured Prompt Service Platform. All major design decisions are documented with clear rationale, enabling the development team to implement the system confidently and consistently.
