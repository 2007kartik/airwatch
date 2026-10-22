"""
AirWatch — Reading Service
Handles creation, retrieval, and time-range queries for sensor readings.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.models.sensor_reading import SensorReading
from app.schemas.reading import ReadingCreate
from app.services.alert_service import evaluate_reading_thresholds

logger = logging.getLogger("airwatch.services.reading")


def create_reading(
    db: Session,
    reading_in: ReadingCreate,
) -> tuple[SensorReading, list[Alert]]:
    """
    Persists a new sensor reading in the database and evaluates alert thresholds.
    Both the reading and any generated alerts are saved in the same transaction.
    """
    # Ensure timestamp is UTC
    ts = reading_in.timestamp
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    else:
        ts = ts.astimezone(timezone.utc)

    reading = SensorReading(
        timestamp=ts,
        temperature_c=reading_in.temperature_c,
        humidity_percent=reading_in.humidity_percent,
        gas_raw_value=reading_in.gas_raw_value,
        pm25_ug_m3=reading_in.pm25_ug_m3,
        pm10_ug_m3=reading_in.pm10_ug_m3,
        source=reading_in.source,
    )

    db.add(reading)
    db.flush()  # Populates reading.id for foreign key in alerts

    # Threshold evaluation
    alerts = evaluate_reading_thresholds(db, reading)

    db.commit()
    db.refresh(reading)
    for alert in alerts:
        db.refresh(alert)

    logger.debug("Ingested reading id=%d, created %d alerts", reading.id, len(alerts))
    return reading, alerts


def get_latest_reading(db: Session) -> Optional[SensorReading]:
    """
    Returns the most recent sensor reading by timestamp.
    """
    stmt = (
        select(SensorReading)
        .order_by(desc(SensorReading.timestamp))
        .limit(1)
    )
    return db.scalars(stmt).first()


def get_readings(
    db: Session,
    limit: int = 50,
    offset: int = 0,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
) -> tuple[list[SensorReading], int]:
    """
    Fetch paginated readings, optionally filtered by timestamp window [start, end].
    Returns (items, total_count).
    """
    query = select(SensorReading)

    if start:
        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)
        query = query.where(SensorReading.timestamp >= start)

    if end:
        if end.tzinfo is None:
            end = end.replace(tzinfo=timezone.utc)
        query = query.where(SensorReading.timestamp <= end)

    # Count total matching query
    count_stmt = select(func.count()).select_from(query.subquery())
    total = db.scalar(count_stmt) or 0

    # Paginated rows ordered by newest first
    stmt = (
        query.order_by(desc(SensorReading.timestamp))
        .limit(limit)
        .offset(offset)
    )
    items = list(db.scalars(stmt).all())

    return items, total
