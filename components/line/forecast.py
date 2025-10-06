"""Prophet-based forecasting engine"""

from typing import Optional
import pandas as pd
import streamlit as st
from prophet import Prophet


# Constants
MAX_FORECAST_PERIODS = 12


class ForecastEngine:
    """Handles time series forecasting using Prophet."""
    
    @staticmethod
    @st.cache_data(show_spinner=False)
    def compute_forecast(
        df: pd.DataFrame,
        x_field: str,
        y_field: str,
        periods: int,
        freq: str,
        category: Optional[str] = None
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
    
    @staticmethod
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
    
    def create_forecast_data(
        self,
        df: pd.DataFrame,
        x_field: str,
        y_field: str,
        forecast_periods: int,
        category_field: Optional[str] = None
    ) -> pd.DataFrame:
        """Generate forecasted data points using Prophet model."""
        if category_field is None:
            freq = self.infer_frequency(df, x_field)
            forecast = self.compute_forecast(df, x_field, y_field, MAX_FORECAST_PERIODS, freq)
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
                    category_freq = self.infer_frequency(category_df, x_field)
                    forecast = self.compute_forecast(
                        category_df, 
                        x_field, 
                        y_field, 
                        MAX_FORECAST_PERIODS, 
                        category_freq, 
                        str(category)
                    )
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
