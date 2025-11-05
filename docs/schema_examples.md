# Schema Examples

This document provides comprehensive examples of request and response schemas for the Structured Prompt Service API.

## Request Examples

### Basic Request (Minimal)

```json
{
  "prompt": "Translate 'Bonjour' to English"
}
```

**Response:**
```json
{
  "request_id": "123e4567-e89b-12d3-a456-426614174000",
  "data": {
    "intent": "translate",
    "subject": "text",
    "entities": {
      "source": "Bonjour",
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

### Full Request (All Options)

```json
{
  "prompt": "Create a JSON schema for a user profile with name (string), email (string, must be valid email), and age (integer, must be 18+)",
  "output_format": "json",
  "schema_definition": {
    "type": "object",
    "properties": {
      "intent": {"type": "string"},
      "subject": {"type": "string"},
      "entities": {"type": "object"}
    },
    "required": ["intent", "subject"]
  },
  "llm_provider": "gemini",
  "temperature": 0.3,
  "max_tokens": 2000,
  "cache_ttl": 3600,
  "metadata": {
    "user_id": "user_123",
    "session_id": "session_abc",
    "source": "web_app"
  }
}
```

### XML Output Request

```json
{
  "prompt": "Extract product information: 'iPhone 15 Pro, 256GB, Titanium Blue, $999'",
  "output_format": "xml"
}
```

**Response (data field as XML):**
```json
{
  "request_id": "789e0123-e89b-12d3-a456-426614174000",
  "data": {
    "intent": "extract",
    "subject": "product information",
    "entities": {
      "product_name": "iPhone 15 Pro",
      "storage": "256GB",
      "color": "Titanium Blue",
      "price": "$999"
    },
    "output_format": "structured",
    "original_language": "en",
    "confidence_score": 0.92
  },
  "llm_provider": "gemini",
  "model_name": "gemini-pro-latest",
  "tokens_used": 187,
  "latency_ms": 312,
  "cached": false,
  "validated": true,
  "timestamp": "2024-01-15T10:35:00Z"
}
```

### Multilingual Request

```json
{
  "prompt": "Analyze the sentiment of this Spanish review: 'Me encanta este producto, es excelente!'",
  "llm_provider": "claude",
  "temperature": 0.1
}
```

**Response:**
```json
{
  "request_id": "abc123-def456",
  "data": {
    "intent": "analyze",
    "subject": "sentiment",
    "entities": {
      "text": "Me encanta este producto, es excelente!",
      "sentiment": "positive",
      "score": 0.95
    },
    "output_format": "sentiment_analysis",
    "original_language": "es",
    "confidence_score": 0.93
  },
  "llm_provider": "claude",
  "model_name": "claude-3-sonnet-20240229",
  "tokens_used": 156,
  "latency_ms": 289,
  "cached": false,
  "validated": true,
  "timestamp": "2024-01-15T10:40:00Z"
}
```

### Request with Custom Schema Validation

```json
{
  "prompt": "Extract contact info from: 'John Doe, john@example.com, (555) 123-4567'",
  "schema_definition": {
    "type": "object",
    "properties": {
      "intent": {"type": "string"},
      "subject": {"type": "string"},
      "entities": {
        "type": "object",
        "properties": {
          "name": {"type": "string"},
          "email": {"type": "string", "format": "email"},
          "phone": {"type": "string"}
        },
        "required": ["name", "email"]
      }
    },
    "required": ["intent", "subject", "entities"]
  }
}
```

### Cached Response Example

```json
{
  "prompt": "Translate 'Hello world' to French"
}
```

**Response (from cache, low latency):**
```json
{
  "request_id": "cached-001",
  "data": {
    "intent": "translate",
    "subject": "text",
    "entities": {
      "source": "Hello world",
      "target_language": "French",
      "translation": "Bonjour le monde"
    },
    "output_format": "text",
    "original_language": "en",
    "confidence_score": 0.98
  },
  "llm_provider": "gemini",
  "model_name": "gemini-pro-latest",
  "tokens_used": 145,
  "latency_ms": 12,
  "cached": true,
  "validated": true,
  "timestamp": "2024-01-15T10:45:00Z"
}
```

## Error Response Examples

### Validation Error

```json
{
  "error": {
    "type": "validation_error",
    "message": "Prompt cannot be empty or only whitespace",
    "field": "prompt"
  },
  "request_id": "error-001",
  "timestamp": "2024-01-15T10:50:00Z"
}
```

### LLM Provider Error

```json
{
  "error": {
    "type": "llm_error",
    "message": "Gemini API temporarily unavailable",
    "details": {
      "provider": "gemini",
      "status_code": 503,
      "retry_after": 30
    }
  },
  "request_id": "error-002",
  "timestamp": "2024-01-15T10:51:00Z"
}
```

### Rate Limit Error

```json
{
  "error": {
    "type": "rate_limit_exceeded",
    "message": "Rate limit exceeded: 1000 requests per hour",
    "details": {
      "limit": 1000,
      "remaining": 0,
      "reset_at": "2024-01-15T11:00:00Z"
    }
  },
  "request_id": "error-003",
  "timestamp": "2024-01-15T10:52:00Z"
}
```

### Schema Validation Error

```json
{
  "error": {
    "type": "schema_validation_error",
    "message": "LLM output does not match provided schema",
    "field": "entities",
    "details": {
      "expected": "object with required fields: name, email",
      "received": "object missing field: email"
    }
  },
  "request_id": "error-004",
  "timestamp": "2024-01-15T10:53:00Z"
}
```

### Invalid Temperature Error

```json
{
  "error": {
    "type": "validation_error",
    "message": "Input should be less than or equal to 2",
    "field": "temperature",
    "details": {
      "input": 3.0,
      "constraint": "le=2.0"
    }
  },
  "request_id": "error-005",
  "timestamp": "2024-01-15T10:54:00Z"
}
```

## Complex Use Cases

### Use Case 1: Multi-Entity Extraction

**Request:**
```json
{
  "prompt": "Parse this meeting request: 'Team standup on Monday at 10am EST with John, Sarah, and Mike. Discuss Q4 roadmap and budget allocation.'",
  "llm_provider": "gpt-4",
  "temperature": 0.1
}
```

**Response:**
```json
{
  "request_id": "complex-001",
  "data": {
    "intent": "parse",
    "subject": "meeting request",
    "entities": {
      "meeting_type": "standup",
      "day": "Monday",
      "time": "10am EST",
      "participants": ["John", "Sarah", "Mike"],
      "topics": ["Q4 roadmap", "budget allocation"]
    },
    "output_format": "structured",
    "original_language": "en",
    "confidence_score": 0.89
  },
  "llm_provider": "gpt-4",
  "model_name": "gpt-4-turbo",
  "tokens_used": 421,
  "latency_ms": 1203,
  "cached": false,
  "validated": true,
  "timestamp": "2024-01-15T11:00:00Z"
}
```

### Use Case 2: Code Generation Intent

**Request:**
```json
{
  "prompt": "Create a Python function that validates email addresses using regex",
  "output_format": "json",
  "metadata": {
    "user_role": "developer",
    "project": "email_validator"
  }
}
```

**Response:**
```json
{
  "request_id": "code-001",
  "data": {
    "intent": "create",
    "subject": "Python function",
    "entities": {
      "purpose": "validate email addresses",
      "method": "regex",
      "language": "Python"
    },
    "output_format": "code",
    "original_language": "en",
    "confidence_score": 0.91
  },
  "llm_provider": "gemini",
  "model_name": "gemini-pro-latest",
  "tokens_used": 298,
  "latency_ms": 567,
  "cached": false,
  "validated": true,
  "timestamp": "2024-01-15T11:05:00Z"
}
```

## Field Descriptions

### Request Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `prompt` | string | Yes | - | Natural language prompt (1-10,000 chars) |
| `output_format` | enum | No | `"json"` | Output format: `"json"` or `"xml"` |
| `schema_definition` | object | No | `null` | JSON Schema for validation |
| `llm_provider` | enum | No | `"auto"` | Provider: `"auto"`, `"gemini"`, `"claude"`, `"gpt-4"` |
| `temperature` | float | No | `0.1` | LLM temperature (0.0-2.0) |
| `max_tokens` | integer | No | `2000` | Max tokens (50-8000) |
| `cache_ttl` | integer | No | `3600` | Cache TTL in seconds (0-86400) |
| `metadata` | object | No | `null` | Custom metadata for logging |

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `request_id` | string | Unique request UUID |
| `data` | object | Structured data (StructuredData schema) |
| `data.intent` | string | Primary action/intent |
| `data.subject` | string | Main topic/object |
| `data.entities` | object | Extracted key-value pairs |
| `data.output_format` | string | Desired result format |
| `data.original_language` | string | ISO 639-1 language code |
| `data.confidence_score` | float | Confidence (0.0-1.0) |
| `llm_provider` | string | Provider used |
| `model_name` | string | Specific model used |
| `tokens_used` | integer | Total tokens consumed |
| `latency_ms` | integer | Processing time in ms |
| `cached` | boolean | Whether served from cache |
| `validated` | boolean | Schema validation passed |
| `timestamp` | string | Response timestamp (ISO 8601) |

### Error Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `error.type` | string | Error type identifier |
| `error.message` | string | Human-readable message |
| `error.field` | string | Field name (validation errors) |
| `error.details` | object | Additional error context |
| `request_id` | string | Request UUID if available |
| `timestamp` | string | Error timestamp (ISO 8601) |

## Testing with cURL

### Basic Request
```bash
curl -X POST http://localhost:8000/v1/analyze \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "prompt": "Translate hello to French"
  }'
```

### Full Request
```bash
curl -X POST http://localhost:8000/v1/analyze \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "prompt": "Create a user profile for John Doe, age 30",
    "output_format": "json",
    "llm_provider": "gemini",
    "temperature": 0.3,
    "max_tokens": 1000
  }'
```
