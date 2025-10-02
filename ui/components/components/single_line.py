"""Single-series time series charts used in the dashboard."""

from __future__ import annotations

import pandas as pd
import streamlit as st
from dataclasses import dataclass

from .base import BaseChartConfig, line_chart_single

@dataclass
class LineChartConfig(BaseChartConfig):
    x_field: str
    x_label: str
    y_field: str
    y_label: str
    
def render_single_line_chart(config: LineChartConfig):
    st.subheader(config['title'])
    st.caption(config['description'])
    st.altair_chart(line_chart_single(config['df'], config['x_field'], config['x_label'], config['y_field'], config['y_label']), use_container_width=True)