"""Prophet-based forecasting for bar charts"""

from typing import Optional
import streamlit as st
import pandas as pd
from prophet import Prophet

MAX_FORECAST_PERIODS = 12
DEFAULT_FORECAST_PERIODS = 6


def _convert_to_datetime(series: pd.Series) -> pd.Series:
    """Convert series to datetime, handling various formats."""
    if pd.api.types.is_datetime64_any_dtype(series):
        return series
    
    # Try to parse as quarter strings (e.g., "2021Q1")
    if series.astype(str).str.match(r'^\d{4}Q[1-4]$').any():
        return pd.PeriodIndex(series, freq='Q').to_timestamp()
    
    # Try standard datetime conversion
    try:
        return pd.to_datetime(series)
    except Exception:
        # If all else fails, try to infer
        return pd.to_datetime(series, infer_datetime_format=True)


def create_forecast_df(config):
    """Handle forecasting"""
    if not config.get('forecast', False):
        return pd.DataFrame()

    df = config['df'].copy()
    x_field = config['x_field']
    category_field = config.get('category_field')
    
    # Convert x-axis to datetime for forecasting
    df[x_field] = _convert_to_datetime(df[x_field])
    
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
        if hasattr(delta, 'days'):
            days = delta.days
            # Detect quarterly (approximately 90 days)
            if 80 <= days <= 100:
                return "QS"  # Quarter start
            # Detect monthly (approximately 30 days)
            elif 28 <= days <= 31:
                return "MS"  # Month start
            elif days >= 1:
                return f"{days}D"
    
    return "D"  # Default to daily
