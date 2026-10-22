"""
AirWatch — Sensor Reading Schemas
Defines Pydantic request and response models for sensor readings.
All sensor data from this project is SIMULATED.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ReadingBase(BaseModel):
    """Base sensor reading fields shared by create and response schemas."""

    timestamp: datetime = Field(
        ...,
        description="UTC timestamp of the reading (ISO 8601)",
    )
    temperature_c: float = Field(
        ...,
        ge=-50.0,
        le=100.0,
        description="Simulated temperature in Celsius (-50°C to 100°C)",
    )
    humidity_percent: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Simulated relative humidity percentage (0% to 100%)",
    )
    gas_raw_value: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=10000.0,
        description="Simulated raw gas sensor indicator (MQ-series-like)",
    )
    pm25_ug_m3: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1000.0,
        description="Simulated PM2.5 indicator in µg/m³ (illustrative only)",
    )
    pm10_ug_m3: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=2000.0,
        description="Simulated PM10 indicator in µg/m³ (illustrative only)",
    )
    source: str = Field(
        default="simulated",
        max_length=50,
        description="Data source identifier; always 'simulated' for this prototype",
    )

    @field_validator("timestamp")
    @classmethod
    def ensure_utc_timestamp(cls, v: datetime) -> datetime:
        """Ensure timestamps are timezone-aware and converted to UTC."""
        if v.tzinfo is None:
            # If naive, assume UTC
            return v.replace(tzinfo=timezone.utc)
        return v.astimezone(timezone.utc)


class ReadingCreate(ReadingBase):
    """Request schema for ingesting a reading via POST /api/readings."""
    pass


class ReadingResponse(ReadingBase):
    """Response schema representing a stored sensor reading."""

    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReadingListResponse(BaseModel):
    """Paginated list of sensor readings."""

    items: list[ReadingResponse]
    total: int
    limit: int
    offset: int


class ReadingIngestResult(BaseModel):
    """Detailed response returned after ingesting a sensor reading."""

    reading: ReadingResponse
    alerts_triggered: list[dict] = Field(
        default_factory=list,
        description="List of alerts created as a result of threshold evaluation",
    )
    message: str = "Reading ingested successfully"
