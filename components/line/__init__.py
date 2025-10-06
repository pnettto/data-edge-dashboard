"""Line chart component with Prophet-based forecasting capability"""

import streamlit as st
import pandas as pd

from .forecast import generate_forecast
from .chart import build_chart
from .helpers import create_connectors


def render_line_chart(config: dict) -> None:
    """
    Main entry point for rendering a line chart with optional forecasting.
    
    Args:
        config: Dictionary containing chart configuration
    """
    st.subheader(config['title'])
    st.caption(config['description'])
    
    # Convert x-axis to datetime
    df = config['df'].copy()
    x_field = config['x_field']
    if not pd.api.types.is_datetime64_any_dtype(df[x_field]):
        df[x_field] = pd.to_datetime(df[x_field])
    
    # Handle forecasting
    forecast_periods = None
    if config.get('forecast', False):
        forecast_periods = st.slider("Forecast periods", 1, 12, 6, key=f"slider_{id(config)}")
    
    # Prepare data
    if config.get('forecast', False) and len(df) >= 2:
        # Add type column to actual data
        df["type"] = "Actual"
        
        # Generate forecast
        with st.spinner("Generating forecast..."):
            forecast_df = generate_forecast(
                df, x_field, config['y_field'], forecast_periods, config.get('category_field')
            )
        
        # Create connectors and combine
        if not forecast_df.empty:
            connector_df = create_connectors(
                df, forecast_df, x_field, config['y_field'], config.get('category_field')
            )
            plot_df = pd.concat([df, forecast_df], ignore_index=True)
        else:
            connector_df = pd.DataFrame()
            plot_df = df
    else:
        plot_df = df
        connector_df = pd.DataFrame()
    
    # Build and display chart
    chart = build_chart(plot_df, connector_df, config)
    st.altair_chart(chart, use_container_width=True)


__all__ = ['render_line_chart']
