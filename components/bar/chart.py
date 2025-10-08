"""Chart building for bar charts"""

import pandas as pd
import altair as alt

# Bar chart styling
BAR_COLOR_SCHEME = "dark2"
BAR_SINGLE_COLOR = "#0b7dcfff"
BAR_FORECAST_OPACITY = 0.5

# Trendline styling
TRENDLINE_COLOR = "#FF6B6B"
TRENDLINE_DASH = [5, 5]
TRENDLINE_WIDTH = 3
TRENDLINE_OPACITY = 0.8

# Chart dimensions
CHART_HEIGHT = 340

# Tooltip formatting
TOOLTIP_NUMBER_FORMAT = ","
TOOLTIP_AXIS_FORMAT = ",.0f"


def _get_x_encoding_type(df: pd.DataFrame, x_field: str) -> str:
    """Determine the appropriate Altair encoding type for x-axis."""
    if pd.api.types.is_datetime64_any_dtype(df[x_field]):
        return "T"  # Temporal
    elif pd.api.types.is_numeric_dtype(df[x_field]):
        return "Q"  # Quantitative
    else:
        return "N"  # Nominal


def build_chart(plot_df: pd.DataFrame, config: dict) -> alt.Chart:
    """Build Altair bar chart based on configuration."""
    has_forecast = config.get('forecast', False) and "type" in plot_df.columns
    has_categories = config.get('category_field') is not None
    
    if has_forecast and has_categories:
        return _build_multi_forecast(plot_df, config)
    elif has_forecast:
        return _build_single_forecast(plot_df, config)
    elif has_categories:
        return _build_multi_bar(plot_df, config)
    else:
        return _build_single_bar(plot_df, config)


def _build_single_bar(df: pd.DataFrame, config: dict) -> alt.Chart:
    """Single bar chart without forecast."""
    x_type = _get_x_encoding_type(df, config['x_field'])
    
    bars = alt.Chart(df).mark_bar(color=BAR_SINGLE_COLOR).encode(
        x=alt.X(f"{config['x_field']}:{x_type}", title=config['x_label']),
        y=alt.Y(f"{config['y_field']}:Q", title=config['y_label'], axis=alt.Axis(format=TOOLTIP_AXIS_FORMAT)),
        tooltip=[
            alt.Tooltip(f"{config['x_field']}:{x_type}", title=config['x_label']),
            alt.Tooltip(f"{config['y_field']}:Q", title=config['y_label'], format=TOOLTIP_NUMBER_FORMAT),
        ]
    )
    
    chart = bars
    
    # Add trendline if requested
    if config.get('trendline', False):
        trendline = _create_trendline(df, config, x_type)
        chart = bars + trendline
    
    return chart.properties(height=CHART_HEIGHT)


def _create_trendline(df: pd.DataFrame, config: dict, x_type: str) -> alt.Chart:
    """Create a trendline layer using linear regression."""
    import numpy as np
    
    # Prepare data for regression
    df_sorted = df.sort_values(by=config['x_field']).reset_index(drop=True)
    x_numeric = np.arange(len(df_sorted))
    y_values = df_sorted[config['y_field']].values
    
    # Calculate linear regression
    coefficients = np.polyfit(x_numeric, y_values, 1)
    slope, intercept = coefficients[0], coefficients[1]
    
    # Create trendline points at start and end
    trendline_data = pd.DataFrame({
        config['x_field']: [df_sorted[config['x_field']].iloc[0], df_sorted[config['x_field']].iloc[-1]],
        config['y_field']: [intercept, slope * (len(df_sorted) - 1) + intercept]
    })
    
    return alt.Chart(trendline_data).mark_line(
        color=TRENDLINE_COLOR,
        strokeDash=TRENDLINE_DASH,
        size=TRENDLINE_WIDTH,
        opacity=TRENDLINE_OPACITY
    ).encode(
        x=alt.X(f"{config['x_field']}:{x_type}"),
        y=alt.Y(f"{config['y_field']}:Q")
    )


def _build_multi_bar(df: pd.DataFrame, config: dict) -> alt.Chart:
    """Multi-bar chart without forecast."""
    category_label = config.get('category_label', config.get('category_field', ''))
    x_type = _get_x_encoding_type(df, config['x_field'])
    
    return alt.Chart(df).mark_bar().encode(
        x=alt.X(f"{config['x_field']}:{x_type}", title=config['x_label']),
        y=alt.Y(f"{config['y_field']}:Q", title=config['y_label'], axis=alt.Axis(format=TOOLTIP_AXIS_FORMAT)),
        color=alt.Color(
            f"{config['category_field']}:N",
            scale=alt.Scale(scheme=BAR_COLOR_SCHEME),
            legend=alt.Legend(title=category_label)
        ),
        tooltip=[
            alt.Tooltip(f"{config['x_field']}:{x_type}", title=config['x_label']),
            alt.Tooltip(f"{config['y_field']}:Q", title=config['y_label'], format=TOOLTIP_NUMBER_FORMAT),
            alt.Tooltip(f"{config['category_field']}:N", title=category_label),
        ]
    ).properties(height=CHART_HEIGHT)


def _build_single_forecast(df: pd.DataFrame, config: dict) -> alt.Chart:
    """Single bar chart with forecast."""
    x_type = _get_x_encoding_type(df, config['x_field'])
    base = alt.Chart(df)
    
    actual = base.transform_filter(alt.datum.type == "Actual").mark_bar(color=BAR_SINGLE_COLOR).encode(
        x=alt.X(f"{config['x_field']}:{x_type}", title=config['x_label']),
        y=alt.Y(f"{config['y_field']}:Q", title=config['y_label'], axis=alt.Axis(format=TOOLTIP_AXIS_FORMAT)),
        tooltip=[
            alt.Tooltip(f"{config['x_field']}:{x_type}", title=config['x_label']),
            alt.Tooltip(f"{config['y_field']}:Q", title=config['y_label'], format=TOOLTIP_NUMBER_FORMAT),
            alt.Tooltip("type:N", title="Type"),
        ]
    )
    
    forecast = base.transform_filter(alt.datum.type == "Forecast").mark_bar(color=BAR_SINGLE_COLOR, opacity=BAR_FORECAST_OPACITY).encode(
        x=alt.X(f"{config['x_field']}:{x_type}", title=config['x_label']),
        y=alt.Y(f"{config['y_field']}:Q", title=config['y_label'], axis=alt.Axis(format=TOOLTIP_AXIS_FORMAT)),
        tooltip=[
            alt.Tooltip(f"{config['x_field']}:{x_type}", title=config['x_label']),
            alt.Tooltip(f"{config['y_field']}:Q", title=config['y_label'], format=TOOLTIP_NUMBER_FORMAT),
            alt.Tooltip("type:N", title="Type"),
        ]
    )
    
    return (actual + forecast).properties(height=CHART_HEIGHT)


def _build_multi_forecast(df: pd.DataFrame, config: dict) -> alt.Chart:
    """Multi-bar chart with forecast."""
    category_label = config.get('category_label', config.get('category_field', ''))
    x_type = _get_x_encoding_type(df, config['x_field'])
    base = alt.Chart(df)
    
    actual = base.transform_filter(alt.datum.type == "Actual").mark_bar().encode(
        x=alt.X(f"{config['x_field']}:{x_type}", title=config['x_label']),
        y=alt.Y(f"{config['y_field']}:Q", title=config['y_label'], axis=alt.Axis(format=TOOLTIP_AXIS_FORMAT)),
        color=alt.Color(
            f"{config['category_field']}:N",
            scale=alt.Scale(scheme=BAR_COLOR_SCHEME),
            legend=alt.Legend(title=category_label)
        ),
        tooltip=[
            alt.Tooltip(f"{config['x_field']}:{x_type}", title=config['x_label']),
            alt.Tooltip(f"{config['y_field']}:Q", title=config['y_label'], format=TOOLTIP_NUMBER_FORMAT),
            alt.Tooltip(f"{config['category_field']}:N", title=category_label),
            alt.Tooltip("type:N", title="Type"),
        ]
    )
    
    forecast = base.transform_filter(alt.datum.type == "Forecast").mark_bar(opacity=BAR_FORECAST_OPACITY).encode(
        x=alt.X(f"{config['x_field']}:{x_type}", title=config['x_label']),
        y=alt.Y(f"{config['y_field']}:Q", title=config['y_label'], axis=alt.Axis(format=TOOLTIP_AXIS_FORMAT)),
        color=alt.Color(
            f"{config['category_field']}:N",
            scale=alt.Scale(scheme=BAR_COLOR_SCHEME),
            legend=None
        ),
        tooltip=[
            alt.Tooltip(f"{config['x_field']}:{x_type}", title=config['x_label']),
            alt.Tooltip(f"{config['y_field']}:Q", title=config['y_label'], format=TOOLTIP_NUMBER_FORMAT),
            alt.Tooltip(f"{config['category_field']}:N", title=category_label),
            alt.Tooltip("type:N", title="Type"),
        ]
    )
    
    return (actual + forecast).properties(height=CHART_HEIGHT)
