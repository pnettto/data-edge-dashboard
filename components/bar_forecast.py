"""Bar chart component with Prophet-based forecasting.

Supports both single-series (no category_field) and multi-series (with category_field) inputs.
Actual bars are colored by series (or a base color for single series).
Forecast bars are shown in orange (#ff7f0e).
"""

import streamlit as st
import altair as alt
import pandas as pd
from prophet import Prophet


@st.cache_data(show_spinner=False)
def _compute_forecast_bar(df: pd.DataFrame, x_field: str, y_field: str, periods: int, freq: str, model_params: dict) -> pd.DataFrame:
    prophet_df = df[[x_field, y_field]].rename(columns={x_field: "ds", y_field: "y"})
    model = Prophet(**model_params)
    model.fit(prophet_df)
    future = model.make_future_dataframe(periods=periods, freq=freq, include_history=False)
    forecast = model.predict(future)
    return forecast[["ds", "yhat"]]


def render_bar_forecast_chart(config):
    st.subheader(config['title'])
    st.caption(config['description'])

    df = config['df'].copy()
    x_field = config['x_field']
    y_field = config['y_field']
    category_field = config.get('category_field')

    base_key = id(config)
    forecast_periods = st.slider("Forecast periods", 1, 12, 6, key=f"bar_slider_{base_key}")

    if not pd.api.types.is_datetime64_any_dtype(df[x_field]):
        df[x_field] = pd.to_datetime(df[x_field])

    def infer_freq_from_series(series: pd.Series) -> str:
        freq = pd.infer_freq(series.sort_values())
        if freq is None:
            if len(series) > 1:
                delta = series.sort_values().iloc[1] - series.sort_values().iloc[0]
                if hasattr(delta, 'days') and delta.days >= 1:
                    freq = f"{delta.days}D"
                else:
                    freq = "D"
            else:
                freq = "D"
        return freq

    if category_field:
        # Multi-series: forecast per category
        plot_frames: list[pd.DataFrame] = []
        forecast_frames: list[pd.DataFrame] = []

        for series_name, group in df.groupby(category_field, sort=False):
            group_sorted = group.sort_values(by=x_field).copy()
            group_sorted["type"] = "Actual"
            plot_frames.append(group_sorted)

            if len(group_sorted) >= 2:
                freq = infer_freq_from_series(group_sorted[x_field])
                model_params = dict(
                    yearly_seasonality=True,
                    weekly_seasonality=False,
                    daily_seasonality=False,
                    n_changepoints=10,
                    seasonality_mode="additive",
                    interval_width=0.0,
                )
                forecast = _compute_forecast_bar(group_sorted, x_field, y_field, forecast_periods, freq, model_params)

                fc_df = pd.DataFrame({
                    x_field: forecast['ds'],
                    y_field: forecast['yhat'],
                    category_field: series_name,
                    "type": ["Forecast"] * len(forecast)
                })
                forecast_frames.append(fc_df)

        if forecast_frames:
            plot_df = pd.concat([*plot_frames, *forecast_frames], ignore_index=True)
        else:
            plot_df = pd.concat(plot_frames, ignore_index=True)

        # Build layered chart: actual bars by series, forecast bars orange
        base = alt.Chart(plot_df)

        actual_bars = base.transform_filter(
            alt.datum.type == "Actual"
        ).mark_bar().encode(
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

        forecast_bars = base.transform_filter(
            alt.datum.type == "Forecast"
        ).mark_bar(color="#ff7f0e").encode(
            x=alt.X(f"{x_field}:T", title=config['x_label']),
            y=alt.Y(f"{y_field}:Q", title=config['y_label'], axis=alt.Axis(format=",.0f")),
            tooltip=[
                alt.Tooltip(f"{x_field}:T", title=config['x_label']),
                alt.Tooltip(f"{category_field}:N", title="series"),
                alt.Tooltip(f"{y_field}:Q", title=config['y_label'], format=","),
                alt.Tooltip("type:N", title="Type"),
            ],
        )

        chart = (actual_bars + forecast_bars).properties(height=340)

    else:
        # Single series: treat entire df as one series
        plot_df = df.copy()
        plot_df = plot_df.sort_values(by=x_field)

        forecast_df = pd.DataFrame()

        if len(plot_df) >= 2:
            freq = infer_freq_from_series(plot_df[x_field])
            model_params = dict(
                yearly_seasonality=True,
                weekly_seasonality=False,
                daily_seasonality=False,
                n_changepoints=10,
                seasonality_mode="additive",
                interval_width=0.0,
            )
            forecast = _compute_forecast_bar(plot_df, x_field, y_field, forecast_periods, freq, model_params)

            forecast_df = pd.DataFrame({
                x_field: forecast['ds'],
                y_field: forecast['yhat'],
                "type": ["Forecast"] * len(forecast)
            })

            plot_df["type"] = "Actual"
            plot_df = pd.concat([plot_df, forecast_df], ignore_index=True)
        else:
            plot_df["type"] = "Actual"

        base = alt.Chart(plot_df)

        actual_bars = base.transform_filter(
            alt.datum.type == "Actual"
        ).mark_bar().encode(
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
        ).mark_bar(color="#ff7f0e").encode(
            x=alt.X(f"{x_field}:T", title=config['x_label']),
            y=alt.Y(f"{y_field}:Q", title=config['y_label'], axis=alt.Axis(format=",.0f")),
            tooltip=[
                alt.Tooltip(f"{x_field}:T", title=config['x_label']),
                alt.Tooltip(f"{y_field}:Q", title=config['y_label'], format=","),
                alt.Tooltip("type:N", title="Type"),
            ],
        )

        chart = (actual_bars + forecast_bars).properties(height=340)

    st.altair_chart(chart, use_container_width=True)
