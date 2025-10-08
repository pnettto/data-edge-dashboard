"""Bar chart component with Prophet-based forecasting capability"""

import streamlit as st
import pandas as pd

from .chart import build_chart
from .forecast import create_forecast_df


def render_bar_chart(config: dict) -> None:
    """
    Main entry point for rendering a bar chart with optional forecasting.

    Args:
        config (dict): Dictionary containing chart configuration with the following keys:
            - title (str): Title of the chart.
            - description (str): Description or caption for the chart.
            - df (pd.DataFrame): DataFrame containing the data to plot.
            - x_field (str): Name of the column to use for the x-axis.
            - y_field (str): Name of the column to use for the y-axis.
            - category_field (str, optional): Name of the column for categorical grouping (optional).
            - category_label (str, optional): Title of the column for categorical grouping (optional).
            - forecast (bool, optional): Whether to enable forecasting (default: False).
            - trendline (bool, optional): Whether to show a trendline for single bar charts (default: False).
    """
    st.subheader(config['title'])
    st.caption(config['description'])

    actual_df = config['df'].copy()
    actual_df["type"] = "Actual"

    # Generate forecast
    forecast_df = create_forecast_df(config)

    # Combine all data for plotting
    plot_df = pd.concat([actual_df, forecast_df], ignore_index=True)

    # Build and display chart
    chart = build_chart(plot_df, config)
    st.altair_chart(chart, use_container_width=True)


__all__ = ['render_bar_chart']