"""
AirWatch — Health Check Schema
"""

from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health status response."""

    status: str
    environment: str
    database: str
    timestamp: datetime
    version: str = "0.1.0"
    data_notice: str = "All sensor data is SIMULATED (no physical hardware)."
