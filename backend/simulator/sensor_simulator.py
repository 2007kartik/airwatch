"""
AirWatch — Standalone Python Sensor Simulator
Generates plausible simulated environmental readings and posts them to FastAPI.

Features:
  - Generates readings every ~5 seconds with natural drift and mean reversion.
  - Generates configurable occasional spikes to test warning/critical alert thresholds.
  - Implements HTTP timeouts, exponential backoff, and automatic recovery.
  - Clear console status reporting for normal ingestion, spikes, errors, and reconnection.
  - All data is labeled source="simulated". No real or regulatory AQI claims.
"""

from __future__ import annotations

import argparse
import logging
import os
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import httpx

# Add backend directory to sys.path so app modules can be imported if needed
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Try loading .env if python-dotenv is available
try:
    from dotenv import load_dotenv
    env_file = BACKEND_DIR / ".env"
    if env_file.exists():
        load_dotenv(env_file)
except ImportError:
    pass

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("sensor_simulator")


class SensorDataGenerator:
    """
    Simulates environmental sensor readings with gradual drift,
    mean-reversion, and occasional configurable spikes.
    """

    def __init__(
        self,
        base_temp: float = 24.0,
        base_humidity: float = 50.0,
        base_gas: float = 120.0,
        base_pm25: float = 15.0,
        base_pm10: float = 30.0,
        spike_probability: float = 0.05,
    ):
        self.base_temp = base_temp
        self.base_humidity = base_humidity
        self.base_gas = base_gas
        self.base_pm25 = base_pm25
        self.base_pm10 = base_pm10
        self.spike_probability = spike_probability

        # Current internal state
        self.temp = base_temp
        self.humidity = base_humidity
        self.gas = base_gas
        self.pm25 = base_pm25
        self.pm10 = base_pm10

        # Spike cooldown / decay state
        self.active_spike: Optional[str] = None
        self.spike_decay_steps = 0

    def generate_reading(
        self,
        force_spike: Optional[str] = None,
        force_severity: str = "warning",
    ) -> tuple[dict[str, Any], Optional[str]]:
        """
        Generates the next reading dictionary.
        Returns: (reading_dict, spike_description_or_None)
        """
        spike_info: Optional[str] = None

        # Check if we should trigger a spike
        trigger_spike = force_spike is not None or (
            random.random() < self.spike_probability and self.spike_decay_steps <= 0
        )

        if trigger_spike:
            metric = force_spike or random.choice(["temp", "humidity", "gas", "pm25", "pm10"])
            severity = force_severity if force_spike else ("critical" if random.random() < 0.3 else "warning")

            if metric == "temp":
                val = random.uniform(40.5, 43.0) if severity == "critical" else random.uniform(35.5, 38.5)
                self.temp = val
                spike_info = f"Temperature {severity.upper()} spike: {val:.1f}°C"
            elif metric == "humidity":
                val = random.uniform(91.0, 96.0) if severity == "critical" else random.uniform(81.0, 88.0)
                self.humidity = val
                spike_info = f"Humidity {severity.upper()} spike: {val:.1f}%"
            elif metric == "gas":
                val = random.uniform(520.0, 650.0) if severity == "critical" else random.uniform(320.0, 450.0)
                self.gas = val
                spike_info = f"Gas {severity.upper()} spike: {val:.1f}"
            elif metric == "pm25":
                val = random.uniform(58.0, 75.0) if severity == "critical" else random.uniform(37.0, 50.0)
                self.pm25 = val
                self.pm10 = max(self.pm10, val * 2.0)
                spike_info = f"Simulated PM2.5 {severity.upper()} spike: {val:.1f} µg/m³"
            elif metric == "pm10":
                val = random.uniform(260.0, 320.0) if severity == "critical" else random.uniform(160.0, 220.0)
                self.pm10 = val
                spike_info = f"Simulated PM10 {severity.upper()} spike: {val:.1f} µg/m³"

            self.active_spike = metric
            self.spike_decay_steps = 3  # Decay back over 3 cycles

        else:
            # Gradual random walk with mean reversion
            if self.spike_decay_steps > 0:
                self.spike_decay_steps -= 1
                decay_weight = 0.4
            else:
                decay_weight = 0.05

            # Temperature: drift ±0.3°C, mean-revert to base
            self.temp += random.uniform(-0.3, 0.3) + decay_weight * (self.base_temp - self.temp)
            self.temp = max(16.0, min(34.0 if self.spike_decay_steps <= 0 else 45.0, self.temp))

            # Humidity: drift ±0.6%, mean-revert to base
            self.humidity += random.uniform(-0.6, 0.6) + decay_weight * (self.base_humidity - self.humidity)
            self.humidity = max(30.0, min(75.0 if self.spike_decay_steps <= 0 else 98.0, self.humidity))

            # Gas raw: drift ±3.0, mean-revert to base
            self.gas += random.uniform(-3.0, 3.0) + decay_weight * (self.base_gas - self.gas)
            self.gas = max(60.0, min(250.0 if self.spike_decay_steps <= 0 else 700.0, self.gas))

            # PM2.5: drift ±0.8, mean-revert to base
            self.pm25 += random.uniform(-0.8, 0.8) + decay_weight * (self.base_pm25 - self.pm25)
            self.pm25 = max(5.0, min(30.0 if self.spike_decay_steps <= 0 else 90.0, self.pm25))

            # PM10: approximately 2x PM2.5 ± 2.0
            self.pm10 = self.pm25 * 2.0 + random.uniform(-2.0, 2.0)
            self.pm10 = max(10.0, min(65.0 if self.spike_decay_steps <= 0 else 350.0, self.pm10))

        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "temperature_c": round(self.temp, 2),
            "humidity_percent": round(self.humidity, 2),
            "gas_raw_value": round(self.gas, 1),
            "pm25_ug_m3": round(self.pm25, 1),
            "pm10_ug_m3": round(self.pm10, 1),
            "source": "simulated",
        }
        return payload, spike_info


class SensorSimulator:
    """
    Manages the sensor generation loop, HTTP transport,
    exponential backoff retry strategy, and error logging.
    """

    def __init__(
        self,
        api_url: str = "http://localhost:8000",
        interval_seconds: float = 5.0,
        spike_probability: float = 0.05,
        max_retries: int = 5,
        backoff_base_delay: float = 1.0,
        backoff_max_delay: float = 30.0,
        http_timeout: float = 5.0,
    ):
        self.api_url = api_url.rstrip("/")
        self.endpoint = f"{self.api_url}/api/readings"
        self.interval_seconds = interval_seconds
        self.spike_probability = spike_probability
        self.max_retries = max_retries
        self.backoff_base_delay = backoff_base_delay
        self.backoff_max_delay = backoff_max_delay
        self.http_timeout = http_timeout

        self.generator = SensorDataGenerator(spike_probability=spike_probability)
        self.was_disconnected = False
        self.total_sent = 0
        self.total_failed = 0

    def post_reading_with_retry(self, payload: dict[str, Any]) -> tuple[bool, Optional[dict]]:
        """
        Attempts to post reading to the FastAPI endpoint.
        Uses exponential backoff for connection errors.
        Returns: (success: bool, response_json_or_None)
        """
        delay = self.backoff_base_delay

        for attempt in range(1, self.max_retries + 1):
            try:
                with httpx.Client(timeout=self.http_timeout) as client:
                    resp = client.post(self.endpoint, json=payload)

                    if resp.status_code in (200, 201):
                        if self.was_disconnected:
                            logger.info(
                                "RECONNECTED: Connection restored to %s after previous failure.",
                                self.endpoint,
                            )
                            self.was_disconnected = False
                        self.total_sent += 1
                        return True, resp.json()

                    logger.warning(
                        "API returned HTTP %d: %s (attempt %d/%d)",
                        resp.status_code,
                        resp.text[:120],
                        attempt,
                        self.max_retries,
                    )

            except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError) as exc:
                self.was_disconnected = True
                if attempt == 1:
                    logger.warning(
                        "Connection issue contacting %s: %s",
                        self.endpoint,
                        exc.__class__.__name__,
                    )
                if attempt < self.max_retries:
                    logger.info(
                        "Retrying in %.1fs (attempt %d/%d)...",
                        delay,
                        attempt,
                        self.max_retries,
                    )
                    time.sleep(delay)
                    delay = min(delay * 2.0, self.backoff_max_delay)

            except Exception as exc:
                logger.error("Unexpected error submitting reading: %s", exc)
                break

        self.total_failed += 1
        return False, None

    def run_once(
        self,
        force_spike: Optional[str] = None,
        force_severity: str = "warning",
    ) -> tuple[bool, dict[str, Any], Optional[str], Optional[dict]]:
        """
        Generates and posts a single reading.
        Returns: (success, payload, spike_info, response_json)
        """
        payload, spike_info = self.generator.generate_reading(
            force_spike=force_spike,
            force_severity=force_severity,
        )
        if spike_info:
            logger.warning("[SPIKE EVENT] %s", spike_info)

        success, response_data = self.post_reading_with_retry(payload)

        if success:
            alerts_count = len(response_data.get("alerts_triggered", [])) if response_data else 0
            alert_str = f" | Alerts: {alerts_count}" if alerts_count > 0 else ""
            logger.info(
                "Ingested #%d | Temp: %.1f°C | Hum: %.1f%% | Gas: %.1f | PM2.5: %.1f | PM10: %.1f%s",
                self.total_sent,
                payload["temperature_c"],
                payload["humidity_percent"],
                payload["gas_raw_value"],
                payload["pm25_ug_m3"],
                payload["pm10_ug_m3"],
                alert_str,
            )
        else:
            logger.error("Failed to deliver reading for timestamp %s", payload["timestamp"])

        return success, payload, spike_info, response_data

    def run_loop(self, count: Optional[int] = None) -> None:
        """
        Runs the simulation loop continuously (or for `count` readings).
        Gracefully handles SIGINT/KeyboardInterrupt.
        """
        logger.info("=" * 65)
        logger.info("AirWatch — Standalone Sensor Simulator Started")
        logger.info("Target API:           %s", self.endpoint)
        logger.info("Generation Interval:  %.1f seconds", self.interval_seconds)
        logger.info("Spike Probability:    %.1f%%", self.spike_probability * 100)
        logger.info("Data Disclaimer:      ALL DATA IS SIMULATED (no physical hardware)")
        logger.info("=" * 65)

        readings_generated = 0

        try:
            while True:
                self.run_once()
                readings_generated += 1

                if count is not None and readings_generated >= count:
                    logger.info("Completed requested count of %d readings.", count)
                    break

                time.sleep(self.interval_seconds)

        except KeyboardInterrupt:
            logger.info("Simulator interrupted by user. Shutting down gracefully...")

        logger.info(
            "Simulator stopped. Total sent: %d | Total failed: %d",
            self.total_sent,
            self.total_failed,
        )


def parse_args() -> argparse.Namespace:
    """Parses command-line arguments, with fallback to environment variables."""
    default_url = os.getenv("SIMULATOR_API_URL", "http://localhost:8000")
    default_interval = float(os.getenv("SIMULATOR_INTERVAL_SECONDS", "5.0"))
    default_spike_prob = float(os.getenv("SIMULATOR_SPIKE_PROBABILITY", "0.05"))

    parser = argparse.ArgumentParser(
        description="AirWatch — Standalone Sensor Simulator",
    )
    parser.add_argument(
        "--api-url",
        default=default_url,
        help=f"FastAPI base URL (default: {default_url})",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=default_interval,
        help=f"Interval between readings in seconds (default: {default_interval})",
    )
    parser.add_argument(
        "--spike-prob",
        type=float,
        default=default_spike_prob,
        help=f"Probability of threshold spike per reading [0.0 - 1.0] (default: {default_spike_prob})",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=None,
        help="Number of readings to generate before exiting (default: infinite loop)",
    )
    parser.add_argument(
        "--single-run",
        action="store_true",
        help="Generate and post a single reading and exit",
    )
    parser.add_argument(
        "--force-spike",
        choices=["temp", "humidity", "gas", "pm25", "pm10"],
        default=None,
        help="Force a spike on a specific metric for testing alerts",
    )
    parser.add_argument(
        "--severity",
        choices=["warning", "critical"],
        default="warning",
        help="Severity when using --force-spike (default: warning)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    simulator = SensorSimulator(
        api_url=args.api_url,
        interval_seconds=args.interval,
        spike_probability=args.spike_prob,
    )

    if args.single_run or args.force_spike:
        success, _, _, _ = simulator.run_once(
            force_spike=args.force_spike,
            force_severity=args.severity,
        )
        sys.exit(0 if success else 1)

    simulator.run_loop(count=args.count)


if __name__ == "__main__":
    main()
