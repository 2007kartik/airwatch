"""
AirWatch — Alert SQLAlchemy Model
Records threshold violations generated during sensor reading ingestion.
All thresholds are configurable demo thresholds — not regulatory health advice.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Alert(Base):
    __tablename__ = "alerts"

    # ------------------------------------------------------------------ #
    # Primary key
    # ------------------------------------------------------------------ #
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # ------------------------------------------------------------------ #
    # Foreign key to sensor_readings
    # ------------------------------------------------------------------ #
    reading_id: Mapped[int] = mapped_column(
        ForeignKey("sensor_readings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ------------------------------------------------------------------ #
    # Alert classification
    # ------------------------------------------------------------------ #
    # e.g. "temperature_high", "pm25_high", "humidity_high"
    alert_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # "warning" or "critical"
    severity: Mapped[str] = mapped_column(String(20), nullable=False, index=True)

    # Human-readable explanation shown in the dashboard alerts panel
    message: Mapped[str] = mapped_column(Text, nullable=False)

    # ------------------------------------------------------------------ #
    # Observed vs configured threshold (for display)
    # ------------------------------------------------------------------ #
    observed_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    threshold_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # ------------------------------------------------------------------ #
    # Lifecycle
    # ------------------------------------------------------------------ #
    # "active" or "acknowledged"
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="active",
        server_default="active",
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ------------------------------------------------------------------ #
    # Relationship (load parent reading on demand)
    # ------------------------------------------------------------------ #
    reading: Mapped["SensorReading"] = relationship(  # noqa: F821
        "SensorReading",
        lazy="select",
    )

    # ------------------------------------------------------------------ #
    # Uniqueness: prevent duplicate alerts for same reading + rule
    # ------------------------------------------------------------------ #
    __table_args__ = (
        UniqueConstraint(
            "reading_id",
            "alert_type",
            name="uq_alert_reading_type",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<Alert id={self.id} "
            f"type={self.alert_type!r} "
            f"severity={self.severity!r} "
            f"status={self.status!r} "
            f"reading_id={self.reading_id}>"
        )
