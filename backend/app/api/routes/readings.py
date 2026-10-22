"""
AirWatch — Readings API Routes
Provides ingestion and retrieval of simulated sensor readings.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.alert import AlertResponse
from app.schemas.reading import (
    ReadingCreate,
    ReadingIngestResult,
    ReadingListResponse,
    ReadingResponse,
)
from app.services import reading_service

router = APIRouter(prefix="/readings", tags=["readings"])


@router.post(
    "",
    response_model=ReadingIngestResult,
    status_code=status.HTTP_201_CREATED,
    summary="Ingest a simulated sensor reading",
)
def ingest_reading(
    reading_in: ReadingCreate,
    db: Session = Depends(get_db),
) -> ReadingIngestResult:
    """
    Ingests one sensor reading from the simulator.
    Validates numeric ranges, persists the reading to PostgreSQL,
    evaluates configurable alert thresholds, and saves any triggered alerts.
    """
    reading, alerts = reading_service.create_reading(db, reading_in)

    reading_data = ReadingResponse.model_validate(reading)
    alerts_data = [AlertResponse.model_validate(a).model_dump() for a in alerts]

    return ReadingIngestResult(
        reading=reading_data,
        alerts_triggered=alerts_data,
        message="Reading ingested successfully",
    )


@router.get(
    "/latest",
    response_model=ReadingResponse,
    summary="Get the most recent sensor reading",
)
def get_latest_reading(
    db: Session = Depends(get_db),
) -> ReadingResponse:
    """
    Returns the newest sensor reading recorded in the database.
    Returns 404 if no readings have been recorded yet.
    """
    reading = reading_service.get_latest_reading(db)
    if not reading:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No sensor readings found in database",
        )
    return ReadingResponse.model_validate(reading)


@router.get(
    "",
    response_model=ReadingListResponse,
    summary="Get historical sensor readings with pagination and time filters",
)
def get_readings_history(
    limit: int = Query(50, ge=1, le=500, description="Max readings to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    start: Optional[datetime] = Query(None, description="Start UTC timestamp filter"),
    end: Optional[datetime] = Query(None, description="End UTC timestamp filter"),
    db: Session = Depends(get_db),
) -> ReadingListResponse:
    """
    Returns a paginated list of sensor readings ordered newest-first.
    Supports optional ISO 8601 UTC start and end bounds.
    """
    items, total = reading_service.get_readings(
        db=db,
        limit=limit,
        offset=offset,
        start=start,
        end=end,
    )
    return ReadingListResponse(
        items=[ReadingResponse.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )
