"""Multi-line line chart component."""

from __future__ import annotations

import streamlit as st
from dataclasses import dataclass

from .base import BaseChartConfig, generate_multiline_df, line_chart_multi

@dataclass
class MultiLineChartConfig(BaseChartConfig):
    x_field: str
    x_label: str
    category_field: str
    y_field: str
    y_label: str

def render_multi_line_chart(config: MultiLineChartConfig):
    st.subheader(config['title'])
    st.caption(config['description'])
    st.altair_chart(
        line_chart_multi(
            config['df'],
            config['x_field'],
            config['category_field'],
            config['y_field'],
            config['y_label'],
        ),
        use_container_width=True,
    )