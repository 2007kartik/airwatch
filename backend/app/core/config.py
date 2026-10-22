"""
AirWatch — Application Configuration
Reads all settings from environment variables (or .env file).
Never hardcodes secrets. All threshold values are demo/configurable thresholds.
"""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central settings for the AirWatch application."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ------------------------------------------------------------------ #
    # Database
    # ------------------------------------------------------------------ #
    database_url: str = (
        "postgresql+psycopg://airwatch_user:change_me@localhost:5432/airwatch"
    )

    # ------------------------------------------------------------------ #
    # FastAPI / Application
    # ------------------------------------------------------------------ #
    app_env: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Stored as a raw comma-separated string so pydantic-settings does NOT
    # attempt to JSON-parse it. Use the `cors_origins_list` property at runtime.
    cors_origins: str = (
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000"
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Return CORS_ORIGINS as a parsed list of origin strings."""
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    # ------------------------------------------------------------------ #
    # Alert Thresholds
    # All values are demo / configurable thresholds — not regulatory advice.
    # ------------------------------------------------------------------ #
    threshold_temp_warning: float = 35.0
    threshold_temp_critical: float = 40.0

    threshold_humidity_warning: float = 80.0
    threshold_humidity_critical: float = 90.0

    threshold_gas_warning: float = 300.0
    threshold_gas_critical: float = 500.0

    threshold_pm25_warning: float = 35.4
    threshold_pm25_critical: float = 55.4

    threshold_pm10_warning: float = 154.0
    threshold_pm10_critical: float = 254.0

    # ------------------------------------------------------------------ #
    # Simulator (used by simulator/sensor_simulator.py)
    # ------------------------------------------------------------------ #
    simulator_api_url: str = "http://localhost:8000"
    simulator_interval_seconds: int = 5
    simulator_spike_probability: float = 0.05


# Single module-level settings instance — import this everywhere.
settings = Settings()

