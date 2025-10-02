"""Charts aggregator: re-export chart components from split modules.

This keeps the public import `from ui.components import charts` stable while
allowing the implementation to live in smaller focused files.
"""

from __future__ import annotations

from .charts_components.base import DEFAULT_DATE_RANGE
from .charts_components.single_line import revenue_timeseries, cashflow_timeseries
from .charts_components.bar import revenue_bar
from .charts_components.multi_line import sample_multi_line

__all__ = [
    "DEFAULT_DATE_RANGE",
    # Single-series
    "revenue_timeseries",
    "cashflow_timeseries",
    # Other chart types
    "revenue_bar",
    "sample_multi_line",
]
