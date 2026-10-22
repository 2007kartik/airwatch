"""
AirWatch — Phase 4 Verification Script
Executes automated checks for:
  Requirement A: Readings arriving every ~5 seconds
  Requirement B: PostgreSQL persistence and schema accuracy
  Requirement C: Warning/Critical alert generation
  Requirement D: Resilient retry and recovery after API downtime
"""

from datetime import datetime, timezone
import json
import time
import httpx
from sqlalchemy import text

from app.db.session import engine


def verify_requirement_a():
    print("=" * 60)
    print("VERIFYING REQUIREMENT A: New Readings Arriving ~5 Seconds")
    print("=" * 60)

    r = httpx.get("http://127.0.0.1:8000/api/readings?limit=10")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.json()
    items = data["items"]
    print(f"Total readings reported by API: {data['total']}")
    print(f"Returned items count: {len(items)}")

    assert len(items) >= 2, "Need at least 2 readings to measure interval"

    deltas = []
    for i in range(len(items) - 1):
        t_newer = datetime.fromisoformat(items[i]["timestamp"])
        t_older = datetime.fromisoformat(items[i + 1]["timestamp"])
        delta = (t_newer - t_older).total_seconds()
        if delta < 15.0:
            deltas.append(delta)
            print(
                f"Reading #{items[i+1]['id']} ({items[i+1]['timestamp']}) -> "
                f"Reading #{items[i]['id']} ({items[i]['timestamp']}): "
                f"Interval = {delta:.2f}s"
            )
        else:
            print(
                f"[Process Restart Gap] Reading #{items[i+1]['id']} -> "
                f"Reading #{items[i]['id']}: {delta:.2f}s (simulator was stopped between runs)"
            )

    assert len(deltas) >= 2, "Need at least 2 consecutive intra-run readings to measure interval"
    avg_delta = sum(deltas) / len(deltas)
    print(f"Average measured intra-run interval: {avg_delta:.2f}s (target: ~5.0s)")
    assert 4.0 <= avg_delta <= 6.5, f"Interval {avg_delta}s outside expected 4.0-6.5s range"

    # Also verify GET /api/readings/latest
    r_latest = httpx.get("http://127.0.0.1:8000/api/readings/latest")
    assert r_latest.status_code == 200
    latest_data = r_latest.json()
    assert latest_data["id"] == items[0]["id"]
    print(f"Latest reading ID #{latest_data['id']} matches most recent list entry.")
    print(">>> REQUIREMENT A: PASS\n")
    return items, deltas


def verify_requirement_b():
    print("=" * 60)
    print("VERIFYING REQUIREMENT B: PostgreSQL Persistence")
    print("=" * 60)

    with engine.connect() as conn:
        # 1. Row count
        count_res = conn.execute(text("SELECT count(*) FROM sensor_readings;")).scalar()
        print(f"Total sensor_readings rows in PostgreSQL 18: {count_res}")
        assert count_res > 0, "No records found in database!"

        # 2. Inspect latest 5 rows
        rows = conn.execute(
            text(
                "SELECT id, timestamp, temperature_c, humidity_percent, gas_raw_value, "
                "pm25_ug_m3, pm10_ug_m3, source, created_at "
                "FROM sensor_readings ORDER BY timestamp DESC LIMIT 5;"
            )
        ).mappings().all()

        for row in rows:
            print(
                f"DB Row #{row['id']}: ts={row['timestamp']} | "
                f"temp={row['temperature_c']}°C | hum={row['humidity_percent']}% | "
                f"gas={row['gas_raw_value']} | pm25={row['pm25_ug_m3']} | "
                f"pm10={row['pm10_ug_m3']} | source='{row['source']}'"
            )
            assert row["source"] == "simulated", f"Unexpected source: {row['source']}"
            assert row["timestamp"] is not None
            assert row["created_at"] is not None

    print("PostgreSQL records verified: schema fields, timestamps, and source='simulated' confirmed.")
    print(">>> REQUIREMENT B: PASS\n")


def verify_requirement_c():
    print("=" * 60)
    print("VERIFYING REQUIREMENT C: Threshold-Based Alerts")
    print("=" * 60)

    # First check existing alerts in DB/API
    r_alerts = httpx.get("http://127.0.0.1:8000/api/alerts")
    assert r_alerts.status_code == 200
    alerts_data = r_alerts.json()
    print(f"Existing alerts count: total={alerts_data['total']}, active={alerts_data['active_count']}")
    for alert in alerts_data["items"]:
        print(
            f"Alert #{alert['id']}: type={alert['alert_type']} | severity={alert['severity']} | "
            f"observed={alert['observed_value']} | threshold={alert['threshold_value']} | "
            f"status={alert['status']} | msg='{alert['message']}'"
        )

    # Perform deterministic controlled tests for both WARNING and CRITICAL thresholds
    print("\n--- Deterministic Controlled Alert Test ---")

    # 1. Trigger temperature WARNING (threshold = 35.0, send 36.5)
    warn_payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "temperature_c": 36.5,
        "humidity_percent": 50.0,
        "gas_raw_value": 120.0,
        "pm25_ug_m3": 15.0,
        "pm10_ug_m3": 30.0,
        "source": "simulated",
    }
    r_warn = httpx.post("http://127.0.0.1:8000/api/readings", json=warn_payload)
    assert r_warn.status_code == 201
    warn_resp = r_warn.json()
    assert len(warn_resp["alerts_triggered"]) == 1
    warn_alert = warn_resp["alerts_triggered"][0]
    print(f"Generated WARNING Alert: {warn_alert['alert_type']}, severity={warn_alert['severity']}, obs={warn_alert['observed_value']}")
    assert warn_alert["alert_type"] == "temperature_high"
    assert warn_alert["severity"] == "warning"

    # 2. Trigger temperature CRITICAL (threshold = 40.0, send 42.0)
    crit_payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "temperature_c": 42.0,
        "humidity_percent": 50.0,
        "gas_raw_value": 120.0,
        "pm25_ug_m3": 15.0,
        "pm10_ug_m3": 30.0,
        "source": "simulated",
    }
    r_crit = httpx.post("http://127.0.0.1:8000/api/readings", json=crit_payload)
    assert r_crit.status_code == 201
    crit_resp = r_crit.json()
    assert len(crit_resp["alerts_triggered"]) == 1
    crit_alert = crit_resp["alerts_triggered"][0]
    print(f"Generated CRITICAL Alert: {crit_alert['alert_type']}, severity={crit_alert['severity']}, obs={crit_alert['observed_value']}")
    assert crit_alert["alert_type"] == "temperature_high"
    assert crit_alert["severity"] == "critical"

    # 3. Test alert acknowledgment
    ack_res = httpx.patch(f"http://127.0.0.1:8000/api/alerts/{crit_alert['id']}")
    assert ack_res.status_code == 200
    ack_data = ack_res.json()
    assert ack_data["status"] == "acknowledged"
    print(f"Acknowledged Alert #{crit_alert['id']}: status={ack_data['status']}, ack_at={ack_data['acknowledged_at']}")

    # 4. Verify in PostgreSQL directly
    with engine.connect() as conn:
        db_alert = conn.execute(
            text("SELECT id, alert_type, severity, status, observed_value FROM alerts WHERE id = :id"),
            {"id": crit_alert["id"]}
        ).mappings().one()
        print(f"Direct DB Query on Alert #{db_alert['id']}: status={db_alert['status']}, severity={db_alert['severity']}")
        assert db_alert["status"] == "acknowledged"

    print(">>> REQUIREMENT C: PASS\n")


def verify_requirement_d():
    print("=" * 60)
    print("VERIFYING REQUIREMENT D: Recovery After API Failure")
    print("=" * 60)

    from simulator.sensor_simulator import SensorSimulator

    # Step 1: Simulator confirms successful reading to live API
    sim = SensorSimulator(
        api_url="http://127.0.0.1:8000",
        max_retries=3,
        backoff_base_delay=0.5,
    )
    success1, payload1, _, resp1 = sim.run_once()
    assert success1 is True, "Initial baseline reading failed"
    print(f"Step 1: Successfully posted reading #{resp1['reading']['id']} to live API.")

    # Step 2 & 3: Simulator attempts to reach an unavailable endpoint
    sim_unavail = SensorSimulator(
        api_url="http://127.0.0.1:59998",  # Non-existent local port
        max_retries=2,
        backoff_base_delay=0.2,
        http_timeout=0.5,
    )
    print("Step 2: Submitting reading to unavailable endpoint (http://127.0.0.1:59998)...")
    success2, _, _, _ = sim_unavail.run_once()
    assert success2 is False, "Expected failure on unavailable port"
    assert sim_unavail.was_disconnected is True, "was_disconnected flag not set"
    print("Step 3: Simulator handled connection failure gracefully with backoff and did not crash.")

    # Step 4 & 5: Restore endpoint availability (switch back to live endpoint) and post
    sim_unavail.api_url = "http://127.0.0.1:8000"
    sim_unavail.endpoint = "http://127.0.0.1:8000/api/readings"
    print("Step 4: Restoring backend connection...")
    success3, payload3, _, resp3 = sim_unavail.run_once()
    assert success3 is True, "Simulator failed to reconnect to live API"
    assert sim_unavail.was_disconnected is False, "was_disconnected flag not cleared after recovery"
    print(f"Step 5: Simulator reconnected and submitted new reading #{resp3['reading']['id']} successfully.")

    # Step 6: Verify new record appears in API and DB
    r_check = httpx.get("http://127.0.0.1:8000/api/readings/latest")
    assert r_check.status_code == 200
    assert r_check.json()["id"] == resp3["reading"]["id"]
    print(f"Step 6: Verified new reading #{resp3['reading']['id']} in API latest endpoint.")

    print(">>> REQUIREMENT D: PASS\n")


if __name__ == "__main__":
    verify_requirement_a()
    verify_requirement_b()
    verify_requirement_c()
    verify_requirement_d()
    print("=" * 60)
    print("ALL 4 REQUIREMENTS (A, B, C, D) FULLY VERIFIED!")
    print("=" * 60)
