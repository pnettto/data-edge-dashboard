"""Single line chart component with Prophet-based forecasting"""

import streamlit as st
import altair as alt
import pandas as pd
from prophet import Prophet


@st.cache_data(show_spinner=False)
def _compute_forecast_single(df: pd.DataFrame, x_field: str, y_field: str, periods: int, freq: str, model_params: dict) -> pd.DataFrame:
    prophet_df = df[[x_field, y_field]].rename(columns={x_field: "ds", y_field: "y"})
    model = Prophet(**model_params)
    model.fit(prophet_df)
    future = model.make_future_dataframe(periods=periods, freq=freq, include_history=False)
    forecast = model.predict(future)
    return forecast[["ds", "yhat"]]


def render_single_line_forecast_chart(config):
    st.subheader(config['title'])
    st.caption(config['description'])

    df = config['df'].copy()
    x_field = config['x_field']
    y_field = config['y_field']

    base_key = id(config)

    forecast_periods = st.slider("Forecast periods", 6, 24, 12, key=f"slider_{base_key}")

    forecast_df = pd.DataFrame()
    connector_df = pd.DataFrame()

    if not pd.api.types.is_datetime64_any_dtype(df[x_field]):
        df[x_field] = pd.to_datetime(df[x_field])

    if len(df) >= 2:
        freq = pd.infer_freq(df[x_field].sort_values())
        if freq is None:
            if len(df) > 1:
                delta = (df[x_field].sort_values().iloc[1] - df[x_field].sort_values().iloc[0])
                if hasattr(delta, 'days') and delta.days >= 1:
                    freq = f"{delta.days}D"
                else:
                    freq = "D"
            else:
                freq = "D"

        model_params = dict(
            yearly_seasonality=True,
            weekly_seasonality=False,
            daily_seasonality=False,
            n_changepoints=10,
            seasonality_mode="additive",
            interval_width=0.0,
        )

        forecast = _compute_forecast_single(df, x_field, y_field, forecast_periods, freq, model_params)
        forecast_df = pd.DataFrame({x_field: forecast['ds'], y_field: forecast['yhat'], "type": ["Forecast"] * len(forecast)})

        df["type"] = "Actual"
        plot_df = pd.concat([df, forecast_df], ignore_index=True)

        # --- Add connector line between last actual and first forecasted point ---
        if not forecast_df.empty:
            # Get last actual point
            last_actual = df.sort_values(by=x_field).iloc[-1]
            # Get first forecasted point
            first_forecast = forecast_df.sort_values(by=x_field).iloc[0]
            connector_df = pd.DataFrame([
                {
                    x_field: last_actual[x_field],
                    y_field: last_actual[y_field],
                    "type": "Connector"
                },
                {
                    x_field: first_forecast[x_field],
                    y_field: first_forecast[y_field],
                    "type": "Connector"
                }
            ])
    else:
        plot_df = df.copy()
        plot_df["type"] = "Actual"

    # Make the forecasted part of the line dashed by layering three charts: one for Actual (solid), one for Forecast (dashed), one for Connector (dashed)
    base_color = "#1f77b4"
    base = alt.Chart(plot_df)
    show_points = plot_df[plot_df["type"] == "Actual"].shape[0] < 200

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

    # Connector line: only if both actual and forecast exist
    if not connector_df.empty:
        connector_chart = alt.Chart(connector_df).mark_line(point=False, color=base_color, strokeDash=[5, 5]).encode(
            x=alt.X(f"{x_field}:T"),
            y=alt.Y(f"{y_field}:Q"),
        )
        chart = (actual_line + forecast_line + connector_chart).properties(height=340)
    else:
        chart = (actual_line + forecast_line).properties(height=340)

    st.altair_chart(chart, use_container_width=True)
