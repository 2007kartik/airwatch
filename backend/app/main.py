"""
AirWatch — FastAPI Application Entry Point
Phase 2: Application skeleton with health endpoint.
Full API routes are implemented in Phase 3.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.session import check_db_connection

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.DEBUG if settings.app_env == "development" else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("airwatch")


# ---------------------------------------------------------------------------
# Lifespan: runs startup/shutdown logic
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("AirWatch API starting up (env=%s)", settings.app_env)
    db_ok = check_db_connection()
    if db_ok:
        logger.info("Database connection: OK")
    else:
        logger.warning(
            "Database connection: FAILED — check DATABASE_URL in .env"
        )
    yield
    logger.info("AirWatch API shutting down")


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------
app = FastAPI(
    title="AirWatch API",
    description=(
        "Real-Time Air Quality Monitoring Dashboard — "
        "All sensor data is SIMULATED (no physical hardware)."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS — allow the React dev server origins defined in .env
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# API Routes (Phase 3)
# ---------------------------------------------------------------------------
from app.api.router import api_router

app.include_router(api_router, prefix="/api")


# ---------------------------------------------------------------------------
# Root redirect / info
# ---------------------------------------------------------------------------
@app.get("/", include_in_schema=False)
def root() -> dict:
    return {
        "message": "AirWatch API — visit /docs for interactive documentation",
        "data_notice": "All sensor readings are SIMULATED. Not real-world measurements.",
    }
