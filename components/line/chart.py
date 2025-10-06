"""Chart building for line charts"""

from typing import Optional
import pandas as pd
import altair as alt

from .data import should_show_points


def build_chart(plot_df: pd.DataFrame, connector_df: pd.DataFrame, config: dict) -> alt.Chart:
    """Build Altair chart based on configuration."""
    
    # Determine if we should show points
    if config.get('forecast', False) and "type" in plot_df.columns:
        actual_data = plot_df[plot_df["type"] == "Actual"]
        show_points = should_show_points(actual_data, config.get('category_field'))
    else:
        show_points = should_show_points(plot_df, config.get('category_field'))
    
    # Build chart based on configuration
    has_forecast = config.get('forecast', False) and "type" in plot_df.columns
    has_categories = config.get('category_field') is not None
    
    if has_forecast and has_categories:
        return _build_multi_forecast(plot_df, connector_df, config, show_points)
    elif has_forecast:
        return _build_single_forecast(plot_df, connector_df, config, show_points)
    elif has_categories:
        return _build_multi_line(plot_df, config, show_points)
    else:
        return _build_single_line(plot_df, config, show_points)


def _build_single_line(df: pd.DataFrame, config: dict, show_points: bool) -> alt.Chart:
    """Single line chart without forecast."""
    return alt.Chart(df).mark_line(point=show_points, color="#0b7dcfff").encode(
        x=alt.X(f"{config['x_field']}:T", title=config['x_label']),
        y=alt.Y(f"{config['y_field']}:Q", title=config['y_label'], axis=alt.Axis(format=",.0f")),
        tooltip=[
            alt.Tooltip(f"{config['x_field']}:T", title=config['x_label']),
            alt.Tooltip(f"{config['y_field']}:Q", title=config['y_label'], format=","),
        ],
    ).properties(height=340)


def _build_multi_line(df: pd.DataFrame, config: dict, show_points: bool) -> alt.Chart:
    """Multi-line chart without forecast."""
    category_label = config.get('category_label') or config['category_field']
    
    return alt.Chart(df).mark_line(point=show_points).encode(
        x=alt.X(f"{config['x_field']}:T", title=config['x_label']),
        y=alt.Y(f"{config['y_field']}:Q", title=config['y_label'], axis=alt.Axis(format=",.0f")),
        color=alt.Color(f"{config['category_field']}:N", legend=alt.Legend(title=category_label)),
        tooltip=[
            alt.Tooltip(f"{config['x_field']}:T", title=config['x_label']),
            alt.Tooltip(f"{config['y_field']}:Q", title=config['y_label'], format=","),
            alt.Tooltip(f"{config['category_field']}:N", title=category_label),
        ],
    ).properties(height=340)


def _build_single_forecast(
    df: pd.DataFrame, 
    connector_df: pd.DataFrame, 
    config: dict, 
    show_points: bool
) -> alt.Chart:
    """Single line chart with forecast."""
    base = alt.Chart(df)
    
    # Actual line (solid)
    actual = base.transform_filter(alt.datum.type == "Actual").mark_line(
        point=show_points, color="#0b7dcfff"
    ).encode(
        x=alt.X(f"{config['x_field']}:T", title=config['x_label']),
        y=alt.Y(f"{config['y_field']}:Q", title=config['y_label'], axis=alt.Axis(format=",.0f")),
        tooltip=[
            alt.Tooltip(f"{config['x_field']}:T", title=config['x_label']),
            alt.Tooltip(f"{config['y_field']}:Q", title=config['y_label'], format=","),
            alt.Tooltip("type:N", title="Type"),
        ],
    )
    
    # Forecast line (dashed)
    forecast = base.transform_filter(alt.datum.type == "Forecast").mark_line(
        point=show_points, color="#0b7dcfff", strokeDash=[5, 5]
    ).encode(
        x=alt.X(f"{config['x_field']}:T", title=config['x_label']),
        y=alt.Y(f"{config['y_field']}:Q", title=config['y_label'], axis=alt.Axis(format=",.0f")),
        tooltip=[
            alt.Tooltip(f"{config['x_field']}:T", title=config['x_label']),
            alt.Tooltip(f"{config['y_field']}:Q", title=config['y_label'], format=","),
            alt.Tooltip("type:N", title="Type"),
        ],
    )
    
    chart = actual + forecast
    
    # Add connector if present
    if not connector_df.empty:
        connector = alt.Chart(connector_df).mark_line(
            point=False, color="#0b7dcfff", strokeDash=[5, 5]
        ).encode(
            x=alt.X(f"{config['x_field']}:T"),
            y=alt.Y(f"{config['y_field']}:Q"),
        )
        chart = chart + connector
    
    return chart.properties(height=340)


def _build_multi_forecast(
    df: pd.DataFrame, 
    connector_df: pd.DataFrame, 
    config: dict, 
    show_points: bool
) -> alt.Chart:
    """Multi-line chart with forecast."""
    category_label = config.get('category_label') or config['category_field']
    base = alt.Chart(df)
    
    # Actual lines (solid, color-coded)
    actual = base.transform_filter(alt.datum.type == "Actual").mark_line(point=show_points).encode(
        x=alt.X(f"{config['x_field']}:T", title=config['x_label']),
        y=alt.Y(f"{config['y_field']}:Q", title=config['y_label'], axis=alt.Axis(format=",.0f")),
        color=alt.Color(f"{config['category_field']}:N", legend=alt.Legend(title=category_label)),
        tooltip=[
            alt.Tooltip(f"{config['x_field']}:T", title=config['x_label']),
            alt.Tooltip(f"{config['y_field']}:Q", title=config['y_label'], format=","),
            alt.Tooltip(f"{config['category_field']}:N", title=category_label),
            alt.Tooltip("type:N", title="Type"),
        ],
    )
    
    # Forecast lines (dashed, color-coded)
    forecast = base.transform_filter(alt.datum.type == "Forecast").mark_line(
        point=show_points, strokeDash=[5, 5]
    ).encode(
        x=alt.X(f"{config['x_field']}:T", title=config['x_label']),
        y=alt.Y(f"{config['y_field']}:Q", title=config['y_label'], axis=alt.Axis(format=",.0f")),
        color=alt.Color(f"{config['category_field']}:N", legend=alt.Legend(title=category_label)),
        tooltip=[
            alt.Tooltip(f"{config['x_field']}:T", title=config['x_label']),
            alt.Tooltip(f"{config['y_field']}:Q", title=config['y_label'], format=","),
            alt.Tooltip(f"{config['category_field']}:N", title=category_label),
            alt.Tooltip("type:N", title="Type"),
        ],
    )
    
    chart = actual + forecast
    
    # Add connectors if present
    if not connector_df.empty:
        connector = alt.Chart(connector_df).mark_line(point=False, strokeDash=[5, 5]).encode(
            x=alt.X(f"{config['x_field']}:T"),
            y=alt.Y(f"{config['y_field']}:Q"),
            color=alt.Color(f"{config['category_field']}:N", legend=alt.Legend(title=category_label)),
        )
        chart = chart + connector
    
    return chart.properties(height=340)

def get_category_label(config: dict) -> Optional[str]:
    """Get the display label for category field."""
    return config['category_label'] if config.get('category_field') else None


def get_base_encoding(config: dict) -> dict:
    """Get the basic x and y axis encodings used across chart types."""
    return {
        'x': alt.X(f"{config['x_field']}:T", title=config['x_label']),
        'y': alt.Y(f"{config['y_field']}:Q", title=config['y_label'], axis=alt.Axis(format=",.0f"))
    }


def get_tooltip_with_type(config: dict) -> list:
    """Get tooltip configuration for forecast charts (single-line)."""
    return [
        alt.Tooltip(f"{config['x_field']}:T", title=config['x_label']),
        alt.Tooltip(f"{config['y_field']}:Q", title=config['y_label'], format=","),
        alt.Tooltip("type:N", title="Type"),
    ]


def get_tooltip_with_type_and_category(config: dict, category_label: str) -> list:
    """Get tooltip configuration for forecast charts (multi-line)."""
    return [
        alt.Tooltip(f"{config['x_field']}:T", title=config['x_label']),
        alt.Tooltip(f"{config['y_field']}:Q", title=config['y_label'], format=","),
        alt.Tooltip(f"{config['category_field']}:N", title=category_label),
        alt.Tooltip("type:N", title="Type"),
    ]