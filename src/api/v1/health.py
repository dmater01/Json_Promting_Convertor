"""Health check endpoint."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import time
from typing import Dict, Any

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

from src.adapters.db_client import get_db_session
from src.adapters.cache_client import get_cache_client
from src.core.config import settings
from src.core.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter()

# Track application start time
start_time = time.time()


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db_session)):
    """
    Health check endpoint with detailed diagnostics.

    Returns service health status, dependency checks, and system metrics.

    Returns:
        dict: Comprehensive health status information
    """
    health_status = {
        "status": "healthy",
        "version": settings.app_version,
        "environment": settings.environment,
        "uptime_seconds": int(time.time() - start_time),
        "timestamp": int(time.time()),
        "dependencies": {},
        "system": {},
    }

    # Check database connection with latency
    db_start = time.time()
    try:
        result = await db.execute(text("SELECT 1"))
        result.scalar()
        db_latency_ms = (time.time() - db_start) * 1000
        health_status["dependencies"]["postgres"] = {
            "status": "up",
            "latency_ms": round(db_latency_ms, 2),
        }
    except Exception as e:
        db_latency_ms = (time.time() - db_start) * 1000
        health_status["dependencies"]["postgres"] = {
            "status": "down",
            "latency_ms": round(db_latency_ms, 2),
            "error": str(e)[:100],
        }
        health_status["status"] = "degraded"
        logger.error("Database health check failed", extra={"error": str(e)})

    # Check Redis connection with latency
    redis_start = time.time()
    try:
        cache_client = await get_cache_client()
        await cache_client._client.ping()
        redis_latency_ms = (time.time() - redis_start) * 1000

        # Get Redis info
        info = await cache_client._client.info()
        health_status["dependencies"]["redis"] = {
            "status": "up",
            "latency_ms": round(redis_latency_ms, 2),
            "used_memory_mb": round(info.get("used_memory", 0) / 1024 / 1024, 2),
            "connected_clients": info.get("connected_clients", 0),
        }
    except Exception as e:
        redis_latency_ms = (time.time() - redis_start) * 1000
        health_status["dependencies"]["redis"] = {
            "status": "down",
            "latency_ms": round(redis_latency_ms, 2),
            "error": str(e)[:100],
        }
        health_status["status"] = "degraded"
        logger.error("Redis health check failed", extra={"error": str(e)})

    # System metrics (optional, requires psutil)
    if PSUTIL_AVAILABLE:
        try:
            health_status["system"] = {
                "cpu_percent": round(psutil.cpu_percent(interval=0.1), 1),
                "memory_percent": round(psutil.virtual_memory().percent, 1),
                "disk_percent": round(psutil.disk_usage('/').percent, 1),
            }
        except Exception as e:
            logger.warning("System metrics collection failed", extra={"error": str(e)})

    # Determine overall status
    if health_status["dependencies"]["postgres"]["status"] == "down":
        health_status["status"] = "unhealthy"
    elif any(dep.get("status") == "down" for dep in health_status["dependencies"].values() if isinstance(dep, dict)):
        health_status["status"] = "degraded"

    return health_status


@router.get("/ready")
async def readiness_check(db: AsyncSession = Depends(get_db_session)):
    """
    Readiness check endpoint for Kubernetes.

    Returns 200 if the service is ready to accept traffic.

    Returns:
        dict: Readiness status
    """
    try:
        # Check critical dependencies
        await db.execute(text("SELECT 1"))
        return {"ready": True}
    except Exception:
        return {"ready": False}


@router.get("/live")
async def liveness_check():
    """
    Liveness check endpoint for Kubernetes.

    Returns 200 if the service is alive (process is running).

    Returns:
        dict: Liveness status
    """
    return {"alive": True}
