"""Bar chart component for displaying categorical data"""

import streamlit as st
import altair as alt
from utils.chart_helpers import get_category_label


# ============================================================================
# MAIN RENDERING FUNCTION
# ============================================================================

def render_bar_chart(config):
    """
    Main entry point for rendering a bar chart.
    
    Args:
        config: Dictionary containing chart configuration:
            - title: Chart title
            - description: Chart description
            - df: Source DataFrame
            - x_field: Category column name
            - y_field: Value column name
            - category_field: Optional column for grouped/stacked bars
            - x_label: Label for x-axis
            - y_label: Label for y-axis
            - stacked: Boolean for stacked vs grouped bars (default: False)
    """
    # Display chart header
    st.subheader(config['title'])
    st.caption(config['description'])
    
    # Extract configuration
    df = config['df']
    x_field = config['x_field']
    y_field = config['y_field']
    category_field = config.get('category_field', None)
    is_stacked = config.get('stacked', False)
    
    # Build and display the chart
    chart = _build_bar_chart(df, x_field, y_field, category_field, config, is_stacked)
    st.altair_chart(chart, use_container_width=True)


# ============================================================================
# CHART BUILDING
# ============================================================================

def _build_bar_chart(df, x_field, y_field, category_field, config, is_stacked):
    """
    Build the appropriate bar chart based on configuration.
    
    Chooses between:
    1. Simple bar chart (no categories)
    2. Grouped bar chart (categories side-by-side)
    3. Stacked bar chart (categories stacked)
    """
    if category_field is None:
        return _build_simple_bar_chart(df, x_field, y_field, config)
    elif is_stacked:
        return _build_stacked_bar_chart(df, x_field, y_field, category_field, config)
    else:
        return _build_grouped_bar_chart(df, x_field, y_field, category_field, config)


def _build_simple_bar_chart(df, x_field, y_field, config):
    """Build a simple bar chart with a single color."""
    base_color = "#0b7dcfff"
    
    return alt.Chart(df).mark_bar(color=base_color).encode(
        x=alt.X(f"{x_field}:N", title=config['x_label']),
        y=alt.Y(f"{y_field}:Q", title=config['y_label'], axis=alt.Axis(format=",.0f")),
        tooltip=[
            alt.Tooltip(f"{x_field}:N", title=config['x_label']),
            alt.Tooltip(f"{y_field}:Q", title=config['y_label'], format=","),
        ],
    ).properties(height=340)


def _build_grouped_bar_chart(df, x_field, y_field, category_field, config):
    """Build a grouped bar chart with categories displayed side-by-side."""
    category_label = get_category_label(config, category_field)
    
    return alt.Chart(df).mark_bar().encode(
        x=alt.X(f"{x_field}:N", title=config['x_label']),
        y=alt.Y(f"{y_field}:Q", title=config['y_label'], axis=alt.Axis(format=",.0f")),
        color=alt.Color(f"{category_field}:N", legend=alt.Legend(title=category_label)),
        xOffset=f"{category_field}:N",  # Side-by-side positioning
        tooltip=[
            alt.Tooltip(f"{x_field}:N", title=config['x_label']),
            alt.Tooltip(f"{y_field}:Q", title=config['y_label'], format=","),
            alt.Tooltip(f"{category_field}:N", title=category_label),
        ],
    ).properties(height=340)


def _build_stacked_bar_chart(df, x_field, y_field, category_field, config):
    """Build a stacked bar chart with categories stacked on top of each other."""
    category_label = get_category_label(config, category_field)
    
    return alt.Chart(df).mark_bar().encode(
        x=alt.X(f"{x_field}:N", title=config['x_label']),
        y=alt.Y(f"{y_field}:Q", title=config['y_label'], axis=alt.Axis(format=",.0f")),
        color=alt.Color(f"{category_field}:N", legend=alt.Legend(title=category_label)),
        tooltip=[
            alt.Tooltip(f"{x_field}:N", title=config['x_label']),
            alt.Tooltip(f"{y_field}:Q", title=config['y_label'], format=","),
            alt.Tooltip(f"{category_field}:N", title=category_label),
        ],
    ).properties(height=340)
def _build_multi_category_chart(base, x_field, y_field, category_field, category_label, config):
    """Build multi-category grouped bar chart without forecast."""
    return base.mark_bar(size=20).encode(
        x=alt.X(f"{x_field}:T", title=config['x_label']),
        y=alt.Y(f"{y_field}:Q", title=config['y_label'], axis=alt.Axis(format=",.0f")),
        color=alt.Color(f"{category_field}:N", legend=alt.Legend(title=category_label)),
        xOffset=f"{category_field}:N",
        tooltip=[
            alt.Tooltip(f"{x_field}:T", title=config['x_label']),
            alt.Tooltip(f"{y_field}:Q", title=config['y_label'], format=","),
            alt.Tooltip(f"{category_field}:N", title=category_label),
        ],
    ).properties(height=340)


def _build_single_category_forecast_chart(base, x_field, y_field, config, base_color, forecast_color):
    """Build single category bar chart with forecast."""
    actual_bars = base.transform_filter(
        alt.datum.type == "Actual"
    ).mark_bar(color=base_color, size=30).encode(
        x=alt.X(f"{x_field}:T", title=config['x_label']),
        y=alt.Y(f"{y_field}:Q", title=config['y_label'], axis=alt.Axis(format=",.0f")),
        tooltip=[
            alt.Tooltip(f"{x_field}:T", title=config['x_label']),
            alt.Tooltip(f"{y_field}:Q", title=config['y_label'], format=","),
            alt.Tooltip("type:N", title="Type"),
        ],
    )

    forecast_bars = base.transform_filter(
        alt.datum.type == "Forecast"
    ).mark_bar(
        color=forecast_color, 
        opacity=0.6,
        stroke=base_color,
        strokeWidth=2,
        strokeDash=[5, 5],
        size=30
    ).encode(
        x=alt.X(f"{x_field}:T", title=config['x_label']),
        y=alt.Y(f"{y_field}:Q", title=config['y_label'], axis=alt.Axis(format=",.0f")),
        tooltip=[
            alt.Tooltip(f"{x_field}:T", title=config['x_label']),
            alt.Tooltip(f"{y_field}:Q", title=config['y_label'], format=","),
            alt.Tooltip("type:N", title="Type"),
        ],
    )

    return (actual_bars + forecast_bars).properties(height=340)


def _build_multi_category_forecast_chart(base, x_field, y_field, category_field, category_label, config):
    """Build multi-category grouped bar chart with forecast."""
    actual_bars = base.transform_filter(
        alt.datum.type == "Actual"
    ).transform_calculate(
        combined_category=f'datum.{category_field} + " (Actual)"'
    ).mark_bar(size=20).encode(
        x=alt.X(f"{x_field}:T", title=config['x_label']),
        y=alt.Y(f"{y_field}:Q", title=config['y_label'], axis=alt.Axis(format=",.0f")),
        color=alt.Color(f"{category_field}:N", legend=alt.Legend(title=category_label)),
        xOffset="combined_category:N",
        tooltip=[
            alt.Tooltip(f"{x_field}:T", title=config['x_label']),
            alt.Tooltip(f"{y_field}:Q", title=config['y_label'], format=","),
            alt.Tooltip(f"{category_field}:N", title=category_label),
            alt.Tooltip("type:N", title="Type"),
        ],
    )
    
    forecast_bars = base.transform_filter(
        alt.datum.type == "Forecast"
    ).transform_calculate(
        combined_category=f'datum.{category_field} + " (Forecast)"'
    ).mark_bar(
        opacity=0.6,
        strokeWidth=2,
        size=20
    ).encode(
        x=alt.X(f"{x_field}:T", title=config['x_label']),
        y=alt.Y(f"{y_field}:Q", title=config['y_label'], axis=alt.Axis(format=",.0f")),
        color=alt.Color(f"{category_field}:N", legend=alt.Legend(title=category_label)),
        stroke=alt.Stroke(f"{category_field}:N", legend=None),
        strokeDash=alt.value([5, 5]),
        xOffset="combined_category:N",
        tooltip=[
            alt.Tooltip(f"{x_field}:T", title=config['x_label']),
            alt.Tooltip(f"{y_field}:Q", title=config['y_label'], format=","),
            alt.Tooltip(f"{category_field}:N", title=category_label),
            alt.Tooltip("type:N", title="Type"),
        ],
    )
    
    return (actual_bars + forecast_bars).properties(height=340)
