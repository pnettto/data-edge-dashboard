"""Prophet-based forecasting engine"""

import streamlit as st
import pandas as pd
from prophet import Prophet


@st.cache_data(show_spinner=False)
def compute_forecast(
    df: pd.DataFrame,
    x_field: str,
    y_field: str,
    periods: int,
    freq: str,
    category: str = None
) -> pd.DataFrame:
    """Generate forecast using Prophet model."""
    model_params = dict(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False,
        n_changepoints=10,
        seasonality_mode="additive",
        interval_width=0.0,
    )
    
    prophet_df = df[[x_field, y_field]].rename(columns={x_field: "ds", y_field: "y"})
    model = Prophet(**model_params)
    model.fit(prophet_df)
    
    future = model.make_future_dataframe(periods=periods, freq=freq, include_history=False)
    forecast = model.predict(future)
    
    result = forecast[["ds", "yhat"]].copy()
    if category is not None:
        result["category"] = category
    return result


def infer_frequency(df: pd.DataFrame, x_field: str) -> str:
    """Determine the time frequency of the data series."""
    freq = pd.infer_freq(df[x_field].sort_values())
    if freq is not None:
        return freq

    if len(df) > 1:
        delta = (df[x_field].sort_values().iloc[1] - df[x_field].sort_values().iloc[0])
        if hasattr(delta, 'days') and delta.days >= 1:
            return f"{delta.days}D"

    return "D"
