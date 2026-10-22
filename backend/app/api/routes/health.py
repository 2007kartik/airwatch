"""
AirWatch — Health Check API Route
"""

from __future__ import annotations

from datetime import datetime, timezone
from fastapi import APIRouter

from app.core.config import settings
from app.db.session import check_db_connection
from app.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """
    Returns API status, database connectivity, environment mode, and current UTC time.
    Database connectivity is verified via a live query (SELECT 1).
    """
    db_ok = check_db_connection()
    return HealthResponse(
        status="ok",
        environment=settings.app_env,
        database="connected" if db_ok else "unreachable",
        timestamp=datetime.now(timezone.utc),
        version="0.1.0",
        data_notice="All sensor data is SIMULATED (no physical hardware).",
    )
