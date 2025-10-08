"""Line chart component with Prophet-based forecasting capability"""

import streamlit as st
import pandas as pd

from .chart import build_chart
from .forecast import create_forecast_df, create_connector_df


def render_line_chart(config: dict) -> None:
    """
    Main entry point for rendering a line chart with optional forecasting.

    Args:
        config (dict): Dictionary containing chart configuration with the following keys:
            - title (str): Title of the chart.
            - description (str): Description or caption for the chart.
            - df (pd.DataFrame): DataFrame containing the data to plot.
            - x_field (str): Name of the column to use for the x-axis (should be datetime or convertible).
            - y_field (str): Name of the column to use for the y-axis.
            - category_field (str, optional): Name of the column for categorical grouping (optional).
            - category_label (str, optional): (chart) Title of the column for categorical grouping (optional).
            - forecast (bool, optional): Whether to enable forecasting (default: False).
    """
    st.subheader(config['title'])
    st.caption(config['description'])

    actual_df = config['df'].copy()
    x_field = config['x_field']
    y_field = config['y_field']
    category_field = config.get('category_field')

    # Convert x-axis to datetime only if forecast is enabled
    if config.get('forecast', False):
        if not pd.api.types.is_datetime64_any_dtype(actual_df[x_field]):
            actual_df[x_field] = pd.to_datetime(actual_df[x_field])

    actual_df["type"] = "Actual"

    # Generate forecast and connectors
    forecast_df = create_forecast_df(config)
    connector_df = create_connector_df(actual_df, forecast_df, x_field, y_field, category_field)

    # Combine all data for plotting
    plot_df = pd.concat([actual_df, forecast_df, connector_df], ignore_index=True)

    # Build and display chart
    chart = build_chart(plot_df, config)
    st.altair_chart(chart, use_container_width=True)


__all__ = ['render_line_chart']
