"""
AirWatch — Sensor Simulator Tests
Tests data generation, drift bounds, spike triggering, and retry logic.
"""

from unittest.mock import MagicMock, patch
import httpx
import pytest

from simulator.sensor_simulator import SensorDataGenerator, SensorSimulator


def test_generator_fields_and_source():
    """Verify generated reading payload contains all expected keys and source='simulated'."""
    generator = SensorDataGenerator(spike_probability=0.0)
    payload, spike = generator.generate_reading()

    assert payload["source"] == "simulated"
    assert "timestamp" in payload
    assert isinstance(payload["temperature_c"], float)
    assert isinstance(payload["humidity_percent"], float)
    assert isinstance(payload["gas_raw_value"], float)
    assert isinstance(payload["pm25_ug_m3"], float)
    assert isinstance(payload["pm10_ug_m3"], float)
    assert spike is None


def test_generator_drift_bounds():
    """Verify drift over 50 iterations stays within plausible baseline bounds when spike_probability=0."""
    generator = SensorDataGenerator(spike_probability=0.0)
    for _ in range(50):
        payload, _ = generator.generate_reading()
        assert 16.0 <= payload["temperature_c"] <= 34.0
        assert 30.0 <= payload["humidity_percent"] <= 75.0
        assert 60.0 <= payload["gas_raw_value"] <= 250.0
        assert 5.0 <= payload["pm25_ug_m3"] <= 30.0
        assert 10.0 <= payload["pm10_ug_m3"] <= 65.0


def test_generator_force_temperature_warning_spike():
    """Verify forcing a warning temperature spike produces temp in warning threshold range (>= 35°C)."""
    generator = SensorDataGenerator()
    payload, spike = generator.generate_reading(force_spike="temp", force_severity="warning")
    assert payload["temperature_c"] >= 35.0
    assert payload["temperature_c"] < 40.0
    assert spike is not None
    assert "WARNING" in spike


def test_generator_force_temperature_critical_spike():
    """Verify forcing a critical temperature spike produces temp in critical threshold range (>= 40°C)."""
    generator = SensorDataGenerator()
    payload, spike = generator.generate_reading(force_spike="temp", force_severity="critical")
    assert payload["temperature_c"] >= 40.0
    assert spike is not None
    assert "CRITICAL" in spike


def test_generator_force_humidity_critical_spike():
    """Verify forcing a critical humidity spike produces humidity >= 90%."""
    generator = SensorDataGenerator()
    payload, spike = generator.generate_reading(force_spike="humidity", force_severity="critical")
    assert payload["humidity_percent"] >= 90.0
    assert "CRITICAL" in spike


def test_generator_force_pm25_critical_spike():
    """Verify forcing a critical PM2.5 spike produces PM2.5 >= 55.4 µg/m³."""
    generator = SensorDataGenerator()
    payload, spike = generator.generate_reading(force_spike="pm25", force_severity="critical")
    assert payload["pm25_ug_m3"] >= 55.4
    assert "CRITICAL" in spike


def test_simulator_retry_and_backoff_on_connection_error():
    """Verify simulator retries upon network error and reports failure without raising exception."""
    simulator = SensorSimulator(
        api_url="http://127.0.0.1:59999",  # Non-existent port
        max_retries=2,
        backoff_base_delay=0.01,  # Fast backoff for tests
        http_timeout=0.2,
    )

    success, resp = simulator.post_reading_with_retry({
        "timestamp": "2026-10-19T10:00:00Z",
        "temperature_c": 22.0,
        "humidity_percent": 50.0,
        "source": "simulated",
    })

    assert success is False
    assert resp is None
    assert simulator.total_failed == 1
    assert simulator.was_disconnected is True


def test_simulator_successful_post():
    """Verify simulator handles 201 response successfully."""
    simulator = SensorSimulator(max_retries=1)

    mock_resp = MagicMock()
    mock_resp.status_code = 201
    mock_resp.json.return_value = {
        "reading": {"id": 1, "temperature_c": 24.0},
        "alerts_triggered": [],
    }

    with patch("httpx.Client.post", return_value=mock_resp):
        success, resp = simulator.post_reading_with_retry({
            "timestamp": "2026-10-19T10:00:00Z",
            "temperature_c": 24.0,
            "humidity_percent": 50.0,
            "source": "simulated",
        })

    assert success is True
    assert resp["reading"]["id"] == 1
    assert simulator.total_sent == 1
    assert simulator.was_disconnected is False
