"""
AirWatch — Alert Workflow and Deduplication Audit
Tests warning/critical alert generation, deduplication, and persistence of acknowledgment.
"""

from datetime import datetime, timezone
import httpx
from sqlalchemy import text
from app.db.session import engine

BASE_URL = "http://127.0.0.1:8000"


def audit_alerts():
    print("=" * 70)
    print("AIRWATCH PHASE 6: ALERT WORKFLOW & DEDUPLICATION AUDIT")
    print("=" * 70)

    with httpx.Client(base_url=BASE_URL, timeout=10.0) as client:
        # 1. Trigger Warning Alert (Temperature = 36.8°C >= 35.0°C)
        print("1. Triggering warning alert via POST /api/readings (temp=36.8°C)...")
        r_warn = client.post("/api/readings", json={
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "temperature_c": 36.8,
            "humidity_percent": 50.0,
            "source": "simulated",
        })
        assert r_warn.status_code == 201
        warn_data = r_warn.json()
        assert len(warn_data["alerts_triggered"]) == 1
        warn_alert = warn_data["alerts_triggered"][0]
        warn_alert_id = warn_alert["id"]
        print(f"   Created Warning Alert ID #{warn_alert_id}: {warn_alert['alert_type']} ({warn_alert['severity']})")
        assert warn_alert["severity"] == "warning"
        assert warn_alert["status"] == "active"

        # 2. Trigger Critical Alert (Temperature = 41.5°C >= 40.0°C)
        print("\n2. Triggering critical alert via POST /api/readings (temp=41.5°C)...")
        r_crit = client.post("/api/readings", json={
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "temperature_c": 41.5,
            "humidity_percent": 50.0,
            "source": "simulated",
        })
        assert r_crit.status_code == 201
        crit_data = r_crit.json()
        assert len(crit_data["alerts_triggered"]) == 1
        crit_alert = crit_data["alerts_triggered"][0]
        crit_alert_id = crit_alert["id"]
        print(f"   Created Critical Alert ID #{crit_alert_id}: {crit_alert['alert_type']} ({crit_alert['severity']})")
        assert crit_alert["severity"] == "critical"
        assert crit_alert["status"] == "active"

        # 3. Check alerts endpoint reflects both active alerts
        print("\n3. Verifying GET /api/alerts...")
        r_alerts = client.get("/api/alerts?limit=10")
        assert r_alerts.status_code == 200
        alerts_list = r_alerts.json()
        active_ids = [a["id"] for a in alerts_list["items"] if a["status"] == "active"]
        print(f"   Active alert IDs in API: {active_ids}")
        assert warn_alert_id in active_ids
        assert crit_alert_id in active_ids
        pre_ack_active = alerts_list["active_count"]

        # 4. Acknowledge Warning Alert
        print(f"\n4. Acknowledging Warning Alert #{warn_alert_id} via PATCH /api/alerts/{warn_alert_id}...")
        r_ack = client.patch(f"/api/alerts/{warn_alert_id}")
        assert r_ack.status_code == 200
        ack_resp = r_ack.json()
        print(f"   Acknowledgment response: status={ack_resp['status']}, ack_at={ack_resp['acknowledged_at']}")
        assert ack_resp["status"] == "acknowledged"

        # 5. Verify direct PostgreSQL persistence
        print("\n5. Verifying persistence in PostgreSQL...")
        with engine.connect() as conn:
            db_row = conn.execute(
                text("SELECT id, status, acknowledged_at, severity FROM alerts WHERE id = :id;"),
                {"id": warn_alert_id},
            ).mappings().one()
            print(f"   PostgreSQL Row #{db_row['id']}: status={db_row['status']}, ack_at={db_row['acknowledged_at']}")
            assert db_row["status"] == "acknowledged"
            assert db_row["acknowledged_at"] is not None

        # 6. Verify GET /api/alerts shows active_count decremented
        r_alerts_post = client.get("/api/alerts?limit=10")
        post_ack_active = r_alerts_post.json()["active_count"]
        print(f"\n6. Active alerts count updated: {pre_ack_active} -> {post_ack_active}")
        assert post_ack_active == pre_ack_active - 1

        # 7. Test de-duplication logic in alert service
        print("\n7. Verifying alert deduplication behavior...")
        from app.services.alert_service import evaluate_reading_thresholds
        from app.models.sensor_reading import SensorReading
        from sqlalchemy.orm import Session
        with Session(engine) as session:
            reading = session.get(SensorReading, warn_data["reading"]["id"])
            # Re-evaluating thresholds on the same reading
            dup_alerts = evaluate_reading_thresholds(session, reading)
            session.commit()
            print(f"   Re-evaluating thresholds on reading #{reading.id} generated {len(dup_alerts)} duplicate alerts.")
            assert len(dup_alerts) == 0, "Duplicate alert was created for the same reading!"

        print("\n" + "=" * 70)
        print("ALERT WORKFLOW & DEDUPLICATION AUDIT: CONFIRMED (PASS)")
        print("=" * 70)


if __name__ == "__main__":
    audit_alerts()
