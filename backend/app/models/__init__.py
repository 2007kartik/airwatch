"""
AirWatch models package.
Import models here so Alembic env.py can discover all of them in one import.
"""

from app.models.sensor_reading import SensorReading
from app.models.alert import Alert

__all__ = ["SensorReading", "Alert"]
