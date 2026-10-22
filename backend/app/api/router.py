"""
AirWatch — Master API Router
Aggregates all route modules under the /api prefix.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.routes import alerts, analytics, health, readings

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(readings.router)
api_router.include_router(alerts.router)
api_router.include_router(analytics.router)
