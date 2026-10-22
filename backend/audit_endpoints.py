"""
AirWatch — Comprehensive API Endpoints Audit Script
Tests all 9 endpoints against the live running server (http://127.0.0.1:8000).
"""

from datetime import datetime, timezone
import json
import httpx

BASE_URL = "http://127.0.0.1:8000"


def audit_api():
    print("=" * 70)
    print("AUDITING ALL FASTAPI BACKEND ENDPOINTS")
    print("=" * 70)

    with httpx.Client(base_url=BASE_URL, timeout=10.0) as client:
        # 1. GET /
        res_root = client.get("/")
        print(f"1. GET / -> Status: {res_root.status_code}")
        assert res_root.status_code == 200
        root_data = res_root.json()
        assert "message" in root_data and "SIMULATED" in root_data["data_notice"]
        print(f"   Response: {root_data}")

        # 2. GET /api/health
        res_health = client.get("/api/health")
        print(f"\n2. GET /api/health -> Status: {res_health.status_code}")
        assert res_health.status_code == 200
        health_data = res_health.json()
        assert health_data["status"] == "ok"
        assert health_data["database"] == "connected"
        assert "timestamp" in health_data
        assert "version" in health_data
        print(f"   Response: {health_data}")

        # 3. POST /api/readings (Valid Payload)
        valid_payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "temperature_c": 23.4,
            "humidity_percent": 52.1,
            "gas_raw_value": 118.0,
            "pm25_ug_m3": 14.5,
            "pm10_ug_m3": 29.0,
            "source": "simulated",
        }
        res_post_valid = client.post("/api/readings", json=valid_payload)
        print(f"\n3a. POST /api/readings (Valid) -> Status: {res_post_valid.status_code}")
        assert res_post_valid.status_code == 201
        post_data = res_post_valid.json()
        assert "reading" in post_data
        assert post_data["reading"]["temperature_c"] == 23.4
        assert post_data["reading"]["source"] == "simulated"
        new_reading_id = post_data["reading"]["id"]
        print(f"    Created reading ID #{new_reading_id}, Alerts triggered: {len(post_data['alerts_triggered'])}")

        # 3b. POST /api/readings (Invalid Payloads - Validation Checks)
        # Invalid humidity (> 100)
        inv_hum = client.post("/api/readings", json={
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "temperature_c": 25.0,
            "humidity_percent": 150.0,
        })
        print(f"\n3b. POST /api/readings (Invalid Humidity 150%) -> Status: {inv_hum.status_code}")
        assert inv_hum.status_code == 422
        print(f"    Error detail: {inv_hum.json()['detail'][0]['msg']}")

        # Invalid temperature (< -50)
        inv_temp = client.post("/api/readings", json={
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "temperature_c": -99.0,
            "humidity_percent": 50.0,
        })
        print(f"3c. POST /api/readings (Invalid Temp -99°C) -> Status: {inv_temp.status_code}")
        assert inv_temp.status_code == 422

        # Missing required field (humidity_percent)
        inv_missing = client.post("/api/readings", json={
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "temperature_c": 25.0,
        })
        print(f"3d. POST /api/readings (Missing required field) -> Status: {inv_missing.status_code}")
        assert inv_missing.status_code == 422

        # 4. GET /api/readings/latest
        res_latest = client.get("/api/readings/latest")
        print(f"\n4. GET /api/readings/latest -> Status: {res_latest.status_code}")
        assert res_latest.status_code == 200
        latest_data = res_latest.json()
        assert "id" in latest_data and "timestamp" in latest_data
        assert latest_data["source"] == "simulated"
        print(f"   Latest: ID #{latest_data['id']} at {latest_data['timestamp']} (temp={latest_data['temperature_c']}°C)")

        # 5. GET /api/readings (Paginated and Filtered)
        res_list = client.get("/api/readings?limit=5&offset=0")
        print(f"\n5. GET /api/readings?limit=5 -> Status: {res_list.status_code}")
        assert res_list.status_code == 200
        list_data = res_list.json()
        assert "total" in list_data and "items" in list_data
        assert len(list_data["items"]) <= 5
        print(f"   Total readings in database: {list_data['total']}, Returned: {len(list_data['items'])}")

        # 6. GET /api/alerts
        res_alerts = client.get("/api/alerts?limit=10")
        print(f"\n6. GET /api/alerts -> Status: {res_alerts.status_code}")
        assert res_alerts.status_code == 200
        alerts_data = res_alerts.json()
        assert "total" in alerts_data and "active_count" in alerts_data and "acknowledged_count" in alerts_data
        print(f"   Total alerts: {alerts_data['total']}, Active: {alerts_data['active_count']}, Acknowledged: {alerts_data['acknowledged_count']}")

        # 7. PATCH /api/alerts/{alert_id} (Acknowledge)
        # Find or trigger an active alert
        active_alert_id = None
        for a in alerts_data["items"]:
            if a["status"] == "active":
                active_alert_id = a["id"]
                break

        if active_alert_id is None:
            # Trigger an active alert
            r_trigger = client.post("/api/readings", json={
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "temperature_c": 41.5,
                "humidity_percent": 50.0,
            })
            active_alert_id = r_trigger.json()["alerts_triggered"][0]["id"]
            print(f"   Triggered fresh active alert ID #{active_alert_id}")

        res_patch = client.patch(f"/api/alerts/{active_alert_id}")
        print(f"\n7. PATCH /api/alerts/{active_alert_id} -> Status: {res_patch.status_code}")
        assert res_patch.status_code == 200
        patch_data = res_patch.json()
        assert patch_data["status"] == "acknowledged"
        assert patch_data["acknowledged_at"] is not None
        print(f"   Acknowledged alert ID #{patch_data['id']} at {patch_data['acknowledged_at']}")

        # Test non-existent alert returns 404
        res_patch_404 = client.patch("/api/alerts/99999999")
        print(f"   PATCH /api/alerts/99999999 -> Status: {res_patch_404.status_code}")
        assert res_patch_404.status_code == 404

        # 8. GET /api/analytics/summary
        res_summary = client.get("/api/analytics/summary?range=24h")
        print(f"\n8. GET /api/analytics/summary?range=24h -> Status: {res_summary.status_code}")
        assert res_summary.status_code == 200
        summary_data = res_summary.json()
        assert "temperature" in summary_data
        assert "humidity" in summary_data
        assert "gas_raw" in summary_data
        assert "pm25" in summary_data
        assert "pm10" in summary_data
        assert summary_data["total_readings"] > 0
        print(f"   Summary: total_readings={summary_data['total_readings']}, active_alerts={summary_data['active_alerts']}")
        print(f"   Temp avg={summary_data['temperature']['avg']}, min={summary_data['temperature']['min']}, max={summary_data['temperature']['max']}")

        # 9. GET /api/analytics/trends
        res_trends = client.get("/api/analytics/trends?range=1h&limit=50")
        print(f"\n9. GET /api/analytics/trends?range=1h&limit=50 -> Status: {res_trends.status_code}")
        assert res_trends.status_code == 200
        trends_data = res_trends.json()
        assert "points" in trends_data
        assert "time_range" in trends_data
        print(f"   Trends: points count={trends_data['count']}")
        if trends_data["points"]:
            first_pt = trends_data["points"][0]
            last_pt = trends_data["points"][-1]
            print(f"   First point: {first_pt['timestamp']} (temp={first_pt['temperature_c']}°C)")
            print(f"   Last point:  {last_pt['timestamp']} (temp={last_pt['temperature_c']}°C)")

    print("\n" + "=" * 70)
    print("ALL 9 API ENDPOINTS SUCCESSFULLY AUDITED AND VERIFIED!")
    print("=" * 70)


if __name__ == "__main__":
    audit_api()
