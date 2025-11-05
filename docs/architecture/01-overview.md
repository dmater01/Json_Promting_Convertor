# Architecture Overview
## Structured Prompt Service Platform

**Version**: 1.0
**Last Updated**: 2025-10-13
**Part**: 1 of 8
**Related**: [Complete Architecture](../ARCHITECTURE.md) | [PRD](../PRD_STRUCTURED_PROMPT_SERVICE.md)

---

## Executive Summary

The Structured Prompt Service Platform is a **cloud-native, microservices-based API platform** that transforms natural language prompts into validated structured data using Large Language Models (LLMs).

### Architectural Approach

**Design Philosophy**: Cloud-native, microservices-based, API-first

**Key Principles**:
- **Reliability**: Multi-layer validation, caching, and fallback mechanisms
- **Performance**: Sub-2-second p95 latency through intelligent caching
- **Scalability**: Horizontal scaling via containerization and stateless services
- **Extensibility**: Provider-agnostic LLM abstraction supporting multiple vendors
- **Observability**: Comprehensive monitoring, tracing, and alerting

---

## High-Level System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                            │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐   │
│  │ Web Apps     │  │ Mobile Apps  │  │ Internal Services  │   │
│  └──────┬───────┘  └──────┬───────┘  └─────────┬──────────┘   │
└─────────┼──────────────────┼─────────────────────┼──────────────┘
          │                  │                     │
          └──────────────────┴─────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API GATEWAY LAYER                          │
│  • TLS Termination          • Rate Limiting                     │
│  • API Key Authentication   • Request Validation                │
└─────────────────────────────┬───────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
              ▼                               ▼
┌─────────────────────────┐      ┌──────────────────────────┐
│   SYNCHRONOUS API       │      │   ASYNCHRONOUS WORKER    │
│   (FastAPI Service)     │      │   (Celery Workers)       │
└───────────┬─────────────┘      └─────────────┬────────────┘
            │                                  │
            └──────────────┬───────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                     CORE SERVICE LAYER                          │
│  ┌────────────────┐  ┌─────────────┐  ┌──────────────────┐    │
│  │ Prompt         │  │ Schema      │  │ LLM Router       │    │
│  │ Processor      │  │ Validator   │  │                  │    │
│  └────────────────┘  └─────────────┘  └──────────────────┘    │
└───────────┬─────────────────────┬────────────────────┬─────────┘
            │                     │                    │
    ┌───────▼────────┐   ┌────────▼────────┐   ┌─────▼──────────┐
    │  CACHE LAYER   │   │   DATA STORE    │   │  LLM PROVIDERS │
    │  (Redis)       │   │   (PostgreSQL)  │   │  • Gemini      │
    │                │   │                 │   │  • Claude      │
    │                │   │                 │   │  • GPT-4       │
    └────────────────┘   └─────────────────┘   └────────────────┘
```

---

## Component Overview

### Client Layer
- **Web Applications**: Browser-based interfaces
- **Mobile Apps**: iOS/Android applications
- **Internal Services**: Backend microservices
- **Data Pipelines**: Kafka, Airflow, etc.

### API Gateway
- **Purpose**: Single entry point for all requests
- **Responsibilities**:
  - TLS termination
  - Authentication (API key validation)
  - Rate limiting
  - Request validation
  - Circuit breaking
- **Technology**: Nginx + Kong / AWS API Gateway

### Synchronous API Service
- **Purpose**: Handle real-time requests
- **Responsibilities**:
  - Request processing
  - LLM interaction
  - Response validation
  - Caching
- **Technology**: FastAPI + Python 3.11+
- **Scaling**: 3-20 pods (auto-scaling)

### Asynchronous Workers
- **Purpose**: Handle batch and long-running jobs
- **Responsibilities**:
  - Batch processing
  - Async job execution
  - Webhook delivery
- **Technology**: Celery + RabbitMQ
- **Scaling**: 2-10 workers (auto-scaling)

### Core Service Layer
- **Prompt Processor**: Preprocessing and meta-prompt generation
- **Schema Validator**: JSON Schema validation
- **LLM Router**: Multi-provider routing and fallback

### Data Layer
- **Cache (Redis)**: Response caching, rate limits, sessions
- **Database (PostgreSQL)**: Request logs, schemas, API keys
- **Message Queue (RabbitMQ)**: Async job queue

### LLM Providers
- Google Gemini
- Anthropic Claude
- OpenAI GPT-4
- Meta Llama

---

## Data Flow

### Synchronous Request Flow

```
1. Client → API Gateway
   - Authenticate via API key
   - Rate limit check
   - Input validation

2. API Gateway → Core Service
   - Cache lookup (Redis)
   - If HIT: return cached response (10-50ms)
   - If MISS: proceed to LLM

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

Latency (cache miss): 1.5-2.5s
Latency (cache hit): 10-50ms
```

### Asynchronous Job Flow

```
1. Client → API Gateway → Job Queue
   - Submit job with webhook URL
   - Return job_id immediately (< 100ms)

2. Worker → Job Queue
   - Pick up job from queue
   - Process (potentially long-running)

3. Worker → Client Webhook
   - POST results to callback URL
   - Retry on failure (exponential backoff)

4. Client → GET /v1/jobs/{id}
   - Poll for status updates (optional)
   - Retrieve results when complete
```

---

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **API Framework** | FastAPI | REST API server with async support |
| **Language** | Python 3.11+ | Application code |
| **Validation** | Pydantic v2 + jsonschema | Request/response validation |
| **LLM Client** | LiteLLM | Multi-provider abstraction |
| **Cache** | Redis 7+ | Response caching, rate limiting |
| **Database** | PostgreSQL 15+ | Persistent storage |
| **Message Queue** | RabbitMQ | Async job queue |
| **Task Queue** | Celery | Background workers |
| **Container** | Docker | Containerization |
| **Orchestration** | Kubernetes | Container orchestration |
| **Metrics** | Prometheus | Metrics collection |
| **Dashboards** | Grafana | Visualization |
| **Logging** | ELK Stack | Log aggregation |
| **Tracing** | OpenTelemetry + Jaeger | Distributed tracing |

---

## Key Design Decisions

### 1. FastAPI over Flask/Django
**Rationale**:
- Native async/await support (critical for I/O-bound LLM calls)
- Automatic OpenAPI docs generation
- Built-in Pydantic validation
- Performance comparable to Node.js/Go

### 2. LiteLLM over Direct APIs
**Rationale**:
- Unified interface for 50+ providers
- Built-in retry, fallback, load balancing
- Easy to add new providers without code changes
- Cost tracking and budgeting features

### 3. PostgreSQL over MongoDB
**Rationale**:
- ACID guarantees for request logs and schemas
- Native JSON support (JSONB) for flexibility
- Mature ecosystem and tooling
- Better for structured data with relationships

### 4. Redis over Memcached
**Rationale**:
- Persistence options (RDB, AOF)
- Rich data structures (hashes, lists, sets)
- Pub/sub for cache invalidation
- Lua scripting for complex operations

### 5. Kubernetes over Docker Swarm
**Rationale**:
- Industry standard with massive ecosystem
- Rich feature set (auto-scaling, rollouts, service mesh)
- Cloud-agnostic (EKS, GKE, AKS)
- Better for long-term scalability

---

## Non-Functional Requirements

### Performance
- **API Latency (p95)**: < 2 seconds
- **API Latency (p99)**: < 5 seconds
- **Cache Hit Latency**: < 50ms
- **Throughput**: 10,000 req/day (Phase 1) → 100,000+ req/day (Phase 3)
- **Cache Hit Rate**: > 40%

### Reliability
- **Uptime SLA**: 99.9%
- **Validation Pass Rate**: > 95%
- **Error Rate**: < 1%
- **Automatic Retry**: Exponential backoff
- **Circuit Breakers**: For dependent services

### Security
- API key authentication
- Rate limiting (1000 req/hour default)
- Input sanitization
- TLS 1.3 for all communications
- Secrets management
- PII detection and redaction (optional)
- Audit logging

### Scalability
- Horizontal pod autoscaling (3-20 pods)
- Database read replicas
- Redis cluster mode
- Multi-region support (future)

---

## Architecture Highlights

### Multi-Layer Caching Strategy
```
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
```

### Provider Routing Strategies
1. **Least Busy** (default): Route to provider with fewest active requests
2. **Cost-Based**: Route to cheapest provider (Gemini → Claude → GPT-4)
3. **Latency-Based**: Route to fastest provider based on historical p95
4. **Quality-Based**: Route complex prompts to better models

### Observability Stack
- **Metrics**: Prometheus (15s scrape interval)
- **Dashboards**: Grafana (3 core dashboards)
- **Logging**: ELK Stack (structured JSON logs)
- **Tracing**: OpenTelemetry + Jaeger (distributed tracing)
- **Alerting**: Alertmanager + PagerDuty

---

## Related Documents

- **[Component Architecture](02-components.md)**: Detailed component designs
- **[Data Architecture](03-data.md)**: Database schemas and data models
- **[API Design](04-api.md)**: REST API specifications
- **[Infrastructure](05-infrastructure.md)**: Kubernetes and cloud deployment
- **[Security](06-security.md)**: Security architecture and controls
- **[Monitoring](07-monitoring.md)**: Observability and alerting
- **[Implementation](08-implementation.md)**: Development phases and guidance

---

## Next Steps

1. Review [Component Architecture](02-components.md) for detailed service designs
2. Review [Data Architecture](03-data.md) for database schemas
3. Review [API Design](04-api.md) for endpoint specifications
4. Review [Implementation Guide](08-implementation.md) for development phases
