"""Base helpers and constants for chart components."""

from __future__ import annotations

import numpy as np
import pandas as pd
import altair as alt

from dataclasses import dataclass
from typing import Literal

@dataclass
class BaseChartConfig:
    type: Literal['single_line', 'multi_line', 'bar']
    title: str
    df: pd.DataFrame
    description: str

# In the future this could be part of a global filter
DEFAULT_DATE_RANGE = ('2023-01-01', '2025-01-01')

# Temporary functions to mimic the dfs coming from the exploratory analysis
def generate_timeseries_df():
    start, end = DEFAULT_DATE_RANGE
    idx = pd.date_range(start=start, end=end, freq="MS") # freq month start
    n_points = len(idx)
    rng = np.random.default_rng(np.random.randint(1, 99))
    base = rng.normal(loc=5500, scale=1500, size=n_points)
    trend = np.linspace(0, 2000, n_points)
    values = np.maximum(base + trend, 1000).astype(float)
    values = np.minimum(values, 10000)
    df = pd.DataFrame({"value": values})
    df.insert(0, "date", idx)
    return df
    
def generate_multiline_df():
    start, end = DEFAULT_DATE_RANGE
    idx = pd.date_range(start=start, end=end, freq="MS")

    rng = np.random.default_rng(17)
    series_names = ["North", "South", "East", "West"]
    frames: list[pd.DataFrame] = []
    for i, name in enumerate(series_names):
        values = np.maximum(
            rng.normal(loc=700_000 + i * 120_000, scale=250_000, size=len(idx))
            + np.linspace(0, 400_000, len(idx)),
            0,
        )
        frames.append(pd.DataFrame({"date": idx, "series": name, "value": values}))

    df = pd.concat(frames, ignore_index=True)
    return df
# End of temporary functions

def line_chart_single(df: pd.DataFrame, x_field: str, x_title: str, y_field: str, y_title: str) -> alt.Chart:
    return (
        alt.Chart(df)
        .mark_line(point=True)
        .encode(
            x=alt.X(f"{x_field}:T", title=x_title),
            y=alt.Y(f"{y_field}:Q", title=y_title, axis=alt.Axis(format=",.0f")),
            tooltip=[
                alt.Tooltip(f"{x_field}:T", title=x_title),
                alt.Tooltip(f"{y_field}:Q", title=y_title, format=","),
            ],
        )
        .properties(height=340)
        .interactive()
    )


def line_chart_multi(df: pd.DataFrame, x_field: str, category_field: str, y_field: str, y_title: str) -> alt.Chart:
    return (
        alt.Chart(df)
        .mark_line(point=True)
        .encode(
            x=alt.X(f"{x_field}:T", title="Date"),
            y=alt.Y(f"{y_field}:Q", title=y_title, axis=alt.Axis(format=",")),
            color=alt.Color(f"{category_field}:N", title="series"),
            tooltip=[
                alt.Tooltip(f"{x_field}:T", title="Date"),
                alt.Tooltip(f"{category_field}:N", title="series"),
                alt.Tooltip(f"{y_field}:Q", title=y_title, format=","),
            ],
        )
        .properties(height=340)
        .interactive()
    )

def bar_chart(df: pd.DataFrame, x_field: str, x_title: str, y_field: str, y_title: str) -> alt.Chart:
    return (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X(f"{x_field}:T", title=x_title),
            y=alt.Y(f"{y_field}:Q", title=y_title, axis=alt.Axis(format=",")),
            tooltip=[
                alt.Tooltip(f"{x_field}:T", title=x_title),
                alt.Tooltip(f"{y_field}:Q", title=y_title, format=","),
            ],
        )
        .properties(height=340)
        .interactive()
    )