"""Prophet-based forecasting for bar charts"""

from typing import Optional
import streamlit as st
import pandas as pd
from prophet import Prophet

MAX_FORECAST_PERIODS = 12
DEFAULT_FORECAST_PERIODS = 6

def create_forecast_df(config):
    """Handle forecasting"""
    if not config.get('forecast', False):
        return pd.DataFrame()

    df = config['df'].copy()
    x_field = config['x_field']
    category_field = config.get('category_field')
    
    # Generate forecast once with maximum periods (cached across reloads)
    with st.spinner("Generating forecast..."):
        full_forecast_df = _generate_forecast_df(
            df, x_field, config['y_field'], MAX_FORECAST_PERIODS, category_field
        )
    
    if full_forecast_df.empty:
        return pd.DataFrame()
    
    # Show slider to select forecast periods
    forecast_periods = st.slider(
        "Forecast periods", 
        1, 
        MAX_FORECAST_PERIODS, 
        DEFAULT_FORECAST_PERIODS, 
        key=f"slider_{id(config)}"
    )
    
    # Slice forecast based on selected periods
    if category_field:
        # Slice each category separately
        sliced_forecasts = [
            full_forecast_df[full_forecast_df[category_field] == category]
                .sort_values(by=x_field)
                .head(forecast_periods)
            for category in full_forecast_df[category_field].unique()
        ]
        return pd.concat(sliced_forecasts, ignore_index=True)
    
    return full_forecast_df.sort_values(by=x_field).head(forecast_periods)


@st.cache_data(show_spinner=False)
def _generate_forecast_df(
    df: pd.DataFrame,
    x_field: str,
    y_field: str,
    periods: int,
    category_field: Optional[str] = None
) -> pd.DataFrame:
    """Generate forecast using Prophet model."""
    
    if category_field is None:
        return _forecast_single(df, x_field, y_field, periods)
    
    # Forecast each category separately
    all_forecasts = []
    for category in sorted(df[category_field].unique()):
        category_df = df[df[category_field] == category].copy()
        if len(category_df) >= 2:
            forecast_df = _forecast_single(category_df, x_field, y_field, periods)
            forecast_df[category_field] = str(category)
            all_forecasts.append(forecast_df)
    
    return pd.concat(all_forecasts, ignore_index=True) if all_forecasts else pd.DataFrame()


def _forecast_single(df: pd.DataFrame, x_field: str, y_field: str, periods: int) -> pd.DataFrame:
    """Forecast a single time series."""
    # Prepare data for Prophet
    prophet_df = df[[x_field, y_field]].rename(columns={x_field: "ds", y_field: "y"})
    
    # Infer frequency from time series
    freq = _infer_frequency(df[x_field])
    
    # Train Prophet model with specified seasonality and changepoints
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False,
        n_changepoints=10,
        seasonality_mode="additive",
        interval_width=0.0,
    )
    model.fit(prophet_df)
    
    # Generate future dates and predict values
    future = model.make_future_dataframe(
        periods=periods,
        freq=freq,
        include_history=False
    )
    forecast = model.predict(future)
    
    return pd.DataFrame({
        x_field: forecast['ds'],
        y_field: forecast['yhat'],
        "type": "Forecast"
    })

def _infer_frequency(date_series: pd.Series) -> str:
    """Infer frequency from a datetime series, defaulting to daily."""
    sorted_dates = date_series.sort_values()
    
    # Try pandas built-in inference
    freq = pd.infer_freq(sorted_dates)
    if freq:
        return freq
    
    # Estimate from first two dates
    if len(sorted_dates) > 1:
        delta = sorted_dates.iloc[1] - sorted_dates.iloc[0]
        if hasattr(delta, 'days') and delta.days >= 1:
            return f"{delta.days}D"
    
    return "D"  # Default to daily
