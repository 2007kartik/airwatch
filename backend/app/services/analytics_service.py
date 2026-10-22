"""
AirWatch — Analytics Service
Calculates summary KPI aggregates and historical trend series for charts.
All data is SIMULATED.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.models.sensor_reading import SensorReading
from app.schemas.analytics import (
    AnalyticsSummary,
    AnalyticsTrends,
    MetricSummary,
    TrendPoint,
)
from app.schemas.reading import ReadingResponse
from app.services.reading_service import get_latest_reading

logger = logging.getLogger("airwatch.services.analytics")


def _get_cutoff(time_str: str) -> Optional[datetime]:
    """Converts a time-window string (e.g., '1h', '6h', '24h', '7d') to a UTC cutoff datetime."""
    now = datetime.now(timezone.utc)
    unit_map = {
        "15m": timedelta(minutes=15),
        "30m": timedelta(minutes=30),
        "1h": timedelta(hours=1),
        "3h": timedelta(hours=3),
        "6h": timedelta(hours=6),
        "12h": timedelta(hours=12),
        "24h": timedelta(hours=24),
        "1d": timedelta(days=1),
        "7d": timedelta(days=7),
        "30d": timedelta(days=30),
    }
    return now - unit_map[time_str.lower()] if time_str.lower() in unit_map else None


def get_analytics_summary(db: Session, time_window: str = "24h") -> AnalyticsSummary:
    """
    Computes summary KPI aggregates (min, max, avg, current) for all simulated indicators.
    """
    cutoff = _get_cutoff(time_window)

    readings_query = select(SensorReading)
    alerts_query = select(Alert)

    if cutoff:
        readings_query = readings_query.where(SensorReading.timestamp >= cutoff)
        alerts_query = alerts_query.where(Alert.created_at >= cutoff)

    # 1. Counts
    total_readings = db.scalar(
        select(func.count()).select_from(readings_query.subquery())
    ) or 0

    total_alerts = db.scalar(
        select(func.count()).select_from(alerts_query.subquery())
    ) or 0

    active_alerts = db.scalar(
        select(func.count()).select_from(Alert).where(Alert.status == "active")
    ) or 0

    # 2. Aggregates for numerical fields
    agg_stmt = select(
        func.avg(SensorReading.temperature_c).label("temp_avg"),
        func.min(SensorReading.temperature_c).label("temp_min"),
        func.max(SensorReading.temperature_c).label("temp_max"),
        func.avg(SensorReading.humidity_percent).label("hum_avg"),
        func.min(SensorReading.humidity_percent).label("hum_min"),
        func.max(SensorReading.humidity_percent).label("hum_max"),
        func.avg(SensorReading.gas_raw_value).label("gas_avg"),
        func.min(SensorReading.gas_raw_value).label("gas_min"),
        func.max(SensorReading.gas_raw_value).label("gas_max"),
        func.avg(SensorReading.pm25_ug_m3).label("pm25_avg"),
        func.min(SensorReading.pm25_ug_m3).label("pm25_min"),
        func.max(SensorReading.pm25_ug_m3).label("pm25_max"),
        func.avg(SensorReading.pm10_ug_m3).label("pm10_avg"),
        func.min(SensorReading.pm10_ug_m3).label("pm10_min"),
        func.max(SensorReading.pm10_ug_m3).label("pm10_max"),
    )
    if cutoff:
        agg_stmt = agg_stmt.where(SensorReading.timestamp >= cutoff)

    row = db.execute(agg_stmt).one_or_none()

    # 3. Latest reading for "current" values
    latest = get_latest_reading(db)
    latest_schema = ReadingResponse.model_validate(latest) if latest else None

    def _round(val: Optional[float], decimals: int = 2) -> Optional[float]:
        return round(val, decimals) if val is not None else None

    temp_summary = MetricSummary(
        avg=_round(row.temp_avg if row else None),
        min=_round(row.temp_min if row else None),
        max=_round(row.temp_max if row else None),
        current=_round(latest.temperature_c if latest else None),
    )
    hum_summary = MetricSummary(
        avg=_round(row.hum_avg if row else None),
        min=_round(row.hum_min if row else None),
        max=_round(row.hum_max if row else None),
        current=_round(latest.humidity_percent if latest else None),
    )
    gas_summary = MetricSummary(
        avg=_round(row.gas_avg if row else None),
        min=_round(row.gas_min if row else None),
        max=_round(row.gas_max if row else None),
        current=_round(latest.gas_raw_value if latest else None),
    )
    pm25_summary = MetricSummary(
        avg=_round(row.pm25_avg if row else None),
        min=_round(row.pm25_min if row else None),
        max=_round(row.pm25_max if row else None),
        current=_round(latest.pm25_ug_m3 if latest else None),
    )
    pm10_summary = MetricSummary(
        avg=_round(row.pm10_avg if row else None),
        min=_round(row.pm10_min if row else None),
        max=_round(row.pm10_max if row else None),
        current=_round(latest.pm10_ug_m3 if latest else None),
    )

    return AnalyticsSummary(
        time_window=time_window,
        total_readings=total_readings,
        active_alerts=active_alerts,
        total_alerts=total_alerts,
        temperature=temp_summary,
        humidity=hum_summary,
        gas_raw=gas_summary,
        pm25=pm25_summary,
        pm10=pm10_summary,
        latest_reading=latest_schema,
    )


def get_analytics_trends(
    db: Session,
    time_range: str = "1h",
    limit: int = 200,
) -> AnalyticsTrends:
    """
    Returns time-series points sorted chronologically for chart rendering.
    Fetches the most recent `limit` readings within the time_range window.
    """
    cutoff = _get_cutoff(time_range)

    query = select(SensorReading)
    if cutoff:
        query = query.where(SensorReading.timestamp >= cutoff)

    # Order by timestamp desc to get the most recent data points up to `limit`
    stmt = query.order_by(SensorReading.timestamp.desc()).limit(limit)
    rows = list(db.scalars(stmt).all())

    # Reverse so they are chronological (oldest to newest) for chart X-axis
    rows.reverse()

    points = [
        TrendPoint(
            timestamp=r.timestamp,
            temperature_c=r.temperature_c,
            humidity_percent=r.humidity_percent,
            gas_raw_value=r.gas_raw_value,
            pm25_ug_m3=r.pm25_ug_m3,
            pm10_ug_m3=r.pm10_ug_m3,
        )
        for r in rows
    ]

    return AnalyticsTrends(
        time_range=time_range,
        count=len(points),
        points=points,
    )
