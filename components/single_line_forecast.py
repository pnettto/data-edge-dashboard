"""Single line chart component with Prophet-based forecasting"""

import streamlit as st
import altair as alt
import pandas as pd
from prophet import Prophet


#######################
# Forecasting Engine
#######################

@st.cache_data(show_spinner=False)
def _compute_forecast_single(df: pd.DataFrame, x_field: str, y_field: str, periods: int, freq: str) -> pd.DataFrame:
    """Core forecasting function using Prophet model."""
    model_params = dict(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False,
        n_changepoints=10,
        seasonality_mode="additive",
        interval_width=0.0,
    )
    # Prepare dataframe for Prophet: rename columns to 'ds' (date) and 'y' (value)
    prophet_df = df[[x_field, y_field]].rename(columns={x_field: "ds", y_field: "y"})
    # Instantiate Prophet model with provided parameters
    model = Prophet(**model_params)
    # Fit the Prophet model to the historical data
    model.fit(prophet_df)
    # Create future dates for forecasting (no history included)
    future = model.make_future_dataframe(periods=periods, freq=freq, include_history=False)
    # Predict future values using the trained model
    forecast = model.predict(future)
    # Return only the date and predicted value columns
    return forecast[["ds", "yhat"]]


#######################
# Data Preparation Functions
#######################

def prepare_actual_data(df: pd.DataFrame, x_field: str, y_field: str) -> pd.DataFrame:
    """Prepare historical data by adding type column for visualization."""
    df = df.copy()
    df["type"] = "Actual"
    return df


def create_forecast_data(df: pd.DataFrame, x_field: str, y_field: str, forecast_periods: int, freq: str) -> pd.DataFrame:
    """Generate forecasted data points using Prophet model with specified parameters."""
    forecast = _compute_forecast_single(df, x_field, y_field, forecast_periods, freq)
    return pd.DataFrame({
        x_field: forecast['ds'],
        y_field: forecast['yhat'],
        "type": ["Forecast"] * len(forecast)
    })


def create_connector_data(actual_df: pd.DataFrame, forecast_df: pd.DataFrame, x_field: str, y_field: str) -> pd.DataFrame:
    """Create connecting points between actual and forecasted data for smooth visualization."""
    if forecast_df.empty:
        return pd.DataFrame()

    last_actual = actual_df.sort_values(by=x_field).iloc[-1]
    first_forecast = forecast_df.sort_values(by=x_field).iloc[0]

    return pd.DataFrame([
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


def infer_frequency(df: pd.DataFrame, x_field: str) -> str:
    """Determine the time frequency of the data series for forecasting."""
    freq = pd.infer_freq(df[x_field].sort_values())
    if freq is not None:
        return freq

    if len(df) > 1:
        delta = (df[x_field].sort_values().iloc[1] - df[x_field].sort_values().iloc[0])
        if hasattr(delta, 'days') and delta.days >= 1:
            return f"{delta.days}D"

    return "D"


#######################
# Main Chart Rendering
#######################

def render_single_line_forecast_chart(config):
    """Render the forecast chart with actual and predicted values."""
    
    # Setup and configuration
    st.subheader(config['title'])
    st.caption(config['description'])
    
    # Data preparation
    df = config['df'].copy()
    x_field = config['x_field']
    y_field = config['y_field']

    # User controls
    base_key = id(config)
    forecast_periods = st.slider("Forecast periods", 1, 12, 6, key=f"slider_{base_key}")

    # Ensure datetime format
    if not pd.api.types.is_datetime64_any_dtype(df[x_field]):
        df[x_field] = pd.to_datetime(df[x_field])

    # Generate all required dataframes
    actual_df = prepare_actual_data(df, x_field, y_field)
    forecast_df = pd.DataFrame()
    connector_df = pd.DataFrame()

    if len(df) >= 2:
        freq = infer_frequency(df, x_field)
        forecast_df = create_forecast_data(df, x_field, y_field, forecast_periods, freq)
        connector_df = create_connector_data(actual_df, forecast_df, x_field, y_field)
        plot_df = pd.concat([actual_df, forecast_df], ignore_index=True)
    else:
        plot_df = actual_df.copy()

    #######################
    # Chart Construction
    #######################

    # Base chart settings
    base_color = "#1f77b4"
    base = alt.Chart(plot_df)
    show_points = plot_df[plot_df["type"] == "Actual"].shape[0] < 200

    # Create actual data line
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

    # Create forecast line
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

    # Add connector line if needed
    if not connector_df.empty:
        connector_chart = alt.Chart(connector_df).mark_line(point=False, color=base_color, strokeDash=[5, 5]).encode(
            x=alt.X(f"{x_field}:T"),
            y=alt.Y(f"{y_field}:Q"),
        )
        chart = (actual_line + forecast_line + connector_chart).properties(height=340)
    else:
        chart = (actual_line + forecast_line).properties(height=340)

    # Render the final chart
    st.altair_chart(chart, use_container_width=True)
