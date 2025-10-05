"""Line chart component with Prophet-based forecasting capability"""

import streamlit as st
import altair as alt
import pandas as pd
from .forecasting.engine import infer_frequency
from .forecasting.data_preparation import (
    prepare_actual_data,
    create_forecast_data,
    create_connector_data
)
from .chart_utils import should_show_points, ensure_datetime, get_category_label


def render_line_chart(config):
    """Render the forecast chart with actual and predicted values."""
    
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

    # Initialize connector_df at the top level
    connector_df = pd.DataFrame()
    
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
                
                connector_df = create_connector_data(actual_df, forecast_df, x_field, y_field, category_field)
            
            if not forecast_df.empty:
                plot_df = pd.concat([actual_df, forecast_df], ignore_index=True)
            else:
                plot_df = actual_df.copy()
        else:
            plot_df = actual_df.copy()
    else:
        plot_df = prepare_actual_data(df, x_field, y_field, category_field, with_type=False)

    chart = _build_line_chart(
        plot_df, connector_df, config, x_field, y_field, category_field, enable_forecast
    )
    
    st.altair_chart(chart, use_container_width=True)


def _build_line_chart(
    plot_df: pd.DataFrame,
    connector_df: pd.DataFrame,
    config: dict,
    x_field: str,
    y_field: str,
    category_field: str,
    enable_forecast: bool
) -> alt.Chart:
    """Build the Altair line chart specification."""
    base_color = "#0b7dcfff"
    base = alt.Chart(plot_df)
    
    if enable_forecast:
        actual_data = plot_df[plot_df["type"] == "Actual"]
        show_points = should_show_points(actual_data, category_field)
    else:
        show_points = should_show_points(plot_df, category_field)

    is_multi_line = category_field is not None
    category_label = get_category_label(config, category_field)

    if enable_forecast:
        if is_multi_line:
            chart = _build_multi_line_forecast_chart(
                base, connector_df, x_field, y_field, category_field,
                category_label, config, show_points
            )
        else:
            chart = _build_single_line_forecast_chart(
                base, connector_df, x_field, y_field, config, show_points, base_color
            )
    else:
        if is_multi_line:
            chart = _build_multi_line_chart(
                base, x_field, y_field, category_field, category_label, config, show_points
            )
        else:
            chart = _build_single_line_chart(
                base, x_field, y_field, config, show_points, base_color
            )

    return chart


def _build_single_line_chart(base, x_field, y_field, config, show_points, base_color):
    """Build single line chart without forecast."""
    return base.mark_line(point=show_points, color=base_color).encode(
        x=alt.X(f"{x_field}:T", title=config['x_label']),
        y=alt.Y(f"{y_field}:Q", title=config['y_label'], axis=alt.Axis(format=",.0f")),
        tooltip=[
            alt.Tooltip(f"{x_field}:T", title=config['x_label']),
            alt.Tooltip(f"{y_field}:Q", title=config['y_label'], format=","),
        ],
    ).properties(height=340)


def _build_multi_line_chart(base, x_field, y_field, category_field, category_label, config, show_points):
    """Build multi-line chart without forecast."""
    return base.mark_line(point=show_points).encode(
        x=alt.X(f"{x_field}:T", title=config['x_label']),
        y=alt.Y(f"{y_field}:Q", title=config['y_label'], axis=alt.Axis(format=",.0f")),
        color=alt.Color(f"{category_field}:N", legend=alt.Legend(title=category_label)),
        tooltip=[
            alt.Tooltip(f"{x_field}:T", title=config['x_label']),
            alt.Tooltip(f"{y_field}:Q", title=config['y_label'], format=","),
            alt.Tooltip(f"{category_field}:N", title=category_label),
        ],
    ).properties(height=340)


def _build_single_line_forecast_chart(base, connector_df, x_field, y_field, config, show_points, base_color):
    """Build single line chart with forecast."""
    actual_line = base.transform_filter(
        alt.datum.type == "Actual"
    ).mark_line(point=show_points, color=base_color).encode(
        x=alt.X(f"{x_field}:T", title=config['x_label']),
        y=alt.Y(f"{y_field}:Q", title=config['y_label'], axis=alt.Axis(format=",.0f")),
        tooltip=[
            alt.Tooltip(f"{x_field}:T", title=config['x_label']),
            alt.Tooltip(f"{y_field}:Q", title=config['y_label'], format=","),
            alt.Tooltip("type:N", title="Type"),
        ],
    )

    forecast_line = base.transform_filter(
        alt.datum.type == "Forecast"
    ).mark_line(point=show_points, color=base_color, strokeDash=[5, 5]).encode(
        x=alt.X(f"{x_field}:T", title=config['x_label']),
        y=alt.Y(f"{y_field}:Q", title=config['y_label'], axis=alt.Axis(format=",.0f")),
        tooltip=[
            alt.Tooltip(f"{x_field}:T", title=config['x_label']),
            alt.Tooltip(f"{y_field}:Q", title=config['y_label'], format=","),
            alt.Tooltip("type:N", title="Type"),
        ],
    )

    if not connector_df.empty:
        connector_chart = alt.Chart(connector_df).mark_line(
            point=False, color=base_color, strokeDash=[5, 5]
        ).encode(
            x=alt.X(f"{x_field}:T"),
            y=alt.Y(f"{y_field}:Q"),
        )
        return (actual_line + forecast_line + connector_chart).properties(height=340)
    else:
        return (actual_line + forecast_line).properties(height=340)


def _build_multi_line_forecast_chart(base, connector_df, x_field, y_field, category_field, category_label, config, show_points):
    """Build multi-line chart with forecast."""
    actual_line = base.transform_filter(
        alt.datum.type == "Actual"
    ).mark_line(point=show_points).encode(
        x=alt.X(f"{x_field}:T", title=config['x_label']),
        y=alt.Y(f"{y_field}:Q", title=config['y_label'], axis=alt.Axis(format=",.0f")),
        color=alt.Color(f"{category_field}:N", legend=alt.Legend(title=category_label)),
        tooltip=[
            alt.Tooltip(f"{x_field}:T", title=config['x_label']),
            alt.Tooltip(f"{y_field}:Q", title=config['y_label'], format=","),
            alt.Tooltip(f"{category_field}:N", title=category_label),
            alt.Tooltip("type:N", title="Type"),
        ],
    )
    
    forecast_line = base.transform_filter(
        alt.datum.type == "Forecast"
    ).mark_line(point=show_points, strokeDash=[5, 5]).encode(
        x=alt.X(f"{x_field}:T", title=config['x_label']),
        y=alt.Y(f"{y_field}:Q", title=config['y_label'], axis=alt.Axis(format=",.0f")),
        color=alt.Color(f"{category_field}:N", legend=alt.Legend(title=category_label)),
        tooltip=[
            alt.Tooltip(f"{x_field}:T", title=config['x_label']),
            alt.Tooltip(f"{y_field}:Q", title=config['y_label'], format=","),
            alt.Tooltip(f"{category_field}:N", title=category_label),
            alt.Tooltip("type:N", title="Type"),
        ],
    )
    
    if not connector_df.empty:
        connector_chart = alt.Chart(connector_df).mark_line(
            point=False, strokeDash=[5, 5]
        ).encode(
            x=alt.X(f"{x_field}:T"),
            y=alt.Y(f"{y_field}:Q"),
            color=alt.Color(f"{category_field}:N", legend=alt.Legend(title=category_label)),
        )
        return (actual_line + forecast_line + connector_chart).properties(height=340)
    else:
        return (actual_line + forecast_line).properties(height=340)