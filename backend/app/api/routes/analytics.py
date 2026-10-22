"""
AirWatch — Analytics API Routes
Provides KPI aggregate statistics and time-series trends for charts.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.analytics import AnalyticsSummary, AnalyticsTrends
from app.services import analytics_service

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get(
    "/summary",
    response_model=AnalyticsSummary,
    summary="Get KPI summary statistics",
)
def get_analytics_summary(
    range_filter: str = Query(
        "24h",
        alias="range",
        description="Time period to aggregate (e.g., '1h', '6h', '24h', '7d', 'all')",
    ),
    db: Session = Depends(get_db),
) -> AnalyticsSummary:
    """
    Returns aggregate statistics (average, minimum, maximum, current)
    for temperature, humidity, gas levels, and simulated particulate indicators,
    along with total readings and active alert counts.
    """
    return analytics_service.get_analytics_summary(db, time_window=range_filter)


@router.get(
    "/trends",
    response_model=AnalyticsTrends,
    summary="Get time-series data for dashboard trend charts",
)
def get_analytics_trends(
    range_filter: str = Query(
        "1h",
        alias="range",
        description="Time range for chart series (e.g., '1h', '6h', '24h', '7d')",
    ),
    limit: int = Query(
        200,
        ge=10,
        le=1000,
        description="Maximum number of time-series points to return",
    ),
    db: Session = Depends(get_db),
) -> AnalyticsTrends:
    """
    Returns time-series points in chronological order (oldest to newest)
    for rendering line charts in the React frontend.
    """
    return analytics_service.get_analytics_trends(
        db,
        time_range=range_filter,
        limit=limit,
    )
