"""
AirWatch — Analytics Schemas
Defines models for summary metrics and historical trend series.
All values reflect SIMULATED data.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.reading import ReadingResponse


class MetricSummary(BaseModel):
    """Aggregate statistics for a single environmental metric."""

    avg: Optional[float] = Field(default=None, description="Average value")
    min: Optional[float] = Field(default=None, description="Minimum value")
    max: Optional[float] = Field(default=None, description="Maximum value")
    current: Optional[float] = Field(default=None, description="Most recent observed value")


class AnalyticsSummary(BaseModel):
    """Overview summary for the dashboard KPI cards and analytics panel."""

    time_window: str = Field(
        ...,
        description="Time period considered (e.g., '1h', '6h', '24h', 'all')",
    )
    total_readings: int = Field(
        ...,
        description="Total readings recorded in this window",
    )
    active_alerts: int = Field(
        ...,
        description="Number of currently active alerts",
    )
    total_alerts: int = Field(
        ...,
        description="Total alerts generated in this window",
    )
    temperature: MetricSummary
    humidity: MetricSummary
    gas_raw: MetricSummary
    pm25: MetricSummary
    pm10: MetricSummary
    latest_reading: Optional[ReadingResponse] = None
    data_notice: str = "All values are SIMULATED. Not official or regulated data."


class TrendPoint(BaseModel):
    """A single time-series data point for chart visualization."""

    timestamp: datetime
    temperature_c: float
    humidity_percent: float
    gas_raw_value: Optional[float] = None
    pm25_ug_m3: Optional[float] = None
    pm10_ug_m3: Optional[float] = None


class AnalyticsTrends(BaseModel):
    """Time-series chart dataset."""

    time_range: str = Field(
        ...,
        description="Range queried (e.g. '1h', '6h', '24h', '7d')",
    )
    count: int = Field(
        ...,
        description="Number of points returned",
    )
    points: list[TrendPoint]
    data_notice: str = "All values are SIMULATED. Illustrative only."
