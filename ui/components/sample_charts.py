"""Sample Charts
"""

from __future__ import annotations

from .components.base import generate_timeseries_df, generate_multiline_df
from .components.single_line import render_single_line_chart
from .components.bar import render_bar_chart
from .components.multi_line import render_multi_line_chart

def sample_revenue_timeseries() -> None:
    render_single_line_chart({
        'title': 'Revenue (invoice date)',
        'description': 'Monthly revenue tracked by invoice date',
        'df': generate_timeseries_df(),
        'x_field': 'date',
        'x_label': 'Date',
        'y_field': 'value',
        'y_label': 'Revenue'
    })

def sample_cashflow_timeseries() -> None:
    render_single_line_chart({
        'title': 'Cash-in (expected pay date)',
        'description': 'Expected cash inflows based on payment due dates',
        'df': generate_timeseries_df(),
        'x_field': 'date',
        'x_label': 'Date',
        'y_field': 'value',
        'y_label': 'Cash-in'
    })

def sample_revenue_bar() -> None:
    render_bar_chart({
        'title': 'Revenue (bar)',
        'description': 'Monthly revenue totals as bars',
        'df': generate_timeseries_df(),
        'x_field': 'date',
        'x_label': 'Date',
        'y_field': 'value',
        'y_label': 'Revenue'
    })

def sample_multi_line() -> None:
    render_multi_line_chart({
        'title': 'Revenue by Segment (multi-line)',
        'description': 'Four segments shown as separate lines over time',
        'df': generate_multiline_df(),
        'x_field': 'date',
        'x_label': 'Date',
        'category_field': 'series',
        'y_field': 'value',
        'y_label': 'Revenue'
    })