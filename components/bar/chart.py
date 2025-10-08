"""Chart building for bar charts"""

import pandas as pd
import altair as alt


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
    
    return alt.Chart(df).mark_bar(color="#0b7dcfff").encode(
        x=alt.X(f"{config['x_field']}:{x_type}", title=config['x_label']),
        y=alt.Y(f"{config['y_field']}:Q", title=config['y_label'], axis=alt.Axis(format=",.0f")),
        tooltip=[
            alt.Tooltip(f"{config['x_field']}:{x_type}", title=config['x_label']),
            alt.Tooltip(f"{config['y_field']}:Q", title=config['y_label'], format=","),
        ]
    ).properties(height=340)


def _build_multi_bar(df: pd.DataFrame, config: dict) -> alt.Chart:
    """Multi-bar chart without forecast."""
    category_label = config.get('category_label', config.get('category_field', ''))
    x_type = _get_x_encoding_type(df, config['x_field'])
    
    return alt.Chart(df).mark_bar().encode(
        x=alt.X(f"{config['x_field']}:{x_type}", title=config['x_label']),
        y=alt.Y(f"{config['y_field']}:Q", title=config['y_label'], axis=alt.Axis(format=",.0f")),
        color=alt.Color(f"{config['category_field']}:N", legend=alt.Legend(title=category_label)),
        tooltip=[
            alt.Tooltip(f"{config['x_field']}:{x_type}", title=config['x_label']),
            alt.Tooltip(f"{config['y_field']}:Q", title=config['y_label'], format=","),
            alt.Tooltip(f"{config['category_field']}:N", title=category_label),
        ]
    ).properties(height=340)


def _build_single_forecast(df: pd.DataFrame, config: dict) -> alt.Chart:
    """Single bar chart with forecast."""
    x_type = _get_x_encoding_type(df, config['x_field'])
    base = alt.Chart(df)
    
    actual = base.transform_filter(alt.datum.type == "Actual").mark_bar(color="#0b7dcfff").encode(
        x=alt.X(f"{config['x_field']}:{x_type}", title=config['x_label']),
        y=alt.Y(f"{config['y_field']}:Q", title=config['y_label'], axis=alt.Axis(format=",.0f")),
        tooltip=[
            alt.Tooltip(f"{config['x_field']}:{x_type}", title=config['x_label']),
            alt.Tooltip(f"{config['y_field']}:Q", title=config['y_label'], format=","),
            alt.Tooltip("type:N", title="Type"),
        ]
    )
    
    forecast = base.transform_filter(alt.datum.type == "Forecast").mark_bar(color="#0b7dcfff", opacity=0.5).encode(
        x=alt.X(f"{config['x_field']}:{x_type}", title=config['x_label']),
        y=alt.Y(f"{config['y_field']}:Q", title=config['y_label'], axis=alt.Axis(format=",.0f")),
        tooltip=[
            alt.Tooltip(f"{config['x_field']}:{x_type}", title=config['x_label']),
            alt.Tooltip(f"{config['y_field']}:Q", title=config['y_label'], format=","),
            alt.Tooltip("type:N", title="Type"),
        ]
    )
    
    return (actual + forecast).properties(height=340)


def _build_multi_forecast(df: pd.DataFrame, config: dict) -> alt.Chart:
    """Multi-bar chart with forecast."""
    category_label = config.get('category_label', config.get('category_field', ''))
    x_type = _get_x_encoding_type(df, config['x_field'])
    base = alt.Chart(df)
    
    actual = base.transform_filter(alt.datum.type == "Actual").mark_bar().encode(
        x=alt.X(f"{config['x_field']}:{x_type}", title=config['x_label']),
        y=alt.Y(f"{config['y_field']}:Q", title=config['y_label'], axis=alt.Axis(format=",.0f")),
        color=alt.Color(
            f"{config['category_field']}:N",
            scale=alt.Scale(scheme="redyellowblue"),
            legend=alt.Legend(title=category_label)
        ),
        tooltip=[
            alt.Tooltip(f"{config['x_field']}:{x_type}", title=config['x_label']),
            alt.Tooltip(f"{config['y_field']}:Q", title=config['y_label'], format=","),
            alt.Tooltip(f"{config['category_field']}:N", title=category_label),
            alt.Tooltip("type:N", title="Type"),
        ]
    )
    
    forecast = base.transform_filter(alt.datum.type == "Forecast").mark_bar(opacity=0.5).encode(
        x=alt.X(f"{config['x_field']}:{x_type}", title=config['x_label']),
        y=alt.Y(f"{config['y_field']}:Q", title=config['y_label'], axis=alt.Axis(format=",.0f")),
        color=alt.Color(
            f"{config['category_field']}:N",
            legend=None
        ),
        tooltip=[
            alt.Tooltip(f"{config['x_field']}:{x_type}", title=config['x_label']),
            alt.Tooltip(f"{config['y_field']}:Q", title=config['y_label'], format=","),
            alt.Tooltip(f"{config['category_field']}:N", title=category_label),
            alt.Tooltip("type:N", title="Type"),
        ]
    )
    
    return (actual + forecast).properties(height=340)
