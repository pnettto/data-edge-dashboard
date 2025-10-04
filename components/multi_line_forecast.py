import streamlit as st
import altair as alt
import pandas as pd
from prophet import Prophet


# ---------- FORECASTING LOGIC ----------

@st.cache_data(show_spinner=False)
def _compute_all_forecasts(df: pd.DataFrame, x_field: str, y_field: str,
                          category_field: str, max_periods: int,
                          model_params: dict) -> dict:
    """Compute and cache Prophet forecasts per series once."""
    forecasts = {}

    for series_name, group in df.groupby(category_field, sort=False):
        group_sorted = group.sort_values(by=x_field).copy()

        if len(group_sorted) < 2:
            continue

        # Infer or approximate frequency
        freq = pd.infer_freq(group_sorted[x_field])
        if freq is None:
            delta = group_sorted[x_field].iloc[1] - group_sorted[x_field].iloc[0]
            if hasattr(delta, "days") and delta.days >= 1:
                freq = f"{delta.days}D"
            else:
                freq = "D"

        prophet_df = group_sorted[[x_field, y_field]].rename(columns={x_field: "ds", y_field: "y"})
        model = Prophet(**model_params)
        model.fit(prophet_df)

        future = model.make_future_dataframe(periods=max_periods, freq=freq, include_history=False)
        forecast = model.predict(future)

        forecasts[series_name] = {
            "forecast": forecast[["ds", "yhat"]],
            "last_actual": group_sorted.iloc[-1],
        }

    return forecasts


@st.cache_data(show_spinner=False)
def get_cached_forecasts(df, x_field, y_field, category_field, model_params):
    """Wrapper to compute all forecasts once per dataset/config."""
    return _compute_all_forecasts(df, x_field, y_field, category_field, 12, model_params)


# ---------- CHART RENDERING ----------

def render_multi_line_forecast_chart(config):
    """Render chart with stable performance and correct layering."""
    st.subheader(config["title"])
    st.caption(config["description"])

    df = config["df"].copy()
    x_field = config["x_field"]
    y_field = config["y_field"]
    category_field = config["category_field"]

    # Ensure datetime type
    if not pd.api.types.is_datetime64_any_dtype(df[x_field]):
        df[x_field] = pd.to_datetime(df[x_field])

    # Prophet parameters
    model_params = dict(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False,
        n_changepoints=10,
        seasonality_mode="additive",
        interval_width=0.0,
    )

    # Cache once — outside of fragment
    all_forecasts = get_cached_forecasts(df, x_field, y_field, category_field, model_params)

    # --- The only interactive part ---
    forecast_periods = st.slider("Forecast periods", 1, 12, 6, key=f"ml_slider_{id(config)}")

    # --- Chart fragment (non-blocking, faster rerender) ---
    @st.fragment
    def _forecast_chart_fragment(df, x_field, y_field, category_field, forecast_periods, config, all_forecasts):
        _render_chart_content(df, x_field, y_field, category_field, forecast_periods, config, all_forecasts)

    _forecast_chart_fragment(df, x_field, y_field, category_field, forecast_periods, config, all_forecasts)



def _render_chart_content(df, x_field, y_field, category_field, forecast_periods, config, all_forecasts):
    """Render the actual Altair chart from cached data."""
    forecast_frames, plot_frames, connector_frames = [], [], []

    for series_name, group in df.groupby(category_field, sort=False):
        group_sorted = group.sort_values(by=x_field).copy()
        group_sorted["type"] = "Actual"
        plot_frames.append(group_sorted)

        if series_name not in all_forecasts:
            continue

        forecast_data = all_forecasts[series_name]["forecast"]
        if forecast_data.empty:
            continue

        forecast_data = forecast_data.iloc[:min(forecast_periods, len(forecast_data))].copy()
        last_actual = all_forecasts[series_name]["last_actual"]

        forecast_df = pd.DataFrame({
            x_field: forecast_data["ds"],
            y_field: forecast_data["yhat"],
            category_field: series_name,
            "type": "Forecast",
        })
        forecast_frames.append(forecast_df)

        # Connector between last actual and first forecast
        if not forecast_df.empty and not pd.isna(last_actual[y_field]):
            first_forecast = forecast_df.iloc[0]
            connector_df = pd.DataFrame([
                {
                    x_field: last_actual[x_field],
                    y_field: last_actual[y_field],
                    category_field: series_name,
                    "type": "Connector",
                },
                {
                    x_field: first_forecast[x_field],
                    y_field: first_forecast[y_field],
                    category_field: series_name,
                    "type": "Connector",
                },
            ])
            connector_frames.append(connector_df)

    # Combine data
    combined = pd.concat([*plot_frames, *forecast_frames], ignore_index=True)
    connector_df_all = pd.concat(connector_frames, ignore_index=True) if connector_frames else None

    # Build layered chart
    base = alt.Chart(combined)

    actual_line = base.transform_filter(
        alt.datum.type == "Actual"
    ).mark_line(point=False).encode(
        x=alt.X(f"{x_field}:T", title=config["x_label"]),
        y=alt.Y(f"{y_field}:Q", title=config["y_label"], axis=alt.Axis(format=",.0f")),
        color=alt.Color(f"{category_field}:N", title="Series"),
        tooltip=[
            alt.Tooltip(f"{x_field}:T", title=config["x_label"]),
            alt.Tooltip(f"{category_field}:N", title="Series"),
            alt.Tooltip(f"{y_field}:Q", title=config["y_label"], format=","),
        ],
    )

    forecast_line = base.transform_filter(
        alt.datum.type == "Forecast"
    ).mark_line(point=False, strokeDash=[5, 5]).encode(
        x=alt.X(f"{x_field}:T"),
        y=alt.Y(f"{y_field}:Q"),
        color=alt.Color(f"{category_field}:N", title="Series"),
    )

    chart = actual_line + forecast_line

    if connector_df_all is not None and not connector_df_all.empty:
        connector_chart = alt.Chart(connector_df_all).mark_line(point=False, strokeDash=[5, 5]).encode(
            x=alt.X(f"{x_field}:T"),
            y=alt.Y(f"{y_field}:Q"),
            color=alt.Color(f"{category_field}:N", title="Series"),
        )
        chart += connector_chart

    chart = chart.properties(height=340)

    # Stable key ensures smooth update, no flicker
    st.altair_chart(chart, use_container_width=True, key=f"forecast_chart_{id(config)}")
