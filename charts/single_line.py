"""Single-series time series charts used in the dashboard."""

from __future__ import annotations

import streamlit as st
import pandas as pd
import altair as alt

def render_single_line_chart(config):
    st.subheader(config['title'])
    st.caption(config['description'])
    st.altair_chart(line_chart_single(config['df'], config['x_field'], config['x_label'], config['y_field'], config['y_label']), use_container_width=True)

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


