"""
AirWatch — Schema Validation Tests
Tests Pydantic validation rules, constraints, and timezone handling.
"""

from datetime import datetime, timezone
import pytest
from pydantic import ValidationError

from app.schemas.reading import ReadingCreate, ReadingResponse
from app.schemas.alert import AlertResponse
from app.schemas.analytics import MetricSummary, AnalyticsSummary


def test_reading_create_valid():
    """Verify that a valid reading payload creates a ReadingCreate instance."""
    payload = {
        "timestamp": "2026-10-19T10:00:00Z",
        "temperature_c": 24.5,
        "humidity_percent": 55.0,
        "gas_raw_value": 120.0,
        "pm25_ug_m3": 15.2,
        "pm10_ug_m3": 35.0,
        "source": "simulated",
    }
    reading = ReadingCreate(**payload)
    assert reading.temperature_c == 24.5
    assert reading.humidity_percent == 55.0
    assert reading.gas_raw_value == 120.0
    assert reading.pm25_ug_m3 == 15.2
    assert reading.pm10_ug_m3 == 35.0
    assert reading.source == "simulated"
    assert reading.timestamp.tzinfo is not None


def test_reading_create_naive_timestamp_converted_to_utc():
    """Verify naive datetimes are automatically assigned UTC."""
    payload = {
        "timestamp": datetime(2026, 10, 19, 10, 0, 0),
        "temperature_c": 20.0,
        "humidity_percent": 50.0,
    }
    reading = ReadingCreate(**payload)
    assert reading.timestamp.tzinfo == timezone.utc


def test_reading_create_humidity_out_of_bounds():
    """Verify humidity < 0 or > 100 raises ValidationError."""
    with pytest.raises(ValidationError):
        ReadingCreate(
            timestamp=datetime.now(timezone.utc),
            temperature_c=25.0,
            humidity_percent=105.0,
        )

    with pytest.raises(ValidationError):
        ReadingCreate(
            timestamp=datetime.now(timezone.utc),
            temperature_c=25.0,
            humidity_percent=-5.0,
        )


def test_reading_create_temperature_out_of_bounds():
    """Verify temperature < -50 or > 100 raises ValidationError."""
    with pytest.raises(ValidationError):
        ReadingCreate(
            timestamp=datetime.now(timezone.utc),
            temperature_c=-60.0,
            humidity_percent=50.0,
        )

    with pytest.raises(ValidationError):
        ReadingCreate(
            timestamp=datetime.now(timezone.utc),
            temperature_c=120.0,
            humidity_percent=50.0,
        )


def test_reading_create_missing_required_fields():
    """Verify missing required fields (temperature or humidity) raises ValidationError."""
    with pytest.raises(ValidationError):
        ReadingCreate(
            timestamp=datetime.now(timezone.utc),
            # missing temperature_c and humidity_percent
        )


def test_alert_response_serialization():
    """Verify AlertResponse correctly parses model attributes."""
    alert_data = {
        "id": 1,
        "reading_id": 42,
        "alert_type": "temperature_high",
        "severity": "critical",
        "message": "Critical temperature detected: 42.0°C",
        "observed_value": 42.0,
        "threshold_value": 40.0,
        "status": "active",
        "created_at": datetime.now(timezone.utc),
        "acknowledged_at": None,
    }
    alert = AlertResponse(**alert_data)
    assert alert.id == 1
    assert alert.alert_type == "temperature_high"
    assert alert.severity == "critical"
    assert alert.status == "active"


def test_analytics_summary_structure():
    """Verify AnalyticsSummary schema requirements."""
    summary = AnalyticsSummary(
        time_window="24h",
        total_readings=100,
        active_alerts=2,
        total_alerts=5,
        temperature=MetricSummary(avg=25.0, min=20.0, max=30.0, current=26.0),
        humidity=MetricSummary(avg=50.0, min=40.0, max=60.0, current=52.0),
        gas_raw=MetricSummary(avg=150.0, min=100.0, max=200.0, current=140.0),
        pm25=MetricSummary(avg=20.0, min=10.0, max=40.0, current=22.0),
        pm10=MetricSummary(avg=45.0, min=25.0, max=75.0, current=50.0),
    )
    assert summary.total_readings == 100
    assert summary.active_alerts == 2
    assert summary.temperature.avg == 25.0
    assert "SIMULATED" in summary.data_notice
