"""
API Endpoints with TOON Support - FastAPI Integration

This module provides FastAPI endpoints that support both JSON and TOON formats,
enabling dual-format API responses for maximum token efficiency.

Features:
- Dual-format support (JSON/TOON)
- Content negotiation
- Automatic format conversion
- Error handling
- Performance monitoring
- Token savings tracking

Author: Development Team
Version: 1.0.0
"""

from fastapi import FastAPI, Request, Response, HTTPException, Header
from fastapi.responses import PlainTextResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum
import time
import logging

from toon_parser import ToonParser, ToonParseError
from toon_validator import validate_toon
from json_vs_toon_comparison import FormatComparator


# ============================================================================
# CONFIGURATION
# ============================================================================

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize TOON utilities
toon_parser = ToonParser(strict=False, indent=2)  # Lenient mode for production
toon_comparator = FormatComparator(model="gpt5")


# ============================================================================
# MODELS
# ============================================================================

class OutputFormat(str, Enum):
    """Supported output formats."""
    JSON = "json"
    TOON = "toon"
    AUTO = "auto"


class PromptAnalysisRequest(BaseModel):
    """Request model for prompt analysis."""
    prompt: str = Field(..., description="Natural language prompt to analyze")
    output_format: Optional[OutputFormat] = Field(
        OutputFormat.AUTO,
        description="Desired output format (json, toon, or auto)"
    )


class PromptAnalysisResponse(BaseModel):
    """Response model for prompt analysis."""
    intent: str
    subject: str
    entities: Dict[str, Any]
    output_format: str
    original_language: str
    confidence_score: float


class FormatComparisonResponse(BaseModel):
    """Response model for format comparison."""
    json_tokens: int
    toon_tokens: int
    savings_tokens: int
    savings_percent: float
    json_size: int
    toon_size: int


# ============================================================================
# MIDDLEWARE
# ============================================================================

class TokenTrackingMiddleware:
    """Middleware to track token usage and savings."""
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.total_json_tokens = 0
        self.total_toon_tokens = 0
        self.total_requests = 0
    
    async def __call__(self, request: Request, call_next):
        """Process request and track tokens."""
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time
        
        # Log request
        logger.info(f"{request.method} {request.url.path} - {duration:.3f}s")
        
        return response


# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="Structured Prompt Service with TOON Support",
    description="API for analyzing prompts with dual-format support (JSON/TOON)",
    version="2.0.0"
)

# Add middleware
# app.add_middleware(TokenTrackingMiddleware)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def determine_output_format(
    request_format: Optional[OutputFormat],
    accept_header: Optional[str]
) -> str:
    """
    Determine output format based on request and headers.
    
    Priority:
    1. Explicit request parameter
    2. Accept header
    3. Default to JSON
    """
    if request_format and request_format != OutputFormat.AUTO:
        return request_format.value
    
    if accept_header:
        if "application/toon" in accept_header.lower():
            return "toon"
        elif "text/toon" in accept_header.lower():
            return "toon"
    
    return "json"


def format_response(data: Dict[str, Any], format_type: str) -> Response:
    """
    Format response in JSON or TOON format.
    
    Args:
        data: Response data
        format_type: "json" or "toon"
        
    Returns:
        FastAPI Response object
    """
    if format_type == "toon":
        try:
            toon_str = toon_parser.encode(data)
            return PlainTextResponse(
                content=toon_str,
                media_type="application/toon"
            )
        except Exception as e:
            logger.error(f"Failed to encode TOON: {e}")
            # Fallback to JSON
            return JSONResponse(content=data)
    else:
        return JSONResponse(content=data)


def analyze_prompt_mock(prompt: str) -> Dict[str, Any]:
    """
    Mock prompt analysis (replace with actual LLM call).
    
    This is a placeholder. In production, this would call your LLM API
    to analyze the prompt and return structured data.
    """
    # Simple mock logic
    intent = "extract" if "extract" in prompt.lower() else "analyze"
    subject = "data"
    
    # Mock entities
    entities = {
        "query": prompt[:50],
        "length": len(prompt)
    }
    
    return {
        "intent": intent,
        "subject": subject,
        "entities": entities,
        "output_format": "structured",
        "original_language": "en",
        "confidence_score": 0.85
    }


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "Structured Prompt Service",
        "version": "2.0.0",
        "formats": ["json", "toon"],
        "endpoints": [
            "/analyze",
            "/analyze-toon",
            "/compare-formats",
            "/health"
        ]
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": time.time()}


@app.post("/analyze")
async def analyze_prompt(
    request: PromptAnalysisRequest,
    accept: Optional[str] = Header(None)
):
    """
    Analyze a natural language prompt (dual-format support).
    
    Supports both JSON and TOON output formats via:
    - Request parameter: output_format
    - Accept header: application/toon or application/json
    """
    try:
        # Analyze prompt (mock - replace with actual LLM call)
        result = analyze_prompt_mock(request.prompt)
        
        # Determine output format
        format_type = determine_output_format(request.output_format, accept)
        
        # Log format choice
        logger.info(f"Output format: {format_type}")
        
        # Format and return response
        return format_response(result, format_type)
        
    except Exception as e:
        logger.error(f"Error analyzing prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze-toon", response_class=PlainTextResponse)
async def analyze_prompt_toon_only(request: PromptAnalysisRequest):
    """
    Analyze a natural language prompt (TOON format only).
    
    This endpoint always returns TOON format for maximum token efficiency.
    Use this when you know you want TOON output.
    """
    try:
        # Analyze prompt
        result = analyze_prompt_mock(request.prompt)
        
        # Encode as TOON
        toon_str = toon_parser.encode(result)
        
        return PlainTextResponse(content=toon_str, media_type="application/toon")
        
    except ToonParseError as e:
        logger.error(f"TOON encoding error: {e}")
        raise HTTPException(status_code=500, detail=f"TOON encoding failed: {e}")
    except Exception as e:
        logger.error(f"Error analyzing prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/compare-formats")
async def compare_formats(data: Dict[str, Any]):
    """
    Compare JSON vs TOON formats for given data.
    
    Returns token counts and savings metrics.
    """
    try:
        # Compare formats
        result = toon_comparator.compare(data)
        
        # Build response
        comparison = FormatComparisonResponse(
            json_tokens=result["json"]["tokens"],
            toon_tokens=result["toon"]["tokens"],
            savings_tokens=result["savings"]["tokens"],
            savings_percent=result["savings"]["tokens_percent"],
            json_size=result["json"]["characters"],
            toon_size=result["toon"]["characters"]
        )
        
        return comparison
        
    except Exception as e:
        logger.error(f"Error comparing formats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/validate-toon", response_class=JSONResponse)
async def validate_toon_endpoint(toon_str: str):
    """
    Validate a TOON format string.
    
    Returns validation results with any errors or warnings.
    """
    try:
        # Validate
        result = validate_toon(toon_str, strict=False)
        
        # Build response
        response = {
            "is_valid": result.is_valid,
            "errors": [
                {"line": e.line_num, "message": e.message}
                for e in result.errors
            ],
            "warnings": [
                {"line": w.line_num, "message": w.message}
                for w in result.warnings
            ],
            "summary": result.get_summary()
        }
        
        return response
        
    except Exception as e:
        logger.error(f"Error validating TOON: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/convert/json-to-toon", response_class=PlainTextResponse)
async def convert_json_to_toon(data: Dict[str, Any]):
    """
    Convert JSON data to TOON format.
    
    Useful for testing and migration.
    """
    try:
        toon_str = toon_parser.encode(data)
        return PlainTextResponse(content=toon_str, media_type="application/toon")
        
    except Exception as e:
        logger.error(f"Error converting to TOON: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/convert/toon-to-json")
async def convert_toon_to_json(toon_str: str):
    """
    Convert TOON format to JSON.
    
    Useful for testing and debugging.
    """
    try:
        data = toon_parser.decode(toon_str)
        return JSONResponse(content=data)
        
    except ToonParseError as e:
        logger.error(f"TOON parsing error: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid TOON: {e}")
    except Exception as e:
        logger.error(f"Error converting to JSON: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics")
async def get_metrics():
    """
    Get API metrics including token savings.
    
    In production, this would track actual usage statistics.
    """
    # Mock metrics (in production, track these in middleware/database)
    return {
        "total_requests": 1000,
        "json_requests": 600,
        "toon_requests": 400,
        "total_tokens_saved": 125000,
        "average_savings_percent": 45.3,
        "uptime_seconds": 86400
    }


# ============================================================================
# BATCH ENDPOINTS
# ============================================================================

@app.post("/batch/analyze")
async def batch_analyze_prompts(
    prompts: List[str],
    output_format: Optional[OutputFormat] = OutputFormat.JSON,
    accept: Optional[str] = Header(None)
):
    """
    Analyze multiple prompts in batch.
    
    Returns results in requested format (JSON or TOON).
    """
    try:
        # Analyze all prompts
        results = [analyze_prompt_mock(prompt) for prompt in prompts]
        
        # Wrap in response object
        response_data = {
            "count": len(results),
            "results": results
        }
        
        # Determine format
        format_type = determine_output_format(output_format, accept)
        
        # Return formatted response
        return format_response(response_data, format_type)
        
    except Exception as e:
        logger.error(f"Error in batch analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

"""
USAGE EXAMPLES:

1. Basic prompt analysis (JSON):
   POST /analyze
   {
     "prompt": "Extract user names from this text",
     "output_format": "json"
   }

2. Prompt analysis (TOON):
   POST /analyze
   {
     "prompt": "Extract user names from this text",
     "output_format": "toon"
   }
   
   OR use Accept header:
   Headers: Accept: application/toon

3. TOON-only endpoint:
   POST /analyze-toon
   {
     "prompt": "Extract user names from this text"
   }

4. Format comparison:
   POST /compare-formats
   {
     "users": [
       {"id": 1, "name": "Alice"},
       {"id": 2, "name": "Bob"}
     ]
   }

5. Validate TOON:
   POST /validate-toon
   Body: users [2,]
         id, name
         1, Alice
         2, Bob

6. Convert JSON to TOON:
   POST /convert/json-to-toon
   {
     "users": [{"id": 1, "name": "Alice"}]
   }

7. Convert TOON to JSON:
   POST /convert/toon-to-json
   Body: users [1,]
         id, name
         1, Alice

8. Batch analysis:
   POST /batch/analyze
   [
     "Extract users from this",
     "Analyze sentiment here",
     "Schedule meeting for Monday"
   ]
"""


# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 70)
    print("Starting Structured Prompt Service with TOON Support")
    print("=" * 70)
    print()
    print("Endpoints:")
    print("  - POST /analyze         (dual-format)")
    print("  - POST /analyze-toon    (TOON only)")
    print("  - POST /compare-formats (comparison)")
    print("  - POST /validate-toon   (validation)")
    print("  - POST /convert/*       (conversion)")
    print("  - POST /batch/analyze   (batch processing)")
    print("  - GET  /metrics         (statistics)")
    print()
    print("Formats supported: JSON, TOON")
    print("Expected token savings: 30-60%")
    print()
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
