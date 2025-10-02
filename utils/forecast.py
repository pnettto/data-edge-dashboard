"""Forecast utilities placeholder.

This module will later house forecasting logic (e.g., linear trend, simple
moving averages, or third-party models). For now, we keep a minimal API
surface so chart components can query a selected method.
"""

from typing import Literal

ForecastMethod = Literal["Linear trend", "Last 6-month avg", "Prophet (soon)"]


def list_methods() -> list[ForecastMethod]:
    return ["Linear trend", "Last 6-month avg", "Prophet (soon)"]


