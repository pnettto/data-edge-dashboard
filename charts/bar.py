"""Reusable bar chart component."""

from __future__ import annotations

import streamlit as st
from dataclasses import dataclass

from .base import BaseChartConfig, bar_chart

@dataclass
class BarChartConfig(BaseChartConfig):
    x_field: str
    x_label: str
    y_field: str
    y_label: str


def render_bar_chart(config: BarChartConfig):
    st.subheader(config['title'])
    st.caption(config['description'])
    st.altair_chart(
        bar_chart(config['df'], config['x_field'], config['x_label'],
                  config['y_field'], config['y_label']),
        use_container_width=True,
    )