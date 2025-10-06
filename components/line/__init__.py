"""Line chart component with Prophet-based forecasting capability"""

import streamlit as st
import pandas as pd

from .config import LineChartConfig, validate_config
from .data import ensure_datetime, prepare_actual_data
from .forecast import ForecastEngine
from .chart import ChartBuilder


def render_line_chart(config: dict) -> None:
    """
    Main entry point for rendering a line chart with optional forecasting.
    
    Args:
        config: Dictionary containing chart configuration (see LineChartConfig)
    """
    # Validate and normalize configuration
    validated_config = validate_config(config)
    
    # Display chart header
    st.subheader(validated_config.title)
    st.caption(validated_config.description)
    
    # Show forecast slider if forecasting is enabled
    forecast_periods = None
    if validated_config.forecast:
        base_key = id(config)
        forecast_periods = st.slider(
            "Forecast periods", 
            1, 
            12, 
            6, 
            key=f"slider_{base_key}"
        )
    
    # Ensure x-axis is datetime format
    df = ensure_datetime(validated_config.df, validated_config.x_field)
    
    # Prepare data based on whether forecasting is enabled
    if validated_config.forecast:
        plot_df, connector_df = _prepare_forecast_data(
            df, 
            validated_config, 
            forecast_periods
        )
    else:
        plot_df = prepare_actual_data(
            df, 
            validated_config.x_field, 
            validated_config.y_field, 
            validated_config.category_field, 
            with_type=False
        )
        connector_df = pd.DataFrame()
    
    # Build and display the chart
    builder = ChartBuilder(validated_config)
    chart = builder.build(plot_df, connector_df, validated_config.forecast)
    st.altair_chart(chart, use_container_width=True)


def _prepare_forecast_data(
    df: pd.DataFrame, 
    config: LineChartConfig, 
    forecast_periods: int
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Prepare data for forecast visualization by generating predictions."""
    from .data import create_connector_data
    
    # Prepare actual historical data
    actual_df = prepare_actual_data(
        df, 
        config.x_field, 
        config.y_field, 
        config.category_field, 
        with_type=True
    )
    
    # Need at least 2 data points to generate a forecast
    if len(df) < 2:
        return actual_df.copy(), pd.DataFrame()
    
    # Generate forecast data
    with st.spinner("Generating forecast..."):
        engine = ForecastEngine()
        forecast_df = engine.create_forecast_data(
            df,
            config.x_field,
            config.y_field,
            forecast_periods,
            config.category_field
        )
        
        # Create connecting lines between actual and forecast data
        connector_df = create_connector_data(
            actual_df, 
            forecast_df, 
            config.x_field, 
            config.y_field, 
            config.category_field
        )
    
    # Combine actual and forecast data
    if not forecast_df.empty:
        plot_df = pd.concat([actual_df, forecast_df], ignore_index=True)
    else:
        plot_df = actual_df.copy()
    
    return plot_df, connector_df


__all__ = ['render_line_chart']
