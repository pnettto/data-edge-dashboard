"""Multi-line chart component with Prophet-based forecasting per series."""

import streamlit as st
import altair as alt
import pandas as pd
from prophet import Prophet


@st.cache_data(show_spinner=False)
def _compute_all_forecasts(df: pd.DataFrame, x_field: str, y_field: str, 
                          category_field: str, max_periods: int, 
                          model_params: dict) -> dict:
    """Compute forecasts for all periods at once for all series."""
    forecasts = {}
    
    for series_name, group in df.groupby(category_field, sort=False):
        group_sorted = group.sort_values(by=x_field).copy()
        
        if len(group_sorted) >= 2:
            freq = pd.infer_freq(group_sorted[x_field])
            if freq is None:
                if len(group_sorted) > 1:
                    delta = (group_sorted[x_field].iloc[1] - group_sorted[x_field].iloc[0])
                    if hasattr(delta, 'days') and delta.days >= 1:
                        freq = f"{delta.days}D"
                    else:
                        freq = "D"
                else:
                    freq = "D"
            
            prophet_df = group_sorted[[x_field, y_field]].rename(columns={x_field: "ds", y_field: "y"})
            model = Prophet(**model_params)
            model.fit(prophet_df)
            
            # Generate forecast for max_periods once
            future = model.make_future_dataframe(periods=max_periods, freq=freq, include_history=False)
            forecast = model.predict(future)
            forecasts[series_name] = {
                'forecast': forecast[["ds", "yhat"]],
                'last_actual': group_sorted.sort_values(by=x_field).iloc[-1]
            }
    
    return forecasts


@st.fragment
def render_multi_line_forecast_chart(config):
    """Render chart in isolation so it doesn't block other page elements."""
    st.subheader(config['title'])
    st.caption(config['description'])

    df = config['df'].copy()
    x_field = config['x_field']
    y_field = config['y_field']
    category_field = config['category_field']

    base_key = id(config)

    forecast_periods = st.slider("Forecast periods", 1, 12, 6, key=f"ml_slider_{base_key}")

    # Use spinner for simple loading message
    with st.spinner(f"Generating forecasts..."):
        _render_chart_content(df, x_field, y_field, category_field, forecast_periods, config)


def _render_chart_content(df, x_field, y_field, category_field, forecast_periods, config):
    """Internal function to render the actual chart content."""
    if not pd.api.types.is_datetime64_any_dtype(df[x_field]):
        df[x_field] = pd.to_datetime(df[x_field])

    model_params = dict(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False,
        n_changepoints=10,
        seasonality_mode="additive",
        interval_width=0.0,
    )

    # Compute all forecasts once (cached)
    all_forecasts = _compute_all_forecasts(df, x_field, y_field, category_field, 12, model_params)

    # Build plot data
    forecast_frames: list[pd.DataFrame] = []
    plot_frames: list[pd.DataFrame] = []
    connector_frames: list[pd.DataFrame] = []

    for series_name, group in df.groupby(category_field, sort=False):
        group_sorted = group.sort_values(by=x_field).copy()
        group_sorted["type"] = "Actual"
        plot_frames.append(group_sorted)

        if series_name in all_forecasts:
            # Slice the pre-computed forecast to the selected number of periods
            forecast_data = all_forecasts[series_name]['forecast'].iloc[:forecast_periods].copy()
            last_actual = all_forecasts[series_name]['last_actual']
            
            forecast_df = pd.DataFrame({
                x_field: forecast_data['ds'], 
                y_field: forecast_data['yhat'], 
                category_field: series_name, 
                "type": ["Forecast"] * len(forecast_data)
            })
            forecast_frames.append(forecast_df)

            # Add connector line between last actual and first forecasted point
            if not forecast_df.empty:
                first_forecast = forecast_df.sort_values(by=x_field).iloc[0]
                connector_df = pd.DataFrame([
                    {
                        x_field: last_actual[x_field],
                        y_field: last_actual[y_field],
                        category_field: series_name,
                        "type": "Connector"
                    },
                    {
                        x_field: first_forecast[x_field],
                        y_field: first_forecast[y_field],
                        category_field: series_name,
                        "type": "Connector"
                    }
                ])
                connector_frames.append(connector_df)

    if forecast_frames:
        plot_df = pd.concat([*plot_frames, *forecast_frames], ignore_index=True)
    else:
        plot_df = pd.concat(plot_frames, ignore_index=True)

    # Combine all connector lines into one DataFrame
    if connector_frames:
        connector_df_all = pd.concat(connector_frames, ignore_index=True)
    else:
        connector_df_all = pd.DataFrame(columns=[x_field, y_field, category_field, "type"])

    # Layer three charts: Actual (solid), Forecast (dashed), Connector (dashed)
    base = alt.Chart(plot_df)

    actual_line = base.transform_filter(
        alt.datum.type == "Actual"
    ).mark_line(point=False).encode(
        x=alt.X(f"{x_field}:T", title=config['x_label']),
        y=alt.Y(f"{y_field}:Q", title=config['y_label'], axis=alt.Axis(format=",.0f")),
        color=alt.Color(f"{category_field}:N", title="series"),
        tooltip=[
            alt.Tooltip(f"{x_field}:T", title=config['x_label']),
            alt.Tooltip(f"{category_field}:N", title="series"),
            alt.Tooltip(f"{y_field}:Q", title=config['y_label'], format=","),
            alt.Tooltip("type:N", title="Type"),
        ],
    )

    forecast_line = base.transform_filter(
        alt.datum.type == "Forecast"
    ).mark_line(point=False, strokeDash=[5, 5]).encode(
        x=alt.X(f"{x_field}:T", title=config['x_label']),
        y=alt.Y(f"{y_field}:Q", title=config['y_label'], axis=alt.Axis(format=",.0f")),
        color=alt.Color(f"{category_field}:N", title="series"),
        tooltip=[
            alt.Tooltip(f"{x_field}:T", title=config['x_label']),
            alt.Tooltip(f"{category_field}:N", title="series"),
            alt.Tooltip(f"{y_field}:Q", title=config['y_label'], format=","),
            alt.Tooltip("type:N", title="Type"),
        ],
    )

    # Connector line: only if both actual and forecast exist for a series
    if not connector_df_all.empty:
        connector_chart = alt.Chart(connector_df_all).mark_line(point=False, strokeDash=[5, 5]).encode(
            x=alt.X(f"{x_field}:T"),
            y=alt.Y(f"{y_field}:Q"),
            color=alt.Color(f"{category_field}:N", title="series"),
        )
        chart = (actual_line + forecast_line + connector_chart).properties(height=340)
    else:
        chart = (actual_line + forecast_line).properties(height=340)

    st.altair_chart(chart, use_container_width=True)