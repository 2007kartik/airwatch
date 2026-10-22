"""
AirWatch — Schemas Package
"""

from app.schemas.alert import (
    AlertAcknowledgeResponse,
    AlertListResponse,
    AlertResponse,
    AlertSeverity,
    AlertStatus,
)
from app.schemas.analytics import (
    AnalyticsSummary,
    AnalyticsTrends,
    MetricSummary,
    TrendPoint,
)
from app.schemas.health import HealthResponse
from app.schemas.reading import (
    ReadingBase,
    ReadingCreate,
    ReadingIngestResult,
    ReadingListResponse,
    ReadingResponse,
)

__all__ = [
    "ReadingBase",
    "ReadingCreate",
    "ReadingResponse",
    "ReadingListResponse",
    "ReadingIngestResult",
    "AlertResponse",
    "AlertAcknowledgeResponse",
    "AlertListResponse",
    "AlertSeverity",
    "AlertStatus",
    "MetricSummary",
    "AnalyticsSummary",
    "TrendPoint",
    "AnalyticsTrends",
    "HealthResponse",
]
