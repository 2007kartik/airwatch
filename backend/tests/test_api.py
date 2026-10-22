"""
AirWatch — End-to-End API Integration Tests
Tests all endpoints using FastAPI TestClient with isolated in-memory DB.
"""

from datetime import datetime, timezone
from fastapi.testclient import TestClient


def test_health_endpoint(client: TestClient):
    """GET /api/health returns status, environment, and database state."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "environment" in data
    assert "database" in data
    assert "timestamp" in data
    assert "SIMULATED" in data["data_notice"]


def test_root_endpoint(client: TestClient):
    """GET / returns system notice."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "AirWatch" in data["message"]
    assert "SIMULATED" in data["data_notice"]


def test_post_reading_success_no_alerts(client: TestClient):
    """POST /api/readings with normal data creates record and triggers 0 alerts."""
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "temperature_c": 22.5,
        "humidity_percent": 50.0,
        "gas_raw_value": 110.0,
        "pm25_ug_m3": 12.0,
        "pm10_ug_m3": 25.0,
        "source": "simulated",
    }
    response = client.post("/api/readings", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["reading"]["temperature_c"] == 22.5
    assert data["reading"]["humidity_percent"] == 50.0
    assert len(data["alerts_triggered"]) == 0


def test_post_reading_triggers_alert(client: TestClient):
    """POST /api/readings with critical temperature triggers critical alert."""
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "temperature_c": 43.0,  # Exceeds critical (40.0)
        "humidity_percent": 50.0,
    }
    response = client.post("/api/readings", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert len(data["alerts_triggered"]) == 1
    alert = data["alerts_triggered"][0]
    assert alert["alert_type"] == "temperature_high"
    assert alert["severity"] == "critical"
    assert alert["status"] == "active"


def test_post_reading_invalid_payload_returns_422(client: TestClient):
    """POST /api/readings with out-of-range humidity returns 422."""
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "temperature_c": 25.0,
        "humidity_percent": 150.0,  # Invalid (>100)
    }
    response = client.post("/api/readings", json=payload)
    assert response.status_code == 422


def test_get_latest_reading_empty_and_populated(client: TestClient):
    """GET /api/readings/latest returns 404 when empty, 200 when populated."""
    # When empty
    response = client.get("/api/readings/latest")
    assert response.status_code == 404

    # Ingest a reading
    client.post("/api/readings", json={
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "temperature_c": 26.0,
        "humidity_percent": 55.0,
    })

    # Now latest returns 200
    response = client.get("/api/readings/latest")
    assert response.status_code == 200
    assert response.json()["temperature_c"] == 26.0


def test_get_readings_pagination(client: TestClient):
    """GET /api/readings supports limit and offset."""
    for i in range(5):
        client.post("/api/readings", json={
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "temperature_c": 20.0 + i,
            "humidity_percent": 50.0,
        })

    response = client.get("/api/readings?limit=2&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["items"]) == 2
    assert data["limit"] == 2
    assert data["offset"] == 0


def test_alerts_list_and_acknowledge(client: TestClient):
    """Test GET /api/alerts and PATCH /api/alerts/{id}."""
    # Trigger an alert via POST reading
    client.post("/api/readings", json={
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "temperature_c": 42.0,
        "humidity_percent": 50.0,
    })

    # List alerts
    res = client.get("/api/alerts")
    assert res.status_code == 200
    alerts_data = res.json()
    assert alerts_data["total"] == 1
    assert alerts_data["active_count"] == 1
    assert alerts_data["acknowledged_count"] == 0

    alert_id = alerts_data["items"][0]["id"]

    # Acknowledge the alert
    ack_res = client.patch(f"/api/alerts/{alert_id}")
    assert ack_res.status_code == 200
    assert ack_res.json()["status"] == "acknowledged"

    # Verify counts updated
    res2 = client.get("/api/alerts")
    assert res2.json()["active_count"] == 0
    assert res2.json()["acknowledged_count"] == 1


def test_acknowledge_nonexistent_alert_returns_404(client: TestClient):
    """PATCH /api/alerts/{invalid_id} returns 404."""
    response = client.patch("/api/alerts/999999")
    assert response.status_code == 404


def test_analytics_summary_and_trends(client: TestClient):
    """Test GET /api/analytics/summary and GET /api/analytics/trends."""
    for temp in [20.0, 25.0, 30.0]:
        client.post("/api/readings", json={
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "temperature_c": temp,
            "humidity_percent": 50.0,
            "gas_raw_value": 150.0,
            "pm25_ug_m3": 20.0,
            "pm10_ug_m3": 40.0,
        })

    # Summary
    res = client.get("/api/analytics/summary?range=24h")
    assert res.status_code == 200
    summary = res.json()
    assert summary["total_readings"] == 3
    assert summary["temperature"]["min"] == 20.0
    assert summary["temperature"]["max"] == 30.0
    assert summary["temperature"]["avg"] == 25.0
    assert summary["temperature"]["current"] == 30.0
    assert "SIMULATED" in summary["data_notice"]

    # Trends
    trend_res = client.get("/api/analytics/trends?range=1h")
    assert trend_res.status_code == 200
    trends = trend_res.json()
    assert trends["count"] == 3
    assert len(trends["points"]) == 3
    assert trends["points"][0]["temperature_c"] == 20.0
    assert trends["points"][-1]["temperature_c"] == 30.0
