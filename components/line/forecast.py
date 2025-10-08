"""Prophet-based forecasting"""

from typing import Optional
import streamlit as st
import pandas as pd
from prophet import Prophet

MAX_FORECAST_PERIODS = 24
DEFAULT_FORECAST_PERIODS = 12
FORECAST_OPTIONS = [6, 12, 18, 24]

def create_forecast_df(config, forecast_periods: int = DEFAULT_FORECAST_PERIODS):
    """Generate (and slice) forecast dataframe. UI selection is handled by caller."""
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
    
    # Slice forecast based on provided forecast_periods (no internal UI)
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
        yearly_seasonality=True,      # Enable yearly seasonality
        weekly_seasonality=False,     # Disable weekly seasonality
        daily_seasonality=False,      # Disable daily seasonality
        n_changepoints=10,            # Number of changepoints for trend flexibility
        seasonality_mode="additive",  # Use additive seasonality
        interval_width=0.0,           # No uncertainty interval
    )
    model.fit(prophet_df)             # Fit model to historical data
    
    # Generate future dates and predict values
    future = model.make_future_dataframe(
        periods=periods,              # Number of periods to forecast
        freq=freq,                    # Frequency inferred from data
        include_history=False         # Only forecast future, exclude history
    )
    forecast = model.predict(future)  # Predict future values
    
    return pd.DataFrame({
        x_field: forecast['ds'],
        y_field: forecast['yhat'],
        "type": "Forecast"
    })

def _infer_frequency(date_series: pd.Series) -> str:
    """Infer frequency from a datetime series, defaulting to daily."""
    sorted_dates = date_series.sort_values()
    
    # Ensure dates are datetime type before frequency inference
    if not pd.api.types.is_datetime64_any_dtype(sorted_dates):
        try:
            sorted_dates = pd.to_datetime(sorted_dates)
        except Exception:
            return "D"  # Default to daily if conversion fails
    
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

def create_connector_df(
    actual_df: pd.DataFrame,
    forecast_df: pd.DataFrame,
    x_field: str,
    y_field: str,
    category_field: Optional[str] = None
) -> pd.DataFrame:
    """
    Create connecting lines between actual and forecasted data.
    
    Connectors provide a visual bridge between the last actual point
    and the first forecast point for smooth chart transitions.
    """
    if forecast_df.empty:
        return pd.DataFrame()
    
    if category_field is None:
        return _create_single_connector(actual_df, forecast_df, x_field, y_field)
    
    return _create_multi_connector(actual_df, forecast_df, x_field, y_field, category_field)

def _create_single_connector(
    actual_df: pd.DataFrame, 
    forecast_df: pd.DataFrame, 
    x_field: str, 
    y_field: str
) -> pd.DataFrame:
    """Create connector for single series."""
    last_actual = actual_df.sort_values(by=x_field).iloc[-1]
    first_forecast = forecast_df.sort_values(by=x_field).iloc[0]
    
    return pd.DataFrame([
        {x_field: last_actual[x_field], y_field: last_actual[y_field], "type": "Connector"},
        {x_field: first_forecast[x_field], y_field: first_forecast[y_field], "type": "Connector"}
    ])

def _create_multi_connector(
    actual_df: pd.DataFrame, 
    forecast_df: pd.DataFrame, 
    x_field: str, 
    y_field: str,
    category_field: str
) -> pd.DataFrame:
    """Create connectors for multi-series."""
    connectors = []
    
    for category in sorted(actual_df[category_field].unique()):
        category = str(category)
        cat_actual = actual_df[actual_df[category_field] == category].sort_values(by=x_field)
        cat_forecast = forecast_df[forecast_df[category_field] == category].sort_values(by=x_field)
        
        if cat_actual.empty or cat_forecast.empty:
            continue
        
        last_actual = cat_actual.iloc[-1]
        first_forecast = cat_forecast.iloc[0]
        
        connectors.append(pd.DataFrame([
            {
                x_field: last_actual[x_field], 
                y_field: last_actual[y_field],
                category_field: category,
                "type": "Connector"
            },
            {
                x_field: first_forecast[x_field], 
                y_field: first_forecast[y_field],
                category_field: category,
                "type": "Connector"
            }
        ]))
    
    return pd.concat(connectors, ignore_index=True) if connectors else pd.DataFrame()
