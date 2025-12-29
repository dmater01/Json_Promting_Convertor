"""Main FastAPI application."""

import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

from src.adapters.cache_client import close_cache_client, get_cache_client
from src.adapters.db_client import close_db, init_db
from src.api.middleware.error_handlers import register_exception_handlers
from src.api.middleware.rate_limit_headers import RateLimitHeadersMiddleware
from src.api.v1 import analyze, api_keys, health
from src.core.config import settings
from src.core.logging_config import setup_logging

# Set up logging
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print("🚀 Starting Structured Prompt Service...")
    await init_db()
    print("✅ Database connection established")

    # Initialize cache
    cache = await get_cache_client()
    print("✅ Cache client initialized")

    yield

    # Shutdown
    print("👋 Shutting down Structured Prompt Service...")
    await close_cache_client()
    print("✅ Cache client closed")
    await close_db()
    print("✅ Database connection closed")


# Create FastAPI application
app = FastAPI(
    title="Structured Prompt Service",
    description="Production API service that transforms natural language prompts into validated structured data using LLMs",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limit Headers Middleware
app.add_middleware(RateLimitHeadersMiddleware)


# Request ID Middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add unique request ID to all requests."""
    request.state.request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    response = await call_next(request)
    response.headers["X-Request-ID"] = request.state.request_id
    return response


# Register exception handlers
register_exception_handlers(app)

# Include routers
app.include_router(health.router, prefix="/v1", tags=["health"])
app.include_router(api_keys.router, prefix="/v1/api-keys", tags=["api-keys"])
app.include_router(analyze.router, prefix="/v1/analyze", tags=["analyze"])

# Prometheus metrics instrumentation
Instrumentator().instrument(app).expose(app, endpoint="/v1/metrics", include_in_schema=False)


# Root endpoint
@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint."""
    return {
        "name": "Structured Prompt Service",
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
        "health": "/v1/health",
        "api_keys": "/v1/api-keys",
        "analyze": "/v1/analyze",
        "metrics": "/v1/metrics",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level="info",
    )
