"""
AirWatch — Alert Service Tests
Tests threshold evaluation rules, severity assignment, duplicate prevention,
and alert acknowledgement workflows.
"""

from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.sensor_reading import SensorReading
from app.services.alert_service import (
    acknowledge_alert,
    evaluate_reading_thresholds,
    get_alerts,
)


def _create_test_reading(
    db: Session,
    temperature_c: float = 24.0,
    humidity_percent: float = 50.0,
    gas_raw_value: float = 100.0,
    pm25_ug_m3: float = 12.0,
    pm10_ug_m3: float = 25.0,
) -> SensorReading:
    reading = SensorReading(
        timestamp=datetime.now(timezone.utc),
        temperature_c=temperature_c,
        humidity_percent=humidity_percent,
        gas_raw_value=gas_raw_value,
        pm25_ug_m3=pm25_ug_m3,
        pm10_ug_m3=pm10_ug_m3,
        source="simulated",
    )
    db.add(reading)
    db.commit()
    db.refresh(reading)
    return reading


def test_normal_reading_generates_no_alerts(db_session: Session):
    """A reading with all values within normal limits triggers no alerts."""
    reading = _create_test_reading(
        db_session,
        temperature_c=22.0,
        humidity_percent=45.0,
        gas_raw_value=120.0,
        pm25_ug_m3=10.0,
        pm10_ug_m3=20.0,
    )
    alerts = evaluate_reading_thresholds(db_session, reading)
    assert len(alerts) == 0


def test_temperature_warning_alert(db_session: Session):
    """Temperature between warning (35°C) and critical (40°C) triggers warning alert."""
    reading = _create_test_reading(db_session, temperature_c=36.5)
    alerts = evaluate_reading_thresholds(db_session, reading)
    assert len(alerts) == 1
    assert alerts[0].alert_type == "temperature_high"
    assert alerts[0].severity == "warning"
    assert alerts[0].status == "active"
    assert alerts[0].observed_value == 36.5


def test_temperature_critical_alert(db_session: Session):
    """Temperature >= 40°C triggers critical alert."""
    reading = _create_test_reading(db_session, temperature_c=42.0)
    alerts = evaluate_reading_thresholds(db_session, reading)
    assert len(alerts) == 1
    assert alerts[0].alert_type == "temperature_high"
    assert alerts[0].severity == "critical"
    assert alerts[0].observed_value == 42.0


def test_humidity_warning_and_critical(db_session: Session):
    """Humidity warning (>=80%) and critical (>=90%) thresholds."""
    r_warn = _create_test_reading(db_session, humidity_percent=85.0)
    alerts_warn = evaluate_reading_thresholds(db_session, r_warn)
    assert len(alerts_warn) == 1
    assert alerts_warn[0].alert_type == "humidity_high"
    assert alerts_warn[0].severity == "warning"

    r_crit = _create_test_reading(db_session, humidity_percent=95.0)
    alerts_crit = evaluate_reading_thresholds(db_session, r_crit)
    assert len(alerts_crit) == 1
    assert alerts_crit[0].alert_type == "humidity_high"
    assert alerts_crit[0].severity == "critical"


def test_multiple_thresholds_triggered_simultaneously(db_session: Session):
    """Reading exceeding multiple thresholds creates multiple distinct alerts."""
    reading = _create_test_reading(
        db_session,
        temperature_c=41.0,    # Critical temp
        humidity_percent=88.0,  # Warning humidity
        pm25_ug_m3=60.0,        # Critical PM2.5
    )
    alerts = evaluate_reading_thresholds(db_session, reading)
    assert len(alerts) == 3

    types = {a.alert_type: a.severity for a in alerts}
    assert types["temperature_high"] == "critical"
    assert types["humidity_high"] == "warning"
    assert types["pm25_high"] == "critical"


def test_no_duplicate_alerts_for_same_reading_and_rule(db_session: Session):
    """Evaluating thresholds twice on the same reading does not duplicate alerts."""
    reading = _create_test_reading(db_session, temperature_c=38.0)
    alerts_first = evaluate_reading_thresholds(db_session, reading)
    db_session.commit()
    assert len(alerts_first) == 1

    alerts_second = evaluate_reading_thresholds(db_session, reading)
    db_session.commit()
    assert len(alerts_second) == 0


def test_acknowledge_alert(db_session: Session):
    """Acknowledge alert updates status and records timestamp."""
    reading = _create_test_reading(db_session, temperature_c=42.0)
    alerts = evaluate_reading_thresholds(db_session, reading)
    db_session.commit()
    alert_id = alerts[0].id

    acknowledged = acknowledge_alert(db_session, alert_id)
    assert acknowledged is not None
    assert acknowledged.status == "acknowledged"
    assert acknowledged.acknowledged_at is not None


def test_acknowledge_nonexistent_alert(db_session: Session):
    """Acknowledging non-existent alert returns None."""
    result = acknowledge_alert(db_session, 99999)
    assert result is None


def test_get_alerts_filtering_and_counts(db_session: Session):
    """Test get_alerts filtering by status and metadata counts."""
    # Create 2 readings that trigger alerts
    r1 = _create_test_reading(db_session, temperature_c=36.0)
    r2 = _create_test_reading(db_session, humidity_percent=92.0)
    evaluate_reading_thresholds(db_session, r1)
    evaluate_reading_thresholds(db_session, r2)
    db_session.commit()

    items, total, active_count, acknowledged_count = get_alerts(db_session)
    assert total == 2
    assert active_count == 2
    assert acknowledged_count == 0

    # Acknowledge first alert
    acknowledge_alert(db_session, items[0].id)

    # Check active filter
    active_items, active_tot, active_c, ack_c = get_alerts(db_session, status="active")
    assert len(active_items) == 1
    assert active_tot == 1
    assert active_c == 1
    assert ack_c == 1
