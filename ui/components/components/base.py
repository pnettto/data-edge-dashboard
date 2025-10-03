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