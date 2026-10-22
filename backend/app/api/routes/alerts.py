"""
AirWatch — Alerts API Routes
Provides listing of triggered alerts and acknowledgment actions.
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.alert import (
    AlertAcknowledgeResponse,
    AlertListResponse,
    AlertResponse,
)
from app.services import alert_service

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get(
    "",
    response_model=AlertListResponse,
    summary="List alerts with optional status/severity filters",
)
def get_alerts(
    status_filter: Optional[str] = Query(
        None,
        alias="status",
        description="Filter by alert status: 'active' or 'acknowledged'",
    ),
    severity: Optional[str] = Query(
        None,
        description="Filter by severity: 'warning' or 'critical'",
    ),
    limit: int = Query(50, ge=1, le=500, description="Max alerts to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: Session = Depends(get_db),
) -> AlertListResponse:
    """
    Returns a list of alerts recorded in the database, ordered newest-first.
    Includes overall counts for active and acknowledged alerts.
    """
    items, total, active_count, acknowledged_count = alert_service.get_alerts(
        db=db,
        status=status_filter,
        severity=severity,
        limit=limit,
        offset=offset,
    )
    return AlertListResponse(
        items=[AlertResponse.model_validate(item) for item in items],
        total=total,
        active_count=active_count,
        acknowledged_count=acknowledged_count,
        limit=limit,
        offset=offset,
    )


@router.patch(
    "/{alert_id}",
    response_model=AlertAcknowledgeResponse,
    summary="Acknowledge an alert",
)
def acknowledge_alert(
    alert_id: int,
    db: Session = Depends(get_db),
) -> AlertAcknowledgeResponse:
    """
    Marks an active alert as acknowledged and records the acknowledgment timestamp.
    Returns 404 if the alert ID does not exist.
    """
    alert = alert_service.acknowledge_alert(db, alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID {alert_id} not found",
        )
    return AlertAcknowledgeResponse(
        id=alert.id,
        status=alert.status,
        acknowledged_at=alert.acknowledged_at,
        message="Alert acknowledged successfully",
    )
