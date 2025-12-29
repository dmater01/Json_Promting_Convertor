# Structured Prompt Service Platform

Production-grade API service that transforms natural language prompts into validated structured data using Large Language Models (LLMs).

## Overview

The Structured Prompt Service Platform is a cloud-native, microservices-based API that provides:

- **Structured Data Extraction**: Convert natural language to validated JSON/XML
- **Multi-Provider Support**: Intelligent routing across Gemini, Claude, GPT-4, and Llama
- **High Reliability**: 99.9% uptime SLA with 95%+ validation pass rate
- **Performance**: Sub-2-second p95 latency with 40%+ cache hit rate
- **Cost Optimization**: 40-60% cost reduction through intelligent caching

## Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Json_Promtpting_App
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements-dev.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

5. **Start services with Docker Compose**:
   ```bash
   docker-compose up -d
   ```

6. **Run database migrations**:
   ```bash
   alembic upgrade head
   ```

7. **Start the API server**:
   ```bash
   uvicorn src.main:app --reload
   ```

8. **Access the API**:
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs
   - Metrics: http://localhost:8000/v1/metrics

## Project Structure

```
Json_Promtpting_App/
├── src/
│   ├── api/              # API endpoints and routes
│   │   └── v1/           # API version 1
│   ├── core/             # Core configuration and utilities
│   ├── services/         # Business logic services
│   ├── models/           # Pydantic and SQLAlchemy models
│   ├── repositories/     # Data access layer
│   ├── adapters/         # External service adapters
│   ├── utils/            # Utility functions
│   └── workers/          # Celery workers
├── tests/
│   ├── unit/             # Unit tests
│   └── integration/      # Integration tests
├── docs/                 # Documentation
│   ├── architecture/     # Architecture documentation
│   ├── PRD_STRUCTURED_PROMPT_SERVICE.md
│   ├── ARCHITECTURE.md
│   ├── EPICS_AND_STORIES.md
│   └── MASTER_CHECKLIST.md
├── docker-compose.yml    # Docker services
├── Dockerfile            # Application container
├── pyproject.toml        # Project configuration
└── requirements.txt      # Python dependencies
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_prompt_processor.py
```

### Code Quality

```bash
# Format code with Black
black src/ tests/

# Lint with Flake8
flake8 src/ tests/

# Type check with mypy
mypy src/

# Run all checks (pre-commit)
pre-commit run --all-files
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## API Usage

### Basic Example

```bash
curl -X POST http://localhost:8000/v1/analyze \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Extract invoice details from: Invoice #12345, Date: 2025-01-15, Amount: $1,250.00",
    "format": "json"
  }'
```

### Response

```json
{
  "intent": "extract",
  "subject": "invoice details",
  "entities": {
    "key_details": ["invoice_number: 12345", "date: 2025-01-15", "amount: 1250.00"],
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

## Documentation

- **[Product Requirements](docs/PRD_STRUCTURED_PROMPT_SERVICE.md)**: Complete PRD with use cases and requirements
- **[Architecture](docs/ARCHITECTURE.md)**: Detailed system architecture (140+ pages)
- **[Architecture Overview](docs/architecture/01-overview.md)**: High-level architecture summary
- **[Component Architecture](docs/architecture/02-components.md)**: Detailed component designs
- **[Epics & Stories](docs/EPICS_AND_STORIES.md)**: 12 epics with 100+ user stories
- **[Master Checklist](docs/MASTER_CHECKLIST.md)**: 200+ implementation tasks

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **API Framework** | FastAPI | REST API with async support |
| **Language** | Python 3.11+ | Application code |
| **Validation** | Pydantic v2 + jsonschema | Request/response validation |
| **LLM Client** | LiteLLM | Multi-provider abstraction |
| **Cache** | Redis 7+ | Response caching |
| **Database** | PostgreSQL 15+ | Persistent storage |
| **Message Queue** | RabbitMQ | Async job queue |
| **Task Queue** | Celery | Background workers |
| **Container** | Docker | Containerization |
| **Orchestration** | Kubernetes | Container orchestration |
| **Metrics** | Prometheus | Metrics collection |
| **Dashboards** | Grafana | Visualization |
| **Tracing** | OpenTelemetry + Jaeger | Distributed tracing |

## Deployment

### Docker Compose (Development)

```bash
docker-compose up -d
```

### Kubernetes (Production)

```bash
# Apply Kubernetes manifests
kubectl apply -f kubernetes/

# Check deployment status
kubectl get pods -n production

# View logs
kubectl logs -f deployment/structured-prompt-service -n production
```

## Monitoring

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)
- **Jaeger**: http://localhost:16686

## Contributing

1. Create a feature branch (`git checkout -b feature/amazing-feature`)
2. Make your changes
3. Run tests (`pytest`)
4. Run code quality checks (`pre-commit run --all-files`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Development Roadmap

### Phase 1: Foundation - MVP (Weeks 1-2) ✅
- Core API with /v1/analyze endpoint
- Basic LLM integration (Gemini)
- Schema validation
- Redis caching
- Monitoring basics

### Phase 2: Production Hardening (Weeks 3-4) 🔄
- API key authentication
- Rate limiting
- Kubernetes deployment
- Load testing
- Security audit

### Phase 3: Advanced Features (Weeks 5-8) 📝
- Multi-LLM support (Claude, GPT-4)
- Batch processing
- Python & JavaScript SDKs
- Distributed tracing

### Phase 4: Ecosystem (Weeks 9-12) 📝
- Web UI dashboard
- CLI tool
- Data pipeline integrations
- Documentation site

## License

MIT License - see LICENSE file for details

## Support

- **Issues**: [GitHub Issues](https://github.com/your-org/structured-prompt-service/issues)
- **Documentation**: [Full Docs](docs/)
- **Slack**: #structured-prompt-service

## Acknowledgments

Built with the BMad Method for structured product development.

---

**Status**: 🚧 In Development (Phase 1)
**Version**: 0.1.0
**Last Updated**: 2025-10-13
