"""
AirWatch — SensorReading SQLAlchemy Model
Stores each simulated sensor reading ingested via POST /api/readings.

IMPORTANT: All readings from the standalone Python simulator have
source="simulated". PM2.5 and PM10 values are illustrative only.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    # ------------------------------------------------------------------ #
    # Primary key
    # ------------------------------------------------------------------ #
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # ------------------------------------------------------------------ #
    # Sensor fields
    # ------------------------------------------------------------------ #
    # timezone-aware UTC timestamp from the simulator
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    temperature_c: Mapped[float] = mapped_column(Float, nullable=False)
    humidity_percent: Mapped[float] = mapped_column(Float, nullable=False)

    # Optional simulated indicators
    gas_raw_value: Mapped[float | None] = mapped_column(Float, nullable=True)

    # PM2.5 and PM10 are simulated/illustrative — not real hardware measurements.
    pm25_ug_m3: Mapped[float | None] = mapped_column(Float, nullable=True)
    pm10_ug_m3: Mapped[float | None] = mapped_column(Float, nullable=True)

    # All records from the simulator carry source="simulated"
    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="simulated",
        server_default="simulated",
    )

    # ------------------------------------------------------------------ #
    # Audit
    # ------------------------------------------------------------------ #
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # ------------------------------------------------------------------ #
    # Extra index: useful for range queries used by analytics/trends
    # ------------------------------------------------------------------ #
    __table_args__ = (
        Index("ix_sensor_readings_timestamp_desc", "timestamp"),
    )

    def __repr__(self) -> str:
        return (
            f"<SensorReading id={self.id} "
            f"ts={self.timestamp.isoformat() if self.timestamp else None} "
            f"temp={self.temperature_c}°C "
            f"hum={self.humidity_percent}% "
            f"source={self.source!r}>"
        )
