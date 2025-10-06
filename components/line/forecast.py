"""Prophet-based forecasting"""

from typing import Optional
import pandas as pd
from prophet import Prophet


def generate_forecast(
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
    
    # Infer frequency of the time series from the x_field column
    freq = pd.infer_freq(df[x_field].sort_values())
    # If frequency can't be inferred and there are at least 2 rows, estimate frequency from the difference between first two sorted dates
    if freq is None and len(df) > 1:
        delta = df[x_field].sort_values().iloc[1] - df[x_field].sort_values().iloc[0]
        # If the delta has a 'days' attribute and is at least 1 day, use that as frequency; otherwise default to daily
        freq = f"{delta.days}D" if hasattr(delta, 'days') and delta.days >= 1 else "D"
    # If still unable to infer frequency, default to daily
    if freq is None:
        freq = "D"
    
    # Train Prophet model
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False,
        n_changepoints=10,
        seasonality_mode="additive",
        interval_width=0.0,
    )
    model.fit(prophet_df)
    
    # Generate forecast
    future = model.make_future_dataframe(periods=periods, freq=freq, include_history=False)
    forecast = model.predict(future)
    
    return pd.DataFrame({
        x_field: forecast['ds'],
        y_field: forecast['yhat'],
        "type": "Forecast"
    })
