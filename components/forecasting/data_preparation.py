"""Data preparation utilities for forecast visualizations"""

import pandas as pd
from .engine import compute_forecast, infer_frequency


def prepare_actual_data(
    df: pd.DataFrame,
    x_field: str,
    y_field: str,
    category_field: str = None,
    with_type: bool = True
) -> pd.DataFrame:
    """Add type column to historical data for visualization."""
    df = df.copy()
    if with_type:
        df["type"] = "Actual"
    return df


def create_forecast_data(
    df: pd.DataFrame,
    x_field: str,
    y_field: str,
    forecast_periods: int,
    freq: str,
    category_field: str = None,
    max_periods: int = 12
) -> pd.DataFrame:
    """Generate forecasted data points using Prophet model."""
    if category_field is None:
        forecast = compute_forecast(df, x_field, y_field, max_periods, freq)
        forecast = forecast.iloc[:forecast_periods]
        return pd.DataFrame({
            x_field: forecast['ds'],
            y_field: forecast['yhat'],
            "type": ["Forecast"] * len(forecast)
        })
    else:
        all_forecasts = []
        categories = sorted(df[category_field].unique())
        for category in categories:
            category_df = df[df[category_field] == category].copy()
            if len(category_df) >= 2:
                category_freq = infer_frequency(category_df, x_field)
                forecast = compute_forecast(category_df, x_field, y_field, max_periods, category_freq, str(category))
                forecast = forecast.iloc[:forecast_periods]
                forecast_data = pd.DataFrame({
                    x_field: forecast['ds'],
                    y_field: forecast['yhat'],
                    category_field: str(category),
                    "type": ["Forecast"] * len(forecast)
                })
                all_forecasts.append(forecast_data)
        
        if all_forecasts:
            return pd.concat(all_forecasts, ignore_index=True)
        return pd.DataFrame()


def create_connector_data(
    actual_df: pd.DataFrame,
    forecast_df: pd.DataFrame,
    x_field: str,
    y_field: str,
    category_field: str = None
) -> pd.DataFrame:
    """Create connecting points between actual and forecasted data."""
    if forecast_df.empty:
        return pd.DataFrame()

    if category_field is None:
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
    else:
        all_connectors = []
        categories = sorted(actual_df[category_field].unique())
        for category in categories:
            category = str(category)
            category_actual = actual_df[actual_df[category_field] == category].sort_values(by=x_field)
            category_forecast = forecast_df[forecast_df[category_field] == category].sort_values(by=x_field)
            
            if not category_actual.empty and not category_forecast.empty:
                last_actual = category_actual.iloc[-1]
                first_forecast = category_forecast.iloc[0]
                
                connectors = pd.DataFrame([
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
                ])
                all_connectors.append(connectors)
        
        if all_connectors:
            return pd.concat(all_connectors, ignore_index=True)
        return pd.DataFrame()
