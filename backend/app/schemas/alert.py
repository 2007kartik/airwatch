"""
AirWatch — Alert Schemas
Defines Pydantic models for alerts triggered by threshold violations.
All thresholds are configurable demo thresholds — not regulatory health advice.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


AlertSeverity = Literal["warning", "critical"]
AlertStatus = Literal["active", "acknowledged"]


class AlertResponse(BaseModel):
    """Response schema representing an alert."""

    id: int
    reading_id: int
    alert_type: str = Field(
        ...,
        description="Type of alert, e.g. temperature_high, pm25_high",
    )
    severity: str = Field(
        ...,
        description="'warning' or 'critical'",
    )
    message: str = Field(
        ...,
        description="Human-readable description of the threshold violation",
    )
    observed_value: Optional[float] = Field(
        default=None,
        description="Value observed in the sensor reading",
    )
    threshold_value: Optional[float] = Field(
        default=None,
        description="Configured demo threshold that was exceeded",
    )
    status: str = Field(
        ...,
        description="'active' or 'acknowledged'",
    )
    created_at: datetime
    acknowledged_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AlertAcknowledgeResponse(BaseModel):
    """Response returned when an alert is acknowledged."""

    id: int
    status: str = "acknowledged"
    acknowledged_at: datetime
    message: str = "Alert acknowledged successfully"


class AlertListResponse(BaseModel):
    """Paginated list of alerts with active count metadata."""

    items: list[AlertResponse]
    total: int
    active_count: int
    acknowledged_count: int
    limit: int
    offset: int
