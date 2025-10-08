"""Line chart component with Prophet-based forecasting capability"""

import streamlit as st
import pandas as pd

from .chart import build_chart
from .forecast import create_forecast_df, create_connector_df, DEFAULT_FORECAST_PERIODS, FORECAST_OPTIONS


def _is_time_based(df: pd.DataFrame, x_field: str) -> bool:
    """Check if x-axis data is time-based (datetime or convertible to datetime)."""
    # Check if already datetime
    if pd.api.types.is_datetime64_any_dtype(df[x_field]):
        return True
    
    # Try to convert to datetime
    try:
        pd.to_datetime(df[x_field])
        return True
    except (ValueError, TypeError):
        return False


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
            - trendline (bool, optional): Whether to show a trendline for single line charts (default: False).
    """
    st.subheader(config['title'])
    st.caption(config['description'])

    # Generate unique key for this chart instance
    chart_key = f"line_chart_{id(config)}"
    forecast_enabled_key = f"{chart_key}_forecast_enabled"
    forecast_periods_key = f"{chart_key}_forecast_periods"
    
    # Check if x-axis is time-based for forecast capability
    is_time_series = _is_time_based(config['df'], config['x_field'])
    
    # Initialize session state for forecast enablement
    if forecast_enabled_key not in st.session_state:
        st.session_state[forecast_enabled_key] = config.get('forecast', False)

    # Only show forecast controls if time-based
    if is_time_series:
        if not st.session_state[forecast_enabled_key]:
            # Right-aligned discreet checkbox
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.checkbox("Forecast", key=f"{chart_key}_checkbox"):
                    st.session_state[forecast_enabled_key] = True
                    st.rerun()
        else:
            col1, col2 = st.columns([3, 1])
            with col2:
                forecast_periods = st.selectbox(
                    "Forecast periods",
                    options=FORECAST_OPTIONS,
                    index=FORECAST_OPTIONS.index(DEFAULT_FORECAST_PERIODS),
                    key=forecast_periods_key
                )
    
    actual_df = config['df'].copy()
    x_field = config['x_field']
    y_field = config['y_field']
    category_field = config.get('category_field')

    # Convert x-axis to datetime if needed (for forecasting or reference lines)
    if not pd.api.types.is_datetime64_any_dtype(actual_df[x_field]):
        try:
            actual_df[x_field] = pd.to_datetime(actual_df[x_field])
        except (ValueError, TypeError):
            pass  # Keep original type if conversion fails

    actual_df["type"] = "Actual"

    # Generate forecast if enabled and time-based
    forecast_df = pd.DataFrame()
    connector_df = pd.DataFrame()
    if is_time_series and st.session_state[forecast_enabled_key]:
        config['forecast'] = True
        periods = st.session_state.get(forecast_periods_key, DEFAULT_FORECAST_PERIODS)
        forecast_df = create_forecast_df(config, forecast_periods=periods)
        connector_df = create_connector_df(actual_df, forecast_df, x_field, y_field, category_field)

    # Combine all data for plotting
    plot_df = pd.concat([actual_df, forecast_df, connector_df], ignore_index=True)

    # Build and display chart
    chart = build_chart(plot_df, config)
    st.altair_chart(chart, use_container_width=True)


__all__ = ['render_line_chart']
