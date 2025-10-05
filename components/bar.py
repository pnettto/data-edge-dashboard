"""Bar chart component with Prophet-based forecasting capability"""

import streamlit as st
import altair as alt
import pandas as pd
from utils.forecasting.engine import infer_frequency
from utils.forecasting.data_preparation import (
    prepare_actual_data,
    create_forecast_data,
)
from utils.chart_helpers import ensure_datetime, get_category_label


def render_bar_chart(config):
    """Render bar chart with actual and predicted values."""
    
    st.subheader(config['title'])
    st.caption(config['description'])
    
    df = config['df'].copy()
    x_field = config['x_field']
    y_field = config['y_field']
    category_field = config.get('category_field', None)
    enable_forecast = config.get('forecast', False)

    if enable_forecast:
        base_key = id(config)
        forecast_periods = st.slider("Forecast periods", 1, 12, 6, key=f"slider_{base_key}")

    df = ensure_datetime(df, x_field)

    if enable_forecast:
        actual_df = prepare_actual_data(df, x_field, y_field, category_field, with_type=True)
        forecast_df = pd.DataFrame()

        if len(df) >= 2:
            with st.spinner("Generating forecast..."):
                if category_field is None:
                    freq = infer_frequency(df, x_field)
                    forecast_df = create_forecast_data(df, x_field, y_field, forecast_periods, freq, category_field)
                else:
                    forecast_df = create_forecast_data(df, x_field, y_field, forecast_periods, None, category_field)
            
            if not forecast_df.empty:
                plot_df = pd.concat([actual_df, forecast_df], ignore_index=True)
            else:
                plot_df = actual_df.copy()
        else:
            plot_df = actual_df.copy()
    else:
        plot_df = prepare_actual_data(df, x_field, y_field, category_field, with_type=False)

    chart = _build_bar_chart(
        plot_df, config, x_field, y_field, category_field, enable_forecast
    )
    
    st.altair_chart(chart, use_container_width=True)


def _build_bar_chart(
    plot_df: pd.DataFrame,
    config: dict,
    x_field: str,
    y_field: str,
    category_field: str,
    enable_forecast: bool
) -> alt.Chart:
    """Build the Altair bar chart specification."""
    base_color = "#0b7dcfff"
    forecast_color = "#8ec8f0ff"
    base = alt.Chart(plot_df)
    
    is_multi_category = category_field is not None
    category_label = get_category_label(config, category_field)

    if enable_forecast:
        if is_multi_category:
            chart = _build_multi_category_forecast_chart(
                base, x_field, y_field, category_field, category_label, config
            )
        else:
            chart = _build_single_category_forecast_chart(
                base, x_field, y_field, config, base_color, forecast_color
            )
    else:
        if is_multi_category:
            chart = _build_multi_category_chart(
                base, x_field, y_field, category_field, category_label, config
            )
        else:
            chart = _build_single_category_chart(
                base, x_field, y_field, config, base_color
            )

    return chart


def _build_single_category_chart(base, x_field, y_field, config, base_color):
    """Build single category bar chart without forecast."""
    return base.mark_bar(color=base_color, size=30).encode(
        x=alt.X(f"{x_field}:T", title=config['x_label']),
        y=alt.Y(f"{y_field}:Q", title=config['y_label'], axis=alt.Axis(format=",.0f")),
        tooltip=[
            alt.Tooltip(f"{x_field}:T", title=config['x_label']),
            alt.Tooltip(f"{y_field}:Q", title=config['y_label'], format=","),
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
