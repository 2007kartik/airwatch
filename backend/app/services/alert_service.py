"""
AirWatch — Alert Service
Implements rule-based threshold evaluation and alert lifecycle management.
All thresholds are demo / configurable thresholds loaded from core.config.settings.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.alert import Alert
from app.models.sensor_reading import SensorReading

logger = logging.getLogger("airwatch.services.alert")


def evaluate_reading_thresholds(db: Session, reading: SensorReading) -> list[Alert]:
    """
    Evaluates configured thresholds against a SensorReading.
    Creates and attaches Alert records for any violated rules.
    Prevents duplicate alerts for the same reading and alert_type.
    """
    triggered_rules: list[dict] = []

    # 1. Temperature Check
    if reading.temperature_c >= settings.threshold_temp_critical:
        triggered_rules.append({
            "alert_type": "temperature_high",
            "severity": "critical",
            "message": (
                f"Critical temperature: {reading.temperature_c:.1f}°C "
                f"exceeds critical threshold ({settings.threshold_temp_critical:.1f}°C)"
            ),
            "observed_value": reading.temperature_c,
            "threshold_value": settings.threshold_temp_critical,
        })
    elif reading.temperature_c >= settings.threshold_temp_warning:
        triggered_rules.append({
            "alert_type": "temperature_high",
            "severity": "warning",
            "message": (
                f"High temperature: {reading.temperature_c:.1f}°C "
                f"exceeds warning threshold ({settings.threshold_temp_warning:.1f}°C)"
            ),
            "observed_value": reading.temperature_c,
            "threshold_value": settings.threshold_temp_warning,
        })

    # 2. Humidity Check
    if reading.humidity_percent >= settings.threshold_humidity_critical:
        triggered_rules.append({
            "alert_type": "humidity_high",
            "severity": "critical",
            "message": (
                f"Critical humidity: {reading.humidity_percent:.1f}% "
                f"exceeds critical threshold ({settings.threshold_humidity_critical:.1f}%)"
            ),
            "observed_value": reading.humidity_percent,
            "threshold_value": settings.threshold_humidity_critical,
        })
    elif reading.humidity_percent >= settings.threshold_humidity_warning:
        triggered_rules.append({
            "alert_type": "humidity_high",
            "severity": "warning",
            "message": (
                f"High humidity: {reading.humidity_percent:.1f}% "
                f"exceeds warning threshold ({settings.threshold_humidity_warning:.1f}%)"
            ),
            "observed_value": reading.humidity_percent,
            "threshold_value": settings.threshold_humidity_warning,
        })

    # 3. Gas Raw Value Check (optional simulated indicator)
    if reading.gas_raw_value is not None:
        if reading.gas_raw_value >= settings.threshold_gas_critical:
            triggered_rules.append({
                "alert_type": "gas_high",
                "severity": "critical",
                "message": (
                    f"Critical gas level: raw value {reading.gas_raw_value:.1f} "
                    f"exceeds critical threshold ({settings.threshold_gas_critical:.1f})"
                ),
                "observed_value": reading.gas_raw_value,
                "threshold_value": settings.threshold_gas_critical,
            })
        elif reading.gas_raw_value >= settings.threshold_gas_warning:
            triggered_rules.append({
                "alert_type": "gas_high",
                "severity": "warning",
                "message": (
                    f"Elevated gas level: raw value {reading.gas_raw_value:.1f} "
                    f"exceeds warning threshold ({settings.threshold_gas_warning:.1f})"
                ),
                "observed_value": reading.gas_raw_value,
                "threshold_value": settings.threshold_gas_warning,
            })

    # 4. PM2.5 Check (simulated/illustrative indicator)
    if reading.pm25_ug_m3 is not None:
        if reading.pm25_ug_m3 >= settings.threshold_pm25_critical:
            triggered_rules.append({
                "alert_type": "pm25_high",
                "severity": "critical",
                "message": (
                    f"Simulated PM2.5 critical: {reading.pm25_ug_m3:.1f} µg/m³ "
                    f"exceeds critical threshold ({settings.threshold_pm25_critical:.1f} µg/m³)"
                ),
                "observed_value": reading.pm25_ug_m3,
                "threshold_value": settings.threshold_pm25_critical,
            })
        elif reading.pm25_ug_m3 >= settings.threshold_pm25_warning:
            triggered_rules.append({
                "alert_type": "pm25_high",
                "severity": "warning",
                "message": (
                    f"Simulated PM2.5 elevated: {reading.pm25_ug_m3:.1f} µg/m³ "
                    f"exceeds warning threshold ({settings.threshold_pm25_warning:.1f} µg/m³)"
                ),
                "observed_value": reading.pm25_ug_m3,
                "threshold_value": settings.threshold_pm25_warning,
            })

    # 5. PM10 Check (simulated/illustrative indicator)
    if reading.pm10_ug_m3 is not None:
        if reading.pm10_ug_m3 >= settings.threshold_pm10_critical:
            triggered_rules.append({
                "alert_type": "pm10_high",
                "severity": "critical",
                "message": (
                    f"Simulated PM10 critical: {reading.pm10_ug_m3:.1f} µg/m³ "
                    f"exceeds critical threshold ({settings.threshold_pm10_critical:.1f} µg/m³)"
                ),
                "observed_value": reading.pm10_ug_m3,
                "threshold_value": settings.threshold_pm10_critical,
            })
        elif reading.pm10_ug_m3 >= settings.threshold_pm10_warning:
            triggered_rules.append({
                "alert_type": "pm10_high",
                "severity": "warning",
                "message": (
                    f"Simulated PM10 elevated: {reading.pm10_ug_m3:.1f} µg/m³ "
                    f"exceeds warning threshold ({settings.threshold_pm10_warning:.1f} µg/m³)"
                ),
                "observed_value": reading.pm10_ug_m3,
                "threshold_value": settings.threshold_pm10_warning,
            })

    created_alerts: list[Alert] = []
    for rule in triggered_rules:
        # Check for existing alert for this reading and alert_type to avoid duplicates
        existing = db.execute(
            select(Alert).where(
                Alert.reading_id == reading.id,
                Alert.alert_type == rule["alert_type"],
            )
        ).scalar_one_or_none()

        if not existing:
            alert = Alert(
                reading_id=reading.id,
                alert_type=rule["alert_type"],
                severity=rule["severity"],
                message=rule["message"],
                observed_value=rule["observed_value"],
                threshold_value=rule["threshold_value"],
                status="active",
                created_at=datetime.now(timezone.utc),
            )
            db.add(alert)
            created_alerts.append(alert)
            logger.info(
                "Triggered alert: %s (%s) for reading_id=%d",
                rule["alert_type"],
                rule["severity"],
                reading.id,
            )

    return created_alerts


def acknowledge_alert(db: Session, alert_id: int) -> Optional[Alert]:
    """
    Marks an active alert as acknowledged with the current UTC timestamp.
    Returns the updated Alert or None if not found.
    """
    alert = db.execute(select(Alert).where(Alert.id == alert_id)).scalar_one_or_none()
    if not alert:
        return None

    if alert.status != "acknowledged":
        alert.status = "acknowledged"
        alert.acknowledged_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(alert)
        logger.info("Alert id=%d acknowledged", alert_id)
    return alert


def get_alerts(
    db: Session,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[Alert], int, int, int]:
    """
    Fetch paginated alerts with optional status and severity filters.
    Returns: (alerts, total_filtered, total_active, total_acknowledged)
    """
    base_query = select(Alert)
    if status:
        base_query = base_query.where(Alert.status == status)
    if severity:
        base_query = base_query.where(Alert.severity == severity)

    # Total matching current filter
    total = db.scalar(select(func.count()).select_from(base_query.subquery())) or 0

    # Total active overall
    active_count = db.scalar(
        select(func.count()).select_from(Alert).where(Alert.status == "active")
    ) or 0

    # Total acknowledged overall
    acknowledged_count = db.scalar(
        select(func.count()).select_from(Alert).where(Alert.status == "acknowledged")
    ) or 0

    # Paginated results ordered by creation timestamp descending
    query = (
        base_query.order_by(desc(Alert.created_at))
        .limit(limit)
        .offset(offset)
    )
    items = list(db.scalars(query).all())

    return items, total, active_count, acknowledged_count
