# BMad Method Implementation Plan
## Structured Prompt Service Platform Development

**Project**: Structured Prompt Service Platform
**Date**: 2025-10-13
**Approach**: BMad Method (Greenfield)
**Status**: Planning Phase

---

## Overview

This document outlines how to use the BMad Method to develop the Structured Prompt Service Platform, transforming the existing research codebase into a production-ready API service.

---

## Current State Assessment

### What You Have
✅ **PRD Complete** - `PRD_STRUCTURED_PROMPT_SERVICE.md` with:
- Functional Requirements (FR-1 through FR-10)
- Non-Functional Requirements (NFR-1 through NFR-7)
- Epics and Stories defined
- Technical architecture documented
- 4-phase roadmap established

✅ **Research Prototype** - Working CLI tools:
- `json_assistant_cli.py` - Basic JSON extraction
- `structured_assistant_cli.py` - JSON/XML extraction
- `experiment_runner.py` - Testing harness

✅ **Integration Guide** - `REAL_WORLD_INTEGRATION_GUIDE.md` with:
- Use cases and integration patterns
- Technology stack recommendations
- Implementation strategies

### What You Need
🔲 Architecture Document (detailed technical design)
🔲 Epic/Story Sharding (for iterative development)
🔲 QA Strategy (test architecture)
🔲 Development Environment Setup

---

## BMad Workflow for Your Project

Since you already have a PRD, you can **fast-track** the planning phase:

### Phase 1: Planning (Web UI or IDE) - CURRENT PHASE ⭐

```
Your Position in Workflow:
├─ ✅ PRD Created (You have this!)
├─ 🔲 Architecture Creation (Next step)
├─ 🔲 PO Master Checklist (Alignment)
├─ 🔲 Document Sharding (Prepare for dev)
└─ 🔲 Ready for Development Cycle
```

#### Step 1.1: Install BMad Method ✅ READY

**Action**: Install BMad in your new project directory

```bash
# Create new project directory
mkdir structured-prompt-service
cd structured-prompt-service

# Initialize git
git init

# Interactive BMad installation
npx bmad-method install

# Or for Claude Code integration
npx bmad-method install -f -i codex -d .
```

**What This Does**:
- Creates `.bmad-core/` directory with agents
- Sets up `docs/` structure for planning artifacts
- Installs PM, Architect, SM, Dev, QA, and PO agents
- Creates configuration files

#### Step 1.2: Copy Your PRD ✅ READY

**Action**: Move PRD to BMad structure

```bash
# Copy PRD to BMad expected location
cp /home/dman/project/Json_Promtpting_App/PRD_STRUCTURED_PROMPT_SERVICE.md \
   ./docs/prd.md
```

**Optional but Recommended**:
```bash
# Copy existing research code for reference
mkdir research
cp -r /home/dman/project/Json_Promtpting_App/*.py ./research/
cp -r /home/dman/project/Json_Promtpting_App/old ./research/
```

#### Step 1.3: Create Architecture with Architect Agent 🔲 NEXT

**Action**: Use BMad Architect to design system architecture

**Option A: In Web UI (Recommended for Planning)**
1. Navigate to BMad `dist/teams/`
2. Copy `team-fullstack.txt`
3. Create Gemini Gem or Claude Project
4. Upload instructions
5. Prompt: "As architect, create architecture from docs/prd.md"

**Option B: In IDE (Claude Code)**
```bash
# Open project in Claude Code
# Then use slash command:
/architect Create system architecture from docs/prd.md

# Or if using Cursor/Windsurf:
@architect Create system architecture from docs/prd.md
```

**What Architect Will Create**:
- System architecture diagram
- Component interactions
- Data models and schemas
- Technology stack details
- API contract definitions
- Security architecture
- Deployment architecture
- File structure recommendations

**Output**: `docs/architecture.md`

#### Step 1.4: PO Master Checklist 🔲 NEXT

**Action**: Validate PRD and Architecture alignment

```bash
# In Claude Code:
/po Run master checklist

# In Cursor/Windsurf:
@po Run master checklist
```

**What PO Validates**:
- PRD and Architecture alignment
- All requirements covered
- No contradictions
- Technical feasibility
- Clear acceptance criteria

**Possible Outcomes**:
- ✅ **Aligned**: Proceed to sharding
- ⚠️ **Needs Updates**: PO identifies gaps, iterate on PRD/Architecture

#### Step 1.5: Shard Documents 🔲 NEXT

**Action**: Break down PRD and Architecture into Epics and Stories

```bash
# Shard PRD first
/po Shard docs/prd.md into epics and stories

# Then shard Architecture
/po Shard docs/architecture.md
```

**What Gets Created**:
```
docs/
├── epics/
│   ├── epic-001-foundation-api.md
│   ├── epic-002-schema-validation.md
│   ├── epic-003-caching-layer.md
│   ├── epic-004-multi-llm-support.md
│   └── ...
└── stories/
    ├── epic-001/
    │   ├── story-001-fastapi-setup.md
    │   ├── story-002-analyze-endpoint.md
    │   ├── story-003-pydantic-models.md
    │   └── ...
    └── ...
```

**Expected Epics Based on Your PRD**:
1. **Foundation API** (Phase 1 - MVP)
2. **Schema Validation** (Phase 1 - MVP)
3. **Caching & Optimization** (Phase 2)
4. **Authentication & Security** (Phase 2)
5. **Multi-LLM Support** (Phase 3)
6. **Batch Processing** (Phase 3)
7. **SDK Development** (Phase 3)
8. **Web Dashboard** (Phase 4)

---

### Phase 2: Development Cycle (IDE) - FUTURE

Once documents are sharded, you enter the iterative dev cycle:

#### The Story Cycle

```
1. SM: Draft story from epic
   ↓
2. QA: *risk + *design (for high-risk stories)
   ↓
3. PO: Validate story (optional)
   ↓
4. User: Approve story
   ↓
5. Dev: Implement tasks + tests
   ↓
6. QA: *trace, *nfr (optional mid-dev checks)
   ↓
7. Dev: Mark ready for review
   ↓
8. QA: *review (comprehensive assessment)
   ↓
9. Commit changes
   ↓
10. Mark story done → Next story
```

---

## BMad Agents for Your Project

### Agents You'll Use

| Agent | When | Purpose | Example Commands |
|-------|------|---------|-----------------|
| **PM** | Planning | PRD creation/updates | `/pm Update NFR-1 with new latency targets` |
| **Architect** | Planning | System design | `/architect Design caching layer architecture` |
| **PO** | Planning + Dev | Validation & sharding | `/po Shard prd`, `/po Validate story against epic` |
| **SM** | Development | Story drafting | `/sm Draft next story from epic-001` |
| **Dev** | Development | Implementation | `/dev Implement story-001-fastapi-setup` |
| **QA** | All phases | Quality assurance | `/qa *risk story-001`, `/qa *review story-001` |

### Recommended Agent Workflow

**Planning Phase** (You are here):
```bash
/architect Create architecture          # Create system design
/po Run master checklist               # Validate alignment
/po Shard docs/prd.md                  # Create epics/stories
/po Shard docs/architecture.md         # Distribute arch guidance
```

**First Story** (After planning):
```bash
/sm Draft story from epic-001          # SM creates first story
/qa *risk draft-story                  # QA assesses risks (HIGH-RISK stories)
/qa *design draft-story                # QA creates test strategy
/dev Implement story-001               # Dev builds feature + tests
/qa *review story-001                  # QA comprehensive review
/qa *gate story-001                    # Update quality gate
```

**Subsequent Stories**:
```bash
/sm Review previous story notes        # Learn from last story
/sm Draft next story                   # Create next story
# Repeat dev cycle...
```

---

## Mapping Your PRD to BMad Epics

### Suggested Epic Breakdown

Based on your PRD's 4-phase roadmap, here's how epics map:

#### **Epic 1: Foundation API (Phase 1 - Weeks 1-2)**
**Stories**:
- 1.1: FastAPI project setup + Docker
- 1.2: Pydantic models for requests/responses
- 1.3: `/v1/analyze` endpoint implementation
- 1.4: LLM integration (Gemini API)
- 1.5: Basic error handling
- 1.6: Health check endpoint
- 1.7: Prometheus metrics setup

**Priority**: P0 (MVP blocker)
**Dependencies**: None
**Risk Level**: Medium (new codebase setup)

#### **Epic 2: Schema Validation (Phase 1 - Weeks 1-2)**
**Stories**:
- 2.1: JSON Schema validation integration
- 2.2: Schema registry structure
- 2.3: Validation error handling
- 2.4: Schema versioning support
- 2.5: Common schema definitions

**Priority**: P0 (MVP blocker)
**Dependencies**: Epic 1 (API foundation)
**Risk Level**: Medium (validation complexity)

#### **Epic 3: Caching Layer (Phase 2 - Weeks 3-4)**
**Stories**:
- 3.1: Redis integration
- 3.2: Cache key generation
- 3.3: TTL configuration
- 3.4: Cache invalidation API
- 3.5: Cache metrics

**Priority**: P0 (cost optimization critical)
**Dependencies**: Epic 1, 2
**Risk Level**: Low (standard pattern)

#### **Epic 4: Authentication & Security (Phase 2 - Weeks 3-4)**
**Stories**:
- 4.1: API key authentication
- 4.2: Rate limiting (per client)
- 4.3: Input sanitization
- 4.4: Secrets management
- 4.5: TLS configuration
- 4.6: Security audit logging

**Priority**: P0 (production requirement)
**Dependencies**: Epic 1
**Risk Level**: High (security critical)

#### **Epic 5: Production Hardening (Phase 2 - Weeks 3-4)**
**Stories**:
- 5.1: Retry logic with exponential backoff
- 5.2: Circuit breaker implementation
- 5.3: Grafana dashboards
- 5.4: Alerting rules
- 5.5: Load testing setup
- 5.6: Graceful shutdown

**Priority**: P0 (reliability requirement)
**Dependencies**: Epics 1-4
**Risk Level**: Medium (integration complexity)

#### **Epic 6: Multi-LLM Support (Phase 3 - Weeks 5-8)**
**Stories**:
- 6.1: LLM provider abstraction
- 6.2: Claude integration
- 6.3: GPT-4 integration
- 6.4: Llama integration
- 6.5: Intelligent routing logic
- 6.6: Provider fallback handling

**Priority**: P1 (competitive advantage)
**Dependencies**: Epics 1-5
**Risk Level**: High (multiple integrations)

#### **Epic 7: Batch Processing (Phase 3 - Weeks 5-8)**
**Stories**:
- 7.1: `/v1/analyze/batch` endpoint
- 7.2: Parallel processing implementation
- 7.3: Per-item error handling
- 7.4: Batch status tracking
- 7.5: Batch size limits

**Priority**: P1 (scalability)
**Dependencies**: Epic 1, 2
**Risk Level**: Medium (concurrency)

#### **Epic 8: Async Job Processing (Phase 3 - Weeks 5-8)**
**Stories**:
- 8.1: RabbitMQ integration
- 8.2: `/v1/jobs` endpoint (submit)
- 8.3: Job status tracking
- 8.4: Webhook notifications
- 8.5: Job cleanup and expiration

**Priority**: P1 (long-running requests)
**Dependencies**: Epic 1, 2, 3
**Risk Level**: High (distributed system)

#### **Epic 9: Python SDK (Phase 3 - Weeks 5-8)**
**Stories**:
- 9.1: SDK project structure
- 9.2: Client implementation
- 9.3: Authentication handling
- 9.4: Error handling and retries
- 9.5: PyPI packaging
- 9.6: SDK documentation

**Priority**: P1 (developer experience)
**Dependencies**: Epics 1-5
**Risk Level**: Low (standard SDK pattern)

#### **Epic 10: Web Dashboard (Phase 4 - Weeks 9-12)**
**Stories**:
- 10.1: Frontend project setup (React/Next.js)
- 10.2: Prompt tester interface
- 10.3: Schema editor
- 10.4: Usage analytics
- 10.5: API key management
- 10.6: Request history viewer

**Priority**: P2 (nice to have)
**Dependencies**: All previous epics
**Risk Level**: Medium (full-stack)

---

## QA Strategy with BMad Test Architect

### When to Use QA Agent

**High-Risk Stories** (Always use QA):
- Epic 4 (Authentication & Security) - All stories
- Epic 6 (Multi-LLM Support) - Provider integrations
- Epic 8 (Async Processing) - Distributed system complexity

**QA Commands by Stage**:

```bash
# Before Development (High-Risk Stories)
/qa *risk story-4.1-api-key-auth
/qa *design story-4.1-api-key-auth

# During Development (All Stories)
/qa *trace story-1.3-analyze-endpoint  # Mid-implementation
/qa *nfr story-1.3-analyze-endpoint    # Check quality attributes

# After Development (All Stories)
/qa *review story-1.3-analyze-endpoint # Comprehensive review
/qa *gate story-1.3-analyze-endpoint   # Update quality gate
```

### Expected Quality Gates

**Critical (Must PASS)**:
- Security stories (Epic 4)
- Core API functionality (Epic 1, 2)
- Performance requirements (NFR-1)

**Important (CONCERNS acceptable with plan)**:
- Advanced features (Epics 6-8)
- SDK implementation (Epic 9)
- Dashboard (Epic 10)

---

## Technical Preferences Setup

Create `.bmad-core/data/technical-preferences.md` to guide architecture decisions:

```markdown
# Technical Preferences - Structured Prompt Service

## Framework & Language
- Python 3.11+
- FastAPI (prefer over Flask)
- Pydantic v2 for validation
- Async/await patterns

## Testing
- pytest for all tests
- pytest-asyncio for async tests
- locust for load testing
- Coverage target: 80%+

## Code Style
- Black for formatting
- Ruff for linting
- Type hints required
- Docstrings for all public APIs

## Architecture Patterns
- Repository pattern for data access
- Dependency injection via FastAPI
- Factory pattern for LLM providers
- Strategy pattern for routing logic

## API Design
- RESTful conventions
- JSON:API error format
- OpenAPI 3.0 spec
- Versioned endpoints (/v1/, /v2/)

## Security
- API key authentication (Phase 1)
- OAuth2 + JWT (future)
- Input validation at boundary
- Secrets via environment/vault

## Performance
- Cache-first strategy
- Connection pooling (Redis, DB)
- Async wherever possible
- Background tasks for slow ops

## Observability
- Structured JSON logging
- Prometheus metrics
- OpenTelemetry tracing
- Correlation IDs for requests
```

---

## Developer Context Files

After architecture is created and sharded, configure which files dev agent always loads:

**Edit `.bmad-core/core-config.yaml`**:
```yaml
devLoadAlwaysFiles:
  - docs/architecture/tech-stack.md
  - docs/architecture/coding-standards.md
  - docs/architecture/api-contracts.md
  - docs/architecture/error-handling.md
```

These files should be **lean** and contain only the critical standards developers need to follow consistently.

---

## Next Steps - Action Plan

### Immediate (Today/This Week)

1. ✅ **Review BMad Method** (Complete!)
2. 🔲 **Create New Project Directory**
   ```bash
   cd /home/dman/project
   mkdir structured-prompt-service
   cd structured-prompt-service
   git init
   ```

3. 🔲 **Install BMad Method**
   ```bash
   npx bmad-method install
   ```

4. 🔲 **Copy PRD to Project**
   ```bash
   cp /home/dman/project/Json_Promtpting_App/PRD_STRUCTURED_PROMPT_SERVICE.md \
      ./docs/prd.md
   ```

5. 🔲 **Create Technical Preferences**
   - Edit `.bmad-core/data/technical-preferences.md`
   - Add your technology preferences

6. 🔲 **Generate Architecture**
   ```bash
   # In Claude Code:
   /architect Create system architecture from docs/prd.md

   # Or in web UI with team-fullstack.txt bundle
   ```

7. 🔲 **Validate with PO**
   ```bash
   /po Run master checklist
   ```

8. 🔲 **Shard Documents**
   ```bash
   /po Shard docs/prd.md
   /po Shard docs/architecture.md
   ```

### First Sprint (Weeks 1-2)

Focus on **Epic 1 (Foundation API)** and **Epic 2 (Schema Validation)**:

```bash
# Story 1.1: FastAPI Setup
/sm Draft story from epic-001
/qa *risk story-1.1          # Risk assessment
/dev Implement story-1.1     # Build it
/qa *review story-1.1        # Review it
git add . && git commit      # Commit it

# Story 1.2: Pydantic Models
/sm Draft next story
/dev Implement story-1.2
/qa *review story-1.2
git add . && git commit

# Repeat for stories 1.3-1.7...
```

### Second Sprint (Weeks 3-4)

Focus on **Epic 3 (Caching)**, **Epic 4 (Security)**, **Epic 5 (Hardening)**:

```bash
# High-risk security stories require extra QA
/sm Draft story from epic-004
/qa *risk story-4.1
/qa *design story-4.1
/dev Implement story-4.1
/qa *nfr story-4.1           # Check security NFRs
/qa *review story-4.1
git add . && git commit
```

---

## Tips for Success with BMad

### 1. **Start Small**
- Focus on one epic at a time
- Complete stories sequentially
- Commit frequently

### 2. **Use QA Strategically**
- Always run `*risk` and `*design` on HIGH-RISK stories
- Use `*trace` and `*nfr` during development to catch issues early
- Run `*review` on every story before marking done

### 3. **Keep Context Lean**
- Only include relevant files in agent context
- Compact conversations periodically (especially with BMad-Master)
- Use focused, specific prompts

### 4. **Follow the Workflow**
- Don't skip steps (especially PO validation)
- Commit after each story
- Review QA gates before proceeding

### 5. **Iterate and Learn**
- SM should review previous story notes before drafting next story
- Update coding standards as patterns emerge
- Refine architecture based on implementation learnings

---

## Expected Outputs by Phase

### After Planning Phase
```
structured-prompt-service/
├── .bmad-core/                    # BMad agents
├── docs/
│   ├── prd.md                     # Your PRD
│   ├── architecture.md            # Generated architecture
│   ├── epics/                     # Sharded epics
│   │   ├── epic-001-foundation-api.md
│   │   └── ...
│   └── stories/                   # Sharded stories
│       ├── epic-001/
│       │   ├── story-001-fastapi-setup.md
│       │   └── ...
│       └── ...
└── README.md
```

### After Phase 1 (MVP - Weeks 1-2)
```
structured-prompt-service/
├── src/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── analyze.py         # /v1/analyze endpoint
│   │   │   └── health.py          # /v1/health endpoint
│   │   └── models.py              # Pydantic models
│   ├── core/
│   │   ├── llm_client.py          # LLM integration
│   │   └── validator.py           # Schema validation
│   └── main.py                    # FastAPI app
├── tests/
│   ├── unit/
│   └── integration/
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

### After Phase 2 (Production - Week 4)
- Add Redis caching
- Add authentication
- Add monitoring/alerting
- Ready for pilot deployment

### After Phase 3 (Advanced - Week 8)
- Multi-LLM support
- Batch processing
- Python SDK
- Internal adoption ready

### After Phase 4 (Platform - Week 12)
- Web dashboard
- Full self-service
- Organization-wide deployment

---

## Conclusion

The BMad Method provides a structured, AI-driven approach perfectly suited for your Structured Prompt Service Platform. You already have the hardest part done (the PRD), so you can fast-track through planning and get to development quickly.

**Your Greenfield Advantage**:
- No legacy code constraints
- Clean architecture from the start
- Test-driven from day one
- Quality gates enforced throughout

**Next Action**: Install BMad and create the architecture document. Once that's done, you'll be ready to start building!

---

## Quick Reference

### Essential Commands

```bash
# Planning
/architect Create architecture from docs/prd.md
/po Run master checklist
/po Shard docs/prd.md
/po Shard docs/architecture.md

# Development Cycle
/sm Draft next story from epic-XXX
/qa *risk story-X.Y
/qa *design story-X.Y
/dev Implement story-X.Y
/qa *trace story-X.Y
/qa *nfr story-X.Y
/qa *review story-X.Y
/qa *gate story-X.Y

# Validation
/po Validate story against epic
```

### File Paths Reference

```text
PRD              → docs/prd.md
Architecture     → docs/architecture.md
Epics            → docs/epics/epic-XXX-name.md
Stories          → docs/stories/epic-XXX/story-XXX-name.md
Risk Assessments → docs/qa/assessments/{epic}.{story}-risk-{DATE}.md
Test Designs     → docs/qa/assessments/{epic}.{story}-test-design-{DATE}.md
Quality Gates    → docs/qa/gates/{epic}.{story}-{slug}.yml
```

Good luck with your development! 🚀
