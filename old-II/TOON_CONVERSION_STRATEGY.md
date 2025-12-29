# TOON Conversion Strategy - Structured Prompt Service

**Target Application:** Structured Prompt Service (FastAPI-based prompt analysis API)
**Current Format:** JSON request/response
**Target Format:** TOON (Token-Oriented Object Notation)
**Expected Token Savings:** 30-60% reduction vs JSON
**Status:** Conversion Planning Phase

---

## Executive Summary

This document outlines the complete strategy for converting the Structured Prompt Service from JSON-based formatting to TOON (Token-Oriented Object Notation) format, achieving 30-60% token savings while maintaining all existing functionality.

### Key Benefits

âœ… **Cost Reduction:** 30-60% fewer tokens = direct cost savings on LLM API calls
âœ… **Performance:** Faster response times due to reduced token processing
âœ… **Scalability:** Handle more requests with same budget
âœ… **Compatibility:** Maintain backward compatibility with JSON format

### High-Level Approach

1. **Dual-Format Support** - Accept both JSON and TOON, return requested format
2. **Gradual Migration** - New endpoints first, then migrate existing endpoints
3. **Backward Compatibility** - Keep JSON support for existing clients
4. **Validation** - Ensure TOON output matches JSON semantics
5. **Performance Monitoring** - Track actual token savings

---

## Table of Contents

1. [Current Architecture Analysis](#current-architecture-analysis)
2. [TOON Integration Points](#toon-integration-points)
3. [Implementation Plan](#implementation-plan)
4. [Code Changes Required](#code-changes-required)
5. [Testing Strategy](#testing-strategy)
6. [Migration Path](#migration-path)
7. [Performance Impact](#performance-impact)
8. [Risk Assessment](#risk-assessment)
9. [Success Metrics](#success-metrics)

---

## Current Architecture Analysis

### Current JSON Flow

```
Client Request (JSON)
    ↓
FastAPI Endpoint /v1/analyze
    ↓
Validate Request Schema (Pydantic)
    ↓
Check Cache (Redis) - Keyed by prompt hash
    ↓
Cache Miss → Call Gemini API
    ↓
Prompt: "Analyze this prompt and return JSON with intent, subject, entities..."
    ↓
Gemini Returns JSON String
    ↓
Parse JSON → Validate against StructuredData schema
    ↓
Store in Cache + Database
    ↓
Return JSON Response
```

### Current Token Usage Pattern

**Example Request:**
```json
{
  "prompt": "Extract contacts from: John Doe (john@example.com, 555-1234)",
  "output_format": "json",
  "llm_provider": "gemini",
  "temperature": 0.1
}
```
**Estimated Tokens:** ~45 tokens

**Example Response:**
```json
{
  "request_id": "abc123",
  "data": {
    "intent": "extract",
    "subject": "contacts",
    "entities": {
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "555-1234"
    },
    "output_format": "structured",
    "original_language": "en",
    "confidence_score": 0.92
  },
  "llm_provider": "gemini",
  "tokens_used": 187,
  "latency_ms": 312,
  "cached": false,
  "timestamp": "2024-01-15T10:35:00Z"
}
```
**Estimated Tokens:** ~150 tokens

**Total JSON Tokens:** ~195 tokens

---

## TOON Integration Points

### Where TOON Fits

```
Client Request (JSON or TOON)
    ↓
FastAPI Endpoint /v1/analyze
    ↓
[NEW] Detect Input Format (JSON/TOON)
    ↓
[NEW] Parse TOON → Python objects (if TOON)
    ↓
Validate Request Schema (Pydantic)
    ↓
[MODIFIED] Cache Key includes format preference
    ↓
Cache Miss → Call Gemini API
    ↓
[MODIFIED] Prompt: "Return TOON format with intent, subject, entities..."
    ↓
[MODIFIED] Gemini Returns TOON String
    ↓
[NEW] Parse TOON → Validate against schema
    ↓
[NEW] Convert to requested output format (JSON/TOON)
    ↓
Store in Cache + Database
    ↓
Return Response (JSON or TOON)
```

### New Components Needed

1. **TOON Parser Module** (`services/toon_parser.py`)
   - Parse TOON strings to Python objects
   - Convert Python objects to TOON strings
   - Validate TOON syntax

2. **Format Detection Middleware** (`middleware/format_detection.py`)
   - Detect request format (JSON/TOON)
   - Set format preference for response

3. **LLM Prompt Templates** (`prompts/toon_prompts.py`)
   - TOON-specific prompt engineering
   - Include TOON format rules in system prompts
   - Few-shot examples for TOON generation

4. **TOON Validation** (`models/toon_schemas.py`)
   - Validate TOON structure matches expected schema
   - Convert between TOON and Pydantic models

5. **Response Formatter** (`services/response_formatter.py`)
   - Convert internal Python objects to requested format
   - Handle both JSON and TOON serialization

---

## Implementation Plan

### Phase 1: Foundation (Week 1)

**Goal:** Set up TOON infrastructure

#### Tasks:

1. **Add TOON Library Dependency**
   ```bash
   pip install toon-format  # Hypothetical package name
   # OR implement custom TOON parser based on specification
   ```

2. **Create TOON Parser Module**
   ```python
   # app/services/toon_parser.py
   
   from toon_format import encode, decode, DecodeOptions
   from typing import Dict, Any
   
   class ToonParser:
       """Parse and generate TOON format strings."""
       
       @staticmethod
       def parse(toon_string: str, strict: bool = False) -> Dict[str, Any]:
           """Parse TOON string to Python dict."""
           options = DecodeOptions(strict=strict)
           return decode(toon_string, options)
       
       @staticmethod
       def generate(data: Dict[str, Any], use_tabular: bool = True) -> str:
           """Generate TOON string from Python dict."""
           options = EncodeOptions(
               delimiter=",",
               indent=2,
               lengthMarker="#"  # Explicit validation for LLMs
           )
           return encode(data, options)
       
       @staticmethod
       def estimate_savings(data: Dict[str, Any]) -> Dict[str, Any]:
           """Calculate token savings vs JSON."""
           from toon_format import estimate_savings
           return estimate_savings(data)
   ```

3. **Update Request Models**
   ```python
   # app/models/requests.py
   
   class AnalyzeRequest(BaseModel):
       prompt: str = Field(..., min_length=1, max_length=10_000)
       output_format: Literal["json", "toon"] = "json"  # NEW: Support TOON
       # ... existing fields
   ```

4. **Create Format Detection Middleware**
   ```python
   # app/middleware/format_detection.py
   
   from fastapi import Request
   
   async def detect_format_middleware(request: Request, call_next):
       """Detect if request body is TOON or JSON."""
       content_type = request.headers.get("content-type", "application/json")
       
       if "application/toon" in content_type:
           request.state.input_format = "toon"
       else:
           request.state.input_format = "json"
       
       response = await call_next(request)
       return response
   ```

**Deliverables:**
- âœ… TOON parser module with encode/decode functions
- âœ… Updated request models supporting TOON format
- âœ… Format detection middleware
- âœ… Unit tests for TOON parsing

**Success Criteria:**
- Parse TOON strings to Python dicts
- Generate TOON strings from Python dicts
- Validate TOON syntax (strict mode)

---

### Phase 2: LLM Integration (Week 1-2)

**Goal:** Modify LLM prompts to generate TOON format

#### Tasks:

1. **Create TOON Prompt Templates**
   ```python
   # app/prompts/toon_prompts.py
   
   TOON_SYSTEM_PROMPT = """
   You are an expert at analyzing natural language prompts and extracting structured information.
   
   CRITICAL: You MUST respond in TOON (Token-Oriented Object Notation) format, NOT JSON.
   
   TOON FORMAT RULES:
   1. Use key: value pairs with indentation for nesting
   2. All arrays must have length indicators [N]
   3. Use tabular arrays [N,] for uniform data (most efficient!)
   4. Quote strings only when necessary:
      - Empty strings
      - Reserved keywords (true, false, null)
      - Strings that look like numbers
      - Strings with leading/trailing whitespace
      - Strings containing structural characters (: [ ] -)
   
   TABULAR ARRAY EXAMPLE (Use this for uniform objects!):
   ```toon
   contacts [2,]
     name, email, phone
     John Doe, john@example.com, 555-1234
     Jane Smith, jane@example.com, 555-5678
   ```
   
   REQUIRED STRUCTURE:
   ```toon
   intent: <primary action>
   subject: <main topic>
   entities:
     <key>: <value>
     ...
   output_format: <desired format>
   original_language: <ISO 639-1 code>
   confidence_score: <0.0-1.0>
   ```
   
   IMPORTANT:
   - Use tabular arrays [N,] whenever possible for maximum token efficiency
   - DO NOT use JSON braces {} or brackets [] except for array indicators
   - DO NOT quote strings unless required by quoting rules
   - Always include array length indicators [N]
   """
   
   def build_toon_prompt(user_prompt: str) -> str:
       """Build complete prompt for TOON generation."""
       return f"""
   {TOON_SYSTEM_PROMPT}
   
   USER PROMPT: {user_prompt}
   
   Analyze the prompt above and respond in TOON format. Use tabular arrays for any uniform data.
   """
   ```

2. **Modify LLM Service**
   ```python
   # app/services/llm_service.py
   
   class LLMService:
       async def analyze_prompt_toon(
           self,
           prompt: str,
           provider: str = "gemini",
           temperature: float = 0.1
       ) -> str:
           """Analyze prompt and return TOON formatted string."""
           
           full_prompt = build_toon_prompt(prompt)
           
           # Call LLM with TOON-specific prompt
           response = await self.client.generate(
               prompt=full_prompt,
               temperature=temperature,
               max_tokens=2000
           )
           
           # Extract TOON from code block if present
           toon_string = self._extract_toon_block(response)
           
           return toon_string
       
       def _extract_toon_block(self, response: str) -> str:
           """Extract TOON from markdown code block."""
           import re
           
           # Look for ```toon ... ``` blocks
           match = re.search(r'```toon\n(.*?)\n```', response, re.DOTALL)
           if match:
               return match.group(1)
           
           # Fallback: return entire response
           return response.strip()
   ```

3. **Add TOON Validation**
   ```python
   # app/services/toon_validator.py
   
   from pydantic import ValidationError
   
   class ToonValidator:
       """Validate TOON output matches expected schema."""
       
       @staticmethod
       def validate_structured_data(toon_string: str) -> StructuredData:
           """Parse TOON and validate against StructuredData schema."""
           try:
               # Parse TOON to dict
               parser = ToonParser()
               data_dict = parser.parse(toon_string, strict=False)  # Lenient for LLM output
               
               # Validate with Pydantic
               structured_data = StructuredData(**data_dict)
               
               return structured_data
               
           except Exception as e:
               # If validation fails, try to fix common issues
               fixed_dict = self._attempt_fixes(data_dict)
               return StructuredData(**fixed_dict)
       
       @staticmethod
       def _attempt_fixes(data: dict) -> dict:
           """Attempt to fix common TOON parsing issues."""
           # Ensure required fields exist
           if "intent" not in data:
               data["intent"] = "unknown"
           if "subject" not in data:
               data["subject"] = "unknown"
           # ... more fixes
           return data
   ```

**Deliverables:**
- âœ… TOON-specific LLM prompts with format rules
- âœ… Modified LLM service supporting TOON generation
- âœ… TOON validation against Pydantic schemas
- âœ… Error recovery for malformed TOON

**Success Criteria:**
- Gemini generates valid TOON 95%+ of the time
- TOON output validates against StructuredData schema
- Token savings measured and logged

---

### Phase 3: API Endpoints (Week 2)

**Goal:** Update API to handle TOON requests/responses

#### Tasks:

1. **Update /v1/analyze Endpoint**
   ```python
   # app/api/v1/analyze.py
   
   @router.post("/", response_model=Union[AnalyzeResponse, str])
   async def analyze_prompt(
       request: AnalyzeRequest,
       api_key: APIKey = Depends(get_api_key),
       db: AsyncSession = Depends(get_db),
       redis: Redis = Depends(get_redis)
   ):
       """Analyze prompt and return structured data.
       
       Supports both JSON and TOON output formats.
       """
       
       # Check cache
       cache_key = generate_cache_key(
           request.prompt,
           request.llm_provider,
           request.temperature,
           request.output_format  # NEW: Include format in cache key
       )
       
       cached_response = await redis.get(cache_key)
       if cached_response:
           if request.output_format == "toon":
               return Response(content=cached_response, media_type="application/toon")
           else:
               return AnalyzeResponse.parse_raw(cached_response)
       
       # Call LLM
       if request.output_format == "toon":
           # Generate TOON
           toon_string = await llm_service.analyze_prompt_toon(
               request.prompt,
               request.llm_provider,
               request.temperature
           )
           
           # Validate TOON
           structured_data = ToonValidator.validate_structured_data(toon_string)
           
           # Build response
           response_dict = {
               "request_id": str(uuid.uuid4()),
               "data": structured_data.dict(),
               "llm_provider": request.llm_provider,
               # ... more fields
           }
           
           # Convert response to TOON
           response_toon = ToonParser.generate(response_dict)
           
           # Cache TOON string
           await redis.setex(cache_key, request.cache_ttl, response_toon)
           
           # Return TOON response
           return Response(content=response_toon, media_type="application/toon")
       
       else:
           # Existing JSON flow
           # ... existing code
   ```

2. **Add TOON-Specific Endpoint (Optional)**
   ```python
   # app/api/v1/analyze_toon.py
   
   @router.post("/toon", response_class=Response)
   async def analyze_prompt_toon(
       request: AnalyzeRequest,
       api_key: APIKey = Depends(get_api_key),
       # ... dependencies
   ):
       """Dedicated TOON endpoint for clarity."""
       request.output_format = "toon"
       return await analyze_prompt(request, api_key, db, redis)
   ```

3. **Update Response Headers**
   ```python
   # Add content-type header based on format
   
   if output_format == "toon":
       headers = {
           "Content-Type": "application/toon",
           "X-Token-Savings": f"{savings_percent}%",
           "X-Original-Format": "json"
       }
   ```

**Deliverables:**
- âœ… Updated /v1/analyze endpoint supporting TOON
- âœ… Optional dedicated /v1/analyze/toon endpoint
- âœ… Proper content-type headers
- âœ… Cache keys include output format

**Success Criteria:**
- Accept requests with `output_format: "toon"`
- Return TOON formatted responses
- Maintain backward compatibility with JSON

---

### Phase 4: Monitoring & Metrics (Week 2-3)

**Goal:** Track TOON adoption and token savings

#### Tasks:

1. **Add TOON Metrics**
   ```python
   # app/monitoring/metrics.py
   
   # New Prometheus metrics
   toon_requests_total = Counter(
       "toon_requests_total",
       "Total TOON format requests"
   )
   
   toon_token_savings = Histogram(
       "toon_token_savings_percent",
       "Token savings percentage vs JSON",
       buckets=[10, 20, 30, 40, 50, 60, 70, 80]
   )
   
   toon_parse_errors = Counter(
       "toon_parse_errors_total",
       "TOON parsing/validation errors"
   )
   
   toon_generation_latency = Histogram(
       "toon_generation_latency_seconds",
       "TOON generation latency"
   )
   ```

2. **Calculate Token Savings**
   ```python
   # app/services/token_calculator.py
   
   class TokenCalculator:
       """Calculate and track token savings."""
       
       @staticmethod
       async def calculate_savings(
           data: dict,
           format_used: str
       ) -> Dict[str, Any]:
           """Calculate token savings for TOON vs JSON."""
           
           # Generate both formats
           json_str = json.dumps(data)
           toon_str = ToonParser.generate(data)
           
           # Count tokens
           json_tokens = count_tokens(json_str)
           toon_tokens = count_tokens(toon_str)
           
           savings = json_tokens - toon_tokens
           savings_percent = (savings / json_tokens) * 100
           
           # Log metrics
           toon_token_savings.observe(savings_percent)
           
           return {
               "json_tokens": json_tokens,
               "toon_tokens": toon_tokens,
               "savings": savings,
               "savings_percent": round(savings_percent, 2)
           }
   ```

3. **Update Grafana Dashboard**
   ```yaml
   # monitoring/grafana/dashboards/toon_metrics.json
   
   # Add panels for:
   - TOON Request Rate
   - Token Savings Distribution (histogram)
   - TOON vs JSON Usage Split
   - TOON Parse Success Rate
   - Average Token Savings per Request
   ```

**Deliverables:**
- âœ… Prometheus metrics for TOON usage
- âœ… Token savings calculation and tracking
- âœ… Grafana dashboard for TOON metrics
- âœ… Logging for TOON-specific events

**Success Criteria:**
- Track TOON adoption rate
- Measure real token savings (target: 30-60%)
- Monitor TOON parse success rate (target: >95%)

---

### Phase 5: Testing & Validation (Week 3)

**Goal:** Comprehensive testing of TOON implementation

#### Tasks:

1. **Unit Tests**
   ```python
   # tests/test_toon_parser.py
   
   def test_parse_valid_toon():
       """Test parsing valid TOON string."""
       toon_str = """
   intent: translate
   subject: text
   entities:
     source: Hello
     target_language: French
   """
       data = ToonParser.parse(toon_str)
       assert data["intent"] == "translate"
   
   def test_generate_toon():
       """Test generating TOON from dict."""
       data = {"intent": "extract", "subject": "contacts"}
       toon_str = ToonParser.generate(data)
       assert "intent: extract" in toon_str
   
   def test_token_savings():
       """Test token savings calculation."""
       data = {"users": [{"name": "Alice"}, {"name": "Bob"}]}
       savings = ToonParser.estimate_savings(data)
       assert savings["savings_percent"] > 30  # Expect 30%+ savings
   ```

2. **Integration Tests**
   ```python
   # tests/test_toon_api.py
   
   @pytest.mark.asyncio
   async def test_toon_endpoint():
       """Test TOON format endpoint."""
       response = await client.post(
           "/v1/analyze",
           json={
               "prompt": "Extract contacts from: John (john@example.com)",
               "output_format": "toon"
           },
           headers={"X-API-Key": test_api_key}
       )
       
       assert response.status_code == 200
       assert response.headers["content-type"] == "application/toon"
       
       # Parse TOON response
       toon_data = ToonParser.parse(response.text)
       assert "intent" in toon_data
   
   @pytest.mark.asyncio
   async def test_json_backward_compatibility():
       """Ensure JSON still works."""
       response = await client.post(
           "/v1/analyze",
           json={
               "prompt": "Test prompt",
               "output_format": "json"
           },
           headers={"X-API-Key": test_api_key}
       )
       
       assert response.status_code == 200
       data = response.json()
       assert "data" in data
   ```

3. **Load Testing with TOON**
   ```python
   # load_tests/toon_load_test.py
   
   class ToonUser(HttpUser):
       wait_time = between(1, 3)
       
       @task
       def analyze_toon(self):
           self.client.post(
               "/v1/analyze",
               json={
                   "prompt": "Extract users from text",
                   "output_format": "toon"
               },
               headers={"X-API-Key": self.api_key}
           )
   ```

4. **Validation Tests**
   ```python
   # tests/test_toon_validation.py
   
   def test_validate_toon_structure():
       """Test TOON structure validation."""
       valid_toon = """
   intent: extract
   subject: contacts
   entities:
     name: John Doe
   output_format: structured
   original_language: en
   confidence_score: 0.95
   """
       structured_data = ToonValidator.validate_structured_data(valid_toon)
       assert structured_data.intent == "extract"
   
   def test_invalid_toon_recovery():
       """Test recovery from malformed TOON."""
       invalid_toon = """
   intent: extract
   # Missing required fields
   """
       # Should still parse with lenient mode
       structured_data = ToonValidator.validate_structured_data(invalid_toon)
       assert structured_data.intent == "extract"
   ```

**Deliverables:**
- âœ… Unit tests for TOON parsing/generation
- âœ… Integration tests for TOON endpoints
- âœ… Load tests comparing TOON vs JSON performance
- âœ… Validation tests for error recovery

**Success Criteria:**
- >95% test coverage for TOON code
- Load tests show 30-60% token reduction
- All tests pass with both JSON and TOON formats

---

### Phase 6: Documentation & Migration (Week 3-4)

**Goal:** Document TOON support and create migration guide

#### Tasks:

1. **API Documentation Updates**
   ```markdown
   # docs/TOON_API_GUIDE.md
   
   # TOON Format Support
   
   The Structured Prompt Service now supports TOON (Token-Oriented Object Notation) format,
   providing 30-60% token savings compared to JSON.
   
   ## Using TOON Format
   
   ### Request
   \`\`\`http
   POST /v1/analyze
   Content-Type: application/json
   X-API-Key: sp_your_key_here
   
   {
     "prompt": "Extract contacts from: John Doe (john@example.com)",
     "output_format": "toon"
   }
   \`\`\`
   
   ### Response (TOON Format)
   \`\`\`toon
   request_id: abc123-def456
   data:
     intent: extract
     subject: contacts
     entities:
       name: John Doe
       email: john@example.com
     output_format: structured
     original_language: en
     confidence_score: 0.92
   llm_provider: gemini
   tokens_used: 89
   latency_ms: 312
   cached: false
   timestamp: 2024-01-15T10:35:00Z
   \`\`\`
   
   ### Token Savings
   - JSON: 187 tokens
   - TOON: 89 tokens
   - **Savings: 52%**
   ```

2. **Migration Guide**
   ```markdown
   # docs/TOON_MIGRATION_GUIDE.md
   
   # Migrating to TOON Format
   
   ## Why Migrate?
   - 30-60% token reduction
   - Lower LLM API costs
   - Faster response times
   
   ## Migration Steps
   
   ### Step 1: Update Request
   \`\`\`python
   # Before (JSON only)
   response = requests.post(
       "https://api.example.com/v1/analyze",
       json={"prompt": "Extract users"},
       headers={"X-API-Key": api_key}
   )
   
   # After (TOON format)
   response = requests.post(
       "https://api.example.com/v1/analyze",
       json={
           "prompt": "Extract users",
           "output_format": "toon"  # Request TOON format
       },
       headers={"X-API-Key": api_key}
   )
   \`\`\`
   
   ### Step 2: Parse TOON Response
   \`\`\`python
   from toon_format import decode
   
   # Parse TOON response
   toon_string = response.text
   data = decode(toon_string)
   
   # Access fields
   print(data["data"]["intent"])
   \`\`\`
   
   ### Step 3: Measure Savings
   \`\`\`python
   # Check token savings in response headers
   savings = response.headers.get("X-Token-Savings")
   print(f"Token savings: {savings}")
   \`\`\`
   ```

3. **Update README**
   ```markdown
   # README.md updates
   
   ## 🚀 New: TOON Format Support
   
   The API now supports TOON (Token-Oriented Object Notation) format for 30-60% token savings!
   
   ### Quick Start with TOON
   \`\`\`bash
   curl -X POST https://api.example.com/v1/analyze \\
     -H "Content-Type: application/json" \\
     -H "X-API-Key: sp_your_key" \\
     -d '{
       "prompt": "Extract users from: Alice, Bob, Charlie",
       "output_format": "toon"
     }'
   \`\`\`
   
   See [TOON API Guide](docs/TOON_API_GUIDE.md) for details.
   ```

4. **Create Example Notebooks**
   ```python
   # examples/toon_examples.ipynb
   
   # TOON Format Examples
   # Complete Jupyter notebook with:
   - Basic TOON usage
   - Token savings comparison
   - Migration examples
   - Error handling
   - Performance testing
   ```

**Deliverables:**
- âœ… TOON API guide with examples
- âœ… Migration guide for existing clients
- âœ… Updated README with TOON support
- âœ… Example notebooks and code snippets

**Success Criteria:**
- Clear documentation for TOON usage
- Migration path for existing clients
- Example code in multiple languages

---

## Code Changes Required

### Summary of Files to Modify

#### New Files (17 files)

```
app/services/toon_parser.py          # TOON parsing/generation
app/services/toon_validator.py       # TOON validation
app/services/response_formatter.py   # Format conversion
app/services/token_calculator.py     # Token savings tracking
app/prompts/toon_prompts.py          # TOON-specific prompts
app/middleware/format_detection.py   # Format detection
app/models/toon_schemas.py           # TOON Pydantic models
app/api/v1/analyze_toon.py           # Optional TOON endpoint
tests/test_toon_parser.py            # TOON parser tests
tests/test_toon_api.py               # TOON API tests
tests/test_toon_validation.py        # Validation tests
load_tests/toon_load_test.py         # TOON load tests
docs/TOON_API_GUIDE.md               # API documentation
docs/TOON_MIGRATION_GUIDE.md         # Migration guide
examples/toon_examples.ipynb         # Example notebook
monitoring/dashboards/toon_metrics.json  # Grafana dashboard
requirements.txt                      # Add toon-format dependency
```

#### Modified Files (8 files)

```
app/models/requests.py               # Add output_format field
app/api/v1/analyze.py                # Support TOON format
app/services/llm_service.py          # TOON generation
app/services/cache_service.py        # Include format in cache key
app/monitoring/metrics.py            # Add TOON metrics
app/core/config.py                   # TOON configuration
README.md                            # Document TOON support
docker-compose.yml                   # Update dependencies
```

### Estimated Lines of Code

- New Code: ~2,000 lines
- Modified Code: ~500 lines
- Tests: ~1,500 lines
- Documentation: ~2,000 lines
- **Total: ~6,000 lines**

---

## Testing Strategy

### Test Coverage Goals

| Component | Target Coverage |
|-----------|----------------|
| TOON Parser | 95%+ |
| TOON Validator | 90%+ |
| API Endpoints | 85%+ |
| LLM Integration | 80%+ (mock tests) |
| **Overall** | **85%+** |

### Test Types

1. **Unit Tests**
   - TOON parsing (valid/invalid)
   - TOON generation
   - Token calculations
   - Validation logic

2. **Integration Tests**
   - End-to-end TOON flow
   - Cache with TOON
   - Database with TOON responses
   - Error handling

3. **Performance Tests**
   - Load testing (10, 50, 100 users)
   - Token savings measurement
   - Latency comparison (JSON vs TOON)
   - Cache hit rate

4. **Compatibility Tests**
   - JSON backward compatibility
   - Mixed JSON/TOON requests
   - Format conversion accuracy

### Test Data

```python
# tests/fixtures/toon_test_data.py

VALID_TOON_EXAMPLES = [
    """
intent: translate
subject: text
entities:
  source: Hello
  target: French
output_format: text
original_language: en
confidence_score: 0.95
    """,
    """
intent: extract
subject: users
entities [3,]
  name, email, role
  Alice, alice@example.com, admin
  Bob, bob@example.com, user
  Charlie, charlie@example.com, guest
output_format: tabular
original_language: en
confidence_score: 0.92
    """
]

INVALID_TOON_EXAMPLES = [
    "intent: missing_required_fields",
    "{\"json\": \"not toon\"}",
    "invalid: [syntax"
]
```

---

## Migration Path

### Option 1: Gradual Migration (Recommended)

**Timeline:** 4-6 weeks

**Phases:**
1. **Week 1-2:** Deploy TOON support (JSON remains default)
2. **Week 3-4:** Encourage TOON adoption (documentation, examples)
3. **Week 5-6:** Monitor adoption, optimize based on feedback
4. **Future:** Eventually deprecate JSON (if desired)

**Benefits:**
- ✅ Zero disruption to existing clients
- ✅ Time to validate TOON performance
- ✅ Gradual user adoption
- ✅ Easy rollback if issues

**Approach:**
```python
# Default to JSON for backward compatibility
output_format: Literal["json", "toon"] = "json"

# Track adoption
toon_adoption_rate = toon_requests / total_requests
```

### Option 2: Dual-Format Support (Long-term)

**Timeline:** Ongoing

**Approach:**
- Maintain both JSON and TOON indefinitely
- Let clients choose based on needs
- Different pricing tiers (TOON = more efficient = lower cost)

**Benefits:**
- ✅ Maximum flexibility
- ✅ Serve different client needs
- ✅ No forced migration

**Configuration:**
```python
# Per-API-key format preference
class APIKey:
    preferred_format: Literal["json", "toon"] = "json"
    
# Billing based on token usage
billing_rate = tokens_used * rate_per_token
```

### Option 3: TOON-First Migration (Aggressive)

**Timeline:** 2-3 weeks

**Approach:**
1. **Week 1:** Deploy TOON, make it default
2. **Week 2:** Notify clients, provide migration guide
3. **Week 3:** Deprecate JSON with 30-day notice

**Benefits:**
- ✅ Faster cost savings
- ✅ Simpler codebase (eventually)
- ✅ Forces adoption

**Risks:**
- ⚠️  Client disruption
- ⚠️  Migration support burden
- ⚠️  Potential churn

**Not Recommended** unless:
- Small number of clients
- Direct communication channel
- Strong business case for immediate savings

---

## Performance Impact

### Expected Token Savings

Based on TOON specification and examples:

| Data Type | JSON Tokens | TOON Tokens | Savings |
|-----------|-------------|-------------|---------|
| Simple config | 45 | 28 | 38% |
| User list (10) | 185 | 72 | 61% |
| Contact extraction | 145 | 62 | 57% |
| Complex nested | 234 | 142 | 39% |
| **Average** | - | - | **49%** |

### Latency Impact

**Parsing Overhead:**
- JSON parsing: ~0.1ms (native Python)
- TOON parsing: ~0.3-0.5ms (custom parser)
- **Net Impact:** +0.2-0.4ms per request

**LLM Generation Time:**
- Similar for both formats (depends on token count)
- TOON may be slightly faster (fewer tokens to generate)

**Overall:**
- Parsing overhead negligible compared to LLM latency (7-52s)
- Token savings offset any parsing overhead
- **Expected Net Benefit:** Positive (faster + cheaper)

### Cache Considerations

**Cache Key Changes:**
```python
# Before
cache_key = sha256(f"{prompt}:{provider}:{temperature}")

# After (include format)
cache_key = sha256(f"{prompt}:{provider}:{temperature}:{format}")
```

**Cache Size Impact:**
- TOON responses are ~40-50% smaller
- Cache can hold more responses
- Faster cache serialization/deserialization

**Recommendation:**
- Separate cache namespaces for JSON vs TOON
- Allow migration of existing cached JSON to TOON

---

## Risk Assessment

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| TOON parsing errors | Medium | Medium | Lenient parsing mode, error recovery |
| LLM generates invalid TOON | Medium | High | Validation, retry logic, fallback to JSON |
| Performance regression | Low | Medium | Load testing before deployment |
| Cache invalidation issues | Low | Low | Separate cache keys by format |
| Backward compatibility breaks | Low | High | Comprehensive testing, gradual rollout |

### Mitigation Strategies

1. **TOON Generation Failures**
   ```python
   try:
       toon_string = await llm_service.analyze_prompt_toon(prompt)
       structured_data = ToonValidator.validate_structured_data(toon_string)
   except Exception as e:
       logger.error(f"TOON generation failed: {e}")
       # Fallback to JSON
       return await analyze_prompt_json(prompt)
   ```

2. **Progressive Rollout**
   - Deploy to 10% of traffic
   - Monitor error rates
   - Gradually increase to 100%

3. **Feature Flag**
   ```python
   ENABLE_TOON = os.getenv("ENABLE_TOON", "false").lower() == "true"
   
   if ENABLE_TOON and request.output_format == "toon":
       # TOON flow
   else:
       # JSON flow
   ```

4. **Monitoring & Alerts**
   ```yaml
   alerts:
     - name: HighToonErrorRate
       expr: rate(toon_parse_errors_total[5m]) > 0.05  # >5% error rate
       severity: warning
       
     - name: ToonSavingsBelowTarget
       expr: avg(toon_token_savings_percent) < 25  # <25% savings
       severity: info
   ```

### Operational Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Support burden | High | Medium | Comprehensive documentation, examples |
| Client confusion | Medium | Low | Clear migration guide, optional adoption |
| Increased complexity | High | Medium | Good abstractions, test coverage |
| Cost of development | High | Low | Phased approach, reuse existing code |

---

## Success Metrics

### Primary KPIs

1. **Token Savings**
   - Target: 35-55% reduction vs JSON
   - Measurement: Actual token count comparison
   - Alert if <25% savings

2. **TOON Parse Success Rate**
   - Target: >95% success rate
   - Measurement: successful_parses / total_attempts
   - Alert if <90%

3. **Adoption Rate**
   - Target: 50%+ of requests using TOON (within 3 months)
   - Measurement: toon_requests / total_requests
   - Track weekly growth

4. **Cost Savings**
   - Target: Match token savings (35-55% cost reduction)
   - Measurement: (json_cost - toon_cost) / json_cost
   - Monthly reporting

### Secondary KPIs

5. **Latency Impact**
   - Target: <+10% latency increase
   - Measurement: toon_latency / json_latency
   - Alert if >+20%

6. **Cache Hit Rate (TOON)**
   - Target: Maintain 15-20% (same as JSON)
   - Measurement: cache_hits / total_toon_requests

7. **Error Rate**
   - Target: <5% TOON-related errors
   - Measurement: toon_errors / toon_requests

### Tracking Dashboard

```grafana
TOON Adoption & Performance Dashboard
├── TOON Request Rate (requests/sec)
├── Token Savings Distribution (histogram)
├── Format Usage Split (JSON vs TOON pie chart)
├── TOON Parse Success Rate (%)
├── Average Token Savings per Request (%)
├── Cost Savings ($/month)
├── Latency Comparison (TOON vs JSON)
└── Error Rate (TOON vs JSON)
```

---

## Next Steps

### Immediate Actions (This Week)

1. **Review & Approval**
   - Review this conversion strategy
   - Get stakeholder buy-in
   - Approve phased approach

2. **Set Up Development Environment**
   - Install TOON format library (or implement custom parser)
   - Create feature branch: `feature/toon-support`
   - Set up test fixtures

3. **Phase 1 Kickoff**
   - Implement TOON parser module
   - Create unit tests
   - Document TOON format rules

### This Month

4. **Complete Phase 1-3**
   - TOON infrastructure (Week 1)
   - LLM integration (Week 1-2)
   - API endpoints (Week 2)

5. **Testing & Validation**
   - Unit tests (ongoing)
   - Integration tests (Week 2-3)
   - Load tests (Week 3)

### Next Month

6. **Deploy to Staging**
   - Deploy Phase 1-5 code
   - Run comprehensive tests
   - Fix bugs and optimize

7. **Production Rollout**
   - Deploy with feature flag (disabled)
   - Enable for 10% traffic
   - Monitor and iterate

8. **Documentation & Migration**
   - Complete API docs
   - Create migration guide
   - Communicate to clients

---

## Appendix

### A. TOON Format Quick Reference

```toon
# Simple object
key: value
nested:
  sub_key: value

# Primitive array
numbers [3]: 1, 2, 3

# Tabular array (most efficient!)
users [2,]
  name, email, role
  Alice, alice@example.com, admin
  Bob, bob@example.com, user

# List array
items [2]
  - type: book
    title: The Hobbit
  - type: movie
    title: The Matrix
```

### B. Example TOON Responses

**Simple Translation:**
```toon
request_id: abc123
data:
  intent: translate
  subject: text
  entities:
    source: Bonjour
    target_language: English
    translation: Hello
  output_format: text
  original_language: fr
  confidence_score: 0.95
llm_provider: gemini
tokens_used: 89
latency_ms: 234
cached: false
timestamp: 2024-01-15T10:30:00Z
```

**Contact Extraction (Tabular):**
```toon
request_id: def456
data:
  intent: extract
  subject: contacts
  entities:
    contacts [3,]
      name, email, phone
      John Doe, john@example.com, 555-1234
      Jane Smith, jane@example.com, 555-5678
      Bob Jones, bob@example.com, 555-9999
  output_format: tabular
  original_language: en
  confidence_score: 0.92
llm_provider: gemini
tokens_used: 67
latency_ms: 312
cached: false
timestamp: 2024-01-15T10:35:00Z
```

### C. Estimated ROI

**Assumptions:**
- Current traffic: 500K requests/month
- Average JSON tokens per response: 150
- Average TOON tokens per response: 75 (50% savings)
- Token cost: $0.03 per 1K tokens

**Current Cost (JSON):**
- 500K × 150 tokens = 75M tokens/month
- Cost: 75,000 × $0.03 = $2,250/month

**TOON Cost:**
- 500K × 75 tokens = 37.5M tokens/month
- Cost: 37,500 × $0.03 = $1,125/month

**Monthly Savings:** $1,125 (50%)
**Annual Savings:** $13,500

**Development Cost:**
- 3-4 weeks × $2,000/week = ~$8,000

**ROI:** 8 months to break even, then $13.5K/year savings

---

## Conclusion

Converting the Structured Prompt Service to support TOON format is a **high-value, moderate-effort** initiative that will:

âœ… Reduce token usage by 30-60% (target: 45% average)
âœ… Lower LLM API costs proportionally
âœ… Improve response times (fewer tokens to process)
âœ… Maintain full backward compatibility with JSON
âœ… Provide a competitive advantage (token-efficient API)

**Recommended Approach:** Gradual migration with dual-format support

**Timeline:** 3-4 weeks for full implementation

**Next Step:** Review and approve Phase 1 (Foundation) to begin implementation

---

**Document Version:** 1.0
**Last Updated:** [Current Date]
**Author:** Development Team
**Status:** Awaiting Approval
