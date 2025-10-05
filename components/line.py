"""Line chart component with Prophet-based forecasting capability"""

import streamlit as st
import altair as alt
import pandas as pd
from utils.forecasting.engine import infer_frequency
from utils.forecasting.data_preparation import (
    prepare_actual_data,
    create_forecast_data,
    create_connector_data
)
from utils.chart_helpers import (
    should_show_points,
    ensure_datetime,
    get_category_label,
    get_base_encoding,
    get_tooltip_with_type,
    get_tooltip_with_type_and_category,
)


# ============================================================================
# MAIN RENDERING FUNCTION
# ============================================================================

def render_line_chart(config):
    """
    Main entry point for rendering a line chart with optional forecasting.
    
    Args:
        config: Dictionary containing chart configuration:
            - title: Chart title
            - description: Chart description
            - df: Source DataFrame
            - x_field: Name of the date/time column
            - y_field: Name of the value column
            - category_field: Optional column for multi-line charts
            - forecast: Boolean to enable/disable forecasting
            - x_label: Label for x-axis
            - y_label: Label for y-axis
    """
    # Display chart header
    st.subheader(config['title'])
    st.caption(config['description'])
    
    # Extract configuration
    df = config['df'].copy()
    x_field = config['x_field']
    y_field = config['y_field']
    category_field = config.get('category_field', None)
    enable_forecast = config.get('forecast', False)

    # Show forecast slider if forecasting is enabled
    if enable_forecast:
        forecast_periods = _render_forecast_slider(config)
    else:
        forecast_periods = None

    # Ensure x-axis is datetime format
    df = ensure_datetime(df, x_field)

    # Prepare data based on whether forecasting is enabled
    if enable_forecast:
        plot_df, connector_df = _prepare_forecast_data(
            df, x_field, y_field, category_field, forecast_periods
        )
    else:
        plot_df = prepare_actual_data(df, x_field, y_field, category_field, with_type=False)
        connector_df = pd.DataFrame()

    # Build and display the chart
    chart = _build_line_chart(
        plot_df, connector_df, config, x_field, y_field, category_field, enable_forecast
    )
    st.altair_chart(chart, use_container_width=True)


# ============================================================================
# DATA PREPARATION HELPERS
# ============================================================================

def _render_forecast_slider(config):
    """
    Render the forecast period slider for forecast-enabled charts.
    
    Returns:
        int: Number of periods to forecast
    """
    base_key = id(config)
    return st.slider("Forecast periods", 1, 12, 6, key=f"slider_{base_key}")


def _prepare_forecast_data(df, x_field, y_field, category_field, forecast_periods):
    """
    Prepare data for forecast visualization by generating predictions.
    
    Args:
        df: Source DataFrame
        x_field: Date/time column name
        y_field: Value column name
        category_field: Optional category column for multi-line charts
        forecast_periods: Number of periods to forecast
        
    Returns:
        tuple: (plot_df, connector_df) - Combined data and connector lines
    """
    # Prepare actual historical data
    actual_df = prepare_actual_data(df, x_field, y_field, category_field, with_type=True)
    
    # Need at least 2 data points to generate a forecast
    if len(df) < 2:
        return actual_df.copy(), pd.DataFrame()
    
    # Generate forecast data
    with st.spinner("Generating forecast..."):
        forecast_df = _generate_forecast(
            df, x_field, y_field, category_field, forecast_periods
        )
        
        # Create connecting lines between actual and forecast data
        connector_df = create_connector_data(
            actual_df, forecast_df, x_field, y_field, category_field
        )
    
    # Combine actual and forecast data
    if not forecast_df.empty:
        plot_df = pd.concat([actual_df, forecast_df], ignore_index=True)
    else:
        plot_df = actual_df.copy()
    
    return plot_df, connector_df


def _generate_forecast(df, x_field, y_field, category_field, forecast_periods):
    """
    Generate forecast data using Prophet.
    
    For single-line charts, infers frequency from data.
    For multi-line charts, handles each category separately.
    
    Returns:
        DataFrame: Forecast predictions
    """
    if category_field is None:
        # Single line: infer time frequency (daily, weekly, monthly, etc.)
        freq = infer_frequency(df, x_field)
        return create_forecast_data(df, x_field, y_field, forecast_periods, freq, category_field)
    else:
        # Multi-line: let forecasting engine handle per-category frequency
        return create_forecast_data(df, x_field, y_field, forecast_periods, None, category_field)


# ============================================================================
# CHART BUILDING ORCHESTRATION
# ============================================================================

def _build_line_chart(
    plot_df: pd.DataFrame,
    connector_df: pd.DataFrame,
    config: dict,
    x_field: str,
    y_field: str,
    category_field: str,
    enable_forecast: bool
) -> alt.Chart:
    """
    Build the appropriate Altair chart based on configuration.
    
    Chooses between 4 chart types:
    1. Single line without forecast
    2. Multi-line without forecast
    3. Single line with forecast
    4. Multi-line with forecast
    """
    # Determine whether to show individual points on lines
    if enable_forecast:
        actual_data = plot_df[plot_df["type"] == "Actual"]
        show_points = should_show_points(actual_data, category_field)
    else:
        show_points = should_show_points(plot_df, category_field)

    # Check if this is a multi-line chart
    is_multi_line = category_field is not None
    
    # Build the appropriate chart type
    if enable_forecast:
        if is_multi_line:
            return _build_multi_line_forecast_chart(
                plot_df, connector_df, x_field, y_field, category_field, config, show_points
            )
        else:
            return _build_single_line_forecast_chart(
                plot_df, connector_df, x_field, y_field, config, show_points
            )
    else:
        if is_multi_line:
            return _build_multi_line_chart(
                plot_df, x_field, y_field, category_field, config, show_points
            )
        else:
            return _build_single_line_chart(
                plot_df, x_field, y_field, config, show_points
            )


# ============================================================================
# CHART BUILDERS - NO FORECAST
# ============================================================================

def _build_single_line_chart(plot_df, x_field, y_field, config, show_points):
    """Build a simple single-line chart without forecasting."""
    base_color = "#0b7dcfff"  # Brand blue color
    
    return alt.Chart(plot_df).mark_line(point=show_points, color=base_color).encode(
        x=alt.X(f"{x_field}:T", title=config['x_label']),
        y=alt.Y(f"{y_field}:Q", title=config['y_label'], axis=alt.Axis(format=",.0f")),
        tooltip=[
            alt.Tooltip(f"{x_field}:T", title=config['x_label']),
            alt.Tooltip(f"{y_field}:Q", title=config['y_label'], format=","),
        ],
    ).properties(height=340)


def _build_multi_line_chart(plot_df, x_field, y_field, category_field, config, show_points):
    """Build a multi-line chart (one line per category) without forecasting."""
    category_label = get_category_label(config, category_field)
    
    return alt.Chart(plot_df).mark_line(point=show_points).encode(
        x=alt.X(f"{x_field}:T", title=config['x_label']),
        y=alt.Y(f"{y_field}:Q", title=config['y_label'], axis=alt.Axis(format=",.0f")),
        color=alt.Color(f"{category_field}:N", legend=alt.Legend(title=category_label)),
        tooltip=[
            alt.Tooltip(f"{x_field}:T", title=config['x_label']),
            alt.Tooltip(f"{y_field}:Q", title=config['y_label'], format=","),
            alt.Tooltip(f"{category_field}:N", title=category_label),
        ],
    ).properties(height=340)


# ============================================================================
# CHART BUILDERS - WITH FORECAST
# ============================================================================

def _build_single_line_forecast_chart(plot_df, connector_df, x_field, y_field, config, show_points):
    """
    Build a single-line chart with forecasting.
    
    Shows:
    - Solid line for actual historical data
    - Dashed line for forecast predictions
    - Connector line between them (if available)
    """
    base_color = "#0b7dcfff"
    base = alt.Chart(plot_df)
    
    # Create the actual data line (solid)
    actual_line = base.transform_filter(
        alt.datum.type == "Actual"
    ).mark_line(point=show_points, color=base_color).encode(
        **get_base_encoding(x_field, y_field, config),
        tooltip=get_tooltip_with_type(x_field, y_field, config)
    )

    # Create the forecast line (dashed)
    forecast_line = base.transform_filter(
        alt.datum.type == "Forecast"
    ).mark_line(point=show_points, color=base_color, strokeDash=[5, 5]).encode(
        **get_base_encoding(x_field, y_field, config),
        tooltip=get_tooltip_with_type(x_field, y_field, config)
    )

    # Combine layers
    chart = actual_line + forecast_line
    
    # Add connector line if available (smooth transition between actual and forecast)
    if not connector_df.empty:
        connector_chart = alt.Chart(connector_df).mark_line(
            point=False, color=base_color, strokeDash=[5, 5]
        ).encode(
            x=alt.X(f"{x_field}:T"),
            y=alt.Y(f"{y_field}:Q"),
        )
        chart = chart + connector_chart
    
    return chart.properties(height=340)


def _build_multi_line_forecast_chart(plot_df, connector_df, x_field, y_field, category_field, config, show_points):
    """
    Build a multi-line chart with forecasting.
    
    Each category gets:
    - Its own color
    - Solid line for actual data
    - Dashed line for forecast
    - Connector line between them
    """
    category_label = get_category_label(config, category_field)
    base = alt.Chart(plot_df)
    
    # Create the actual data lines (solid, color-coded by category)
    actual_line = base.transform_filter(
        alt.datum.type == "Actual"
    ).mark_line(point=show_points).encode(
        **get_base_encoding(x_field, y_field, config),
        color=alt.Color(f"{category_field}:N", legend=alt.Legend(title=category_label)),
        tooltip=get_tooltip_with_type_and_category(x_field, y_field, category_field, category_label, config)
    )
    
    # Create the forecast lines (dashed, color-coded by category)
    forecast_line = base.transform_filter(
        alt.datum.type == "Forecast"
    ).mark_line(point=show_points, strokeDash=[5, 5]).encode(
        **get_base_encoding(x_field, y_field, config),
        color=alt.Color(f"{category_field}:N", legend=alt.Legend(title=category_label)),
        tooltip=get_tooltip_with_type_and_category(x_field, y_field, category_field, category_label, config)
    )
    
    # Combine layers
    chart = actual_line + forecast_line
    
    # Add connector lines if available
    if not connector_df.empty:
        connector_chart = alt.Chart(connector_df).mark_line(
            point=False, strokeDash=[5, 5]
        ).encode(
            x=alt.X(f"{x_field}:T"),
            y=alt.Y(f"{y_field}:Q"),
            color=alt.Color(f"{category_field}:N", legend=alt.Legend(title=category_label)),
        )
        chart = chart + connector_chart
    
    return chart.properties(height=340)