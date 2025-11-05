# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an experimental research project comparing Natural Language (NL), JSON, and XML structured prompting techniques for LLMs. The codebase contains CLI tools that analyze natural language prompts using the Google Gemini API and extract structured information into JSON or XML formats.

The project demonstrates how structured prompting (JSON/XML) provides higher reliability and precision compared to natural language prompting, though at the cost of increased verbosity and token usage.

## Project Status

**Current Phase**: Planning for Production Service
- Research/prototype phase complete with CLI tools validated
- Production planning documents created (PRD, Integration Guide, BMAD Implementation Plan)
- Transitioning from research codebase to production API service
- See `PRD_STRUCTURED_PROMPT_SERVICE.md` for production requirements

## Context for AI Assistants

This project started as research comparing NL vs. JSON/XML prompting approaches. The research phase validated that structured prompting provides higher reliability and precision. Based on these findings, the project is now transitioning to build a production API service.

When working in this repository:
- The root directory contains **research/prototype** code and planning documents
- The `structured-prompt-service/` directory will contain the **production** implementation
- Refer to the PRD and architecture documents for production requirements
- The CLI scripts demonstrate the core approach but are not production code

## Core Components

### Main Scripts

- **`json_assistant_cli.py`**: Basic CLI that extracts structured JSON from natural language prompts. Outputs JSON format only.
- **`structured_assistant_cli.py`**: Enhanced version that supports both JSON and XML output formats via `--format` flag. Includes XML conversion utilities.
- **`experiment_runner.py`**: Automated test harness that runs both scripts against a suite of complex/ambiguous prompts, validates output structure, and logs results to CSV.

### Architecture

All three scripts follow a similar pattern:
1. Configure Gemini API via `GEMINI_API_KEY` environment variable
2. Accept command-line arguments (prompt text, optional format flag)
3. Send a meta-prompt to Gemini with a strict JSON schema definition
4. Parse and validate the response
5. Output structured data or run experiments

The meta-prompt instructs the model to extract:
- `intent`: Primary action (e.g., 'create', 'analyze', 'translate')
- `subject`: Main topic/object
- `entities`: Key details, source, target
- `output_format`: Desired result format
- `original_language`: Language code of the subject (NOT the instruction language)

### Key Design Decision: Language Detection

The meta-prompt includes special instructions for `original_language` detection. It must identify the language of the subject being acted upon, not the instruction language. Example: "Translate 'Bonjour' to English" should detect `original_language: 'fr'` not `'en'`.

## Development Commands

### Setup
```bash
# Install dependencies (from new_JSON_Promtpting/)
pip install -r new_JSON_Promtpting/requirements.txt

# Or install directly:
pip install python-dotenv google-generativeai

# Set API key
export GEMINI_API_KEY="your-key-here"
```

### Running the Tools
```bash
# Basic JSON extraction
python json_assistant_cli.py "Your natural language prompt here"

# Structured extraction with format selection
python structured_assistant_cli.py "Your prompt" --format json
python structured_assistant_cli.py "Your prompt" --format xml

# Run experimental test suite
python experiment_runner.py
```

### Testing
The `experiment_runner.py` script validates:
- JSON structural validity (via `json.loads()`)
- XML structural validity (via `ET.fromstring()`)
- Latency measurements
- Error handling and edge cases

Results are saved to `test_results.csv` with columns: prompt_id, prompt_text, output_format, status, latency_seconds, output_content.

## Test Data

- **`Complex Ambiguous Prompts.txt`**: Categorized test prompts including complex/ambiguous, implicit/conversational, multilingual, technical, and creative prompts
- **`Complex Ambiguous Prompts-outputs.txt`**: Output results from initial test runs
- **`Complex Ambiguous Prompts-30-more.txt`**: Extended test set
- **`NL_JSON_XML_Overview`**: Research notes comparing the three prompting formats

## Production Planning Documents

- **`PRD_STRUCTURED_PROMPT_SERVICE.md`**: Complete product requirements document for the production API service, including functional/non-functional requirements, use cases, technical architecture, and 4-phase development roadmap
- **`REAL_WORLD_INTEGRATION_GUIDE.md`**: Integration patterns, technology stack recommendations, implementation strategies, cost-benefit analysis, and ROI calculations for production deployment
- **`BMAD_IMPLEMENTATION_PLAN.md`**: Step-by-step guide for using the BMad Method to build the production service from the PRD, including epic breakdowns and QA strategy

## Project History (old/ directory)

The `old/` directory contains previous iterations and documentation:
- Earlier converter implementations with category detection, constraint parsing, and quality scoring
- Markdown guides on usage and best practices
- JSON output samples from previous experiments

These are archived but provide context on the project's evolution from a feature-rich converter to a focused research tool.

## Important Notes

- The model used is `gemini-pro-latest` from Google's Generative AI API
- API responses may include markdown code fences (```json...```) which are stripped during parsing
- Error handling covers JSON decode errors and general exceptions
- The project has NO git repository initialized at the root level (not version controlled)
- A Python virtual environment exists at `new_JSON_Promtpting/venv/` but the main scripts run from the root directory
- The `structured-prompt-service/` directory is being set up for the production API implementation (currently empty Git repo)
- The project is transitioning from research to production - the CLI scripts are prototypes demonstrating the approach

## Production Development

The project is evolving into a production API service. For production development:

### Technology Stack (Planned)
- **Framework**: FastAPI (async, high-performance, auto-docs)
- **Validation**: Pydantic v2 + jsonschema
- **LLM Client**: LiteLLM (multi-provider abstraction)
- **Cache**: Redis (fast, persistent, distributed)
- **Database**: PostgreSQL (for request logs, schemas, user data)
- **Message Queue**: RabbitMQ or Kafka (for async processing)
- **Deployment**: Docker + Kubernetes

### Development Approach
The production service will be built using the BMad Method (see `BMAD_IMPLEMENTATION_PLAN.md`). Key phases:

#### Phase 1 (Weeks 1-2): Foundation - MVP
- REST API with `/v1/analyze` endpoint
- JSON Schema validation
- Basic caching (Redis)
- Prometheus metrics
- Docker containerization

#### Phase 2 (Weeks 3-4): Production Hardening
- API key authentication
- Rate limiting
- Advanced error handling + retries
- Monitoring dashboards (Grafana)
- Load testing and security audit

#### Phase 3 (Weeks 5-8): Advanced Features
- Multi-LLM support (Gemini, Claude, GPT-4)
- Batch processing API
- Async job processing
- Python SDK
- Prompt templates library

#### Phase 4 (Weeks 9-12): Ecosystem Integration
- JavaScript SDK
- Web UI dashboard
- Webhook notifications
- Data pipeline integrations
- Comprehensive documentation

### Repository Structure
- `/` (root): Research/prototype CLI tools and planning documents
- `/structured-prompt-service/`: Production API service implementation (in progress)
- `/old/`: Archived previous iterations
- `/research/`: Research notes and test data
- `/new_JSON_Promtpting/`: Original research environment with virtual environment
- `/docs/`: Production service documentation (will be in structured-prompt-service/)

### Working with Production Service
```bash
# Production service is being built in separate directory
cd structured-prompt-service/

# BMad Method will be used for structured development
# See BMAD_IMPLEMENTATION_PLAN.md for detailed workflow
```

## Research Context

The project validates that structured prompts (JSON/XML) achieve:
- Higher reliability and consistency (95%+ validation pass rate vs. 75% manual accuracy)
- Better precision and adherence to schema
- More predictable outputs for automation
- At the cost of higher token usage due to verbosity

The research phase is complete and validated the approach. The CLI tools are prototypes demonstrating the core technique - the focus is now on building a production-grade API service based on these findings.
