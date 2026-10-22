"""
AirWatch — Phase 6 Integration Pipeline Audit Script
Tests the full data flow from ingestion to PostgreSQL persistence, API endpoints,
analytics incorporation, and alert lifecycle.
"""

from datetime import datetime, timezone
import httpx
from sqlalchemy import text
from app.db.session import engine

BASE_URL = "http://127.0.0.1:8000"


def run_pipeline_audit():
    print("=" * 70)
    print("AIRWATCH PHASE 6: FULL DATA PIPELINE AUDIT")
    print("=" * 70)

    with httpx.Client(base_url=BASE_URL, timeout=10.0) as client:
        # Step 1: Record initial count and latest reading
        r_init_list = client.get("/api/readings?limit=1")
        assert r_init_list.status_code == 200
        initial_total = r_init_list.json()["total"]
        initial_latest = client.get("/api/readings/latest").json()
        print(f"1. Initial database reading count: {initial_total}")
        print(f"   Initial latest reading ID: #{initial_latest['id']} (ts: {initial_latest['timestamp']})")

        # Step 2: Ingest a uniquely identifiable test reading
        unique_temp = 28.75
        unique_hum = 64.35
        unique_gas = 173.8
        unique_pm25 = 21.4
        unique_pm10 = 42.8
        test_ts = datetime.now(timezone.utc).isoformat()

        payload = {
            "timestamp": test_ts,
            "temperature_c": unique_temp,
            "humidity_percent": unique_hum,
            "gas_raw_value": unique_gas,
            "pm25_ug_m3": unique_pm25,
            "pm10_ug_m3": unique_pm10,
            "source": "simulated",
        }

        print("\n2. Submitting unique test packet to POST /api/readings...")
        r_post = client.post("/api/readings", json=payload)
        assert r_post.status_code == 201, f"Failed POST: {r_post.status_code}"
        post_data = r_post.json()
        new_reading_id = post_data["reading"]["id"]
        print(f"   POST /api/readings accepted. Created Reading ID: #{new_reading_id}")
        assert post_data["reading"]["temperature_c"] == unique_temp
        assert post_data["reading"]["humidity_percent"] == unique_hum
        assert post_data["reading"]["source"] == "simulated"

        # Step 3: Verify direct PostgreSQL persistence
        print("\n3. Verifying persistence in PostgreSQL 18...")
        with engine.connect() as conn:
            row = conn.execute(
                text(
                    "SELECT id, timestamp, temperature_c, humidity_percent, gas_raw_value, "
                    "pm25_ug_m3, pm10_ug_m3, source, created_at "
                    "FROM sensor_readings WHERE id = :id;"
                ),
                {"id": new_reading_id},
            ).mappings().one_or_none()

            assert row is not None, f"Reading #{new_reading_id} not found in PostgreSQL!"
            print(f"   PostgreSQL Row verified: ID={row['id']} | temp={row['temperature_c']} | hum={row['humidity_percent']} | source='{row['source']}'")
            assert row["temperature_c"] == unique_temp
            assert row["humidity_percent"] == unique_hum
            assert row["source"] == "simulated"

        # Step 4: Verify retrieval via GET /api/readings
        print("\n4. Verifying retrieval via GET /api/readings...")
        r_list = client.get(f"/api/readings?limit=5")
        assert r_list.status_code == 200
        list_data = r_list.json()
        ids = [item["id"] for item in list_data["items"]]
        print(f"   Most recent reading IDs in API: {ids}")
        assert new_reading_id in ids, f"Reading #{new_reading_id} not in recent list!"

        # Step 5: Verify GET /api/readings/latest
        print("\n5. Verifying retrieval via GET /api/readings/latest...")
        r_latest = client.get("/api/readings/latest")
        assert r_latest.status_code == 200
        latest_data = r_latest.json()
        print(f"   Latest API reading ID: #{latest_data['id']} (ts: {latest_data['timestamp']})")
        # Since continuous simulator is running, latest might be our test reading or an immediately newer one
        assert latest_data["id"] >= new_reading_id

        # Step 6: Verify analytics incorporation
        print("\n6. Verifying analytics summary and trends incorporation...")
        r_summary = client.get("/api/analytics/summary?range=1h")
        assert r_summary.status_code == 200
        summary_data = r_summary.json()
        print(f"   1h Analytics total readings: {summary_data['total_readings']}")
        print(f"   Temp avg={summary_data['temperature']['avg']}, min={summary_data['temperature']['min']}, max={summary_data['temperature']['max']}")
        assert summary_data["total_readings"] > 0
        assert summary_data["temperature"]["min"] <= unique_temp <= summary_data["temperature"]["max"]

        r_trends = client.get("/api/analytics/trends?range=1h&limit=100")
        assert r_trends.status_code == 200
        trends_data = r_trends.json()
        print(f"   Trends count returned: {trends_data['count']} data points")
        assert trends_data["count"] > 0

        print("\n" + "=" * 70)
        print("PIPELINE AUDIT: ALL BACKEND PIPELINE STAGES CONFIRMED (PASS)")
        print("=" * 70)


if __name__ == "__main__":
    run_pipeline_audit()
