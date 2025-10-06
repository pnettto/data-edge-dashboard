"""Helper functions for line chart component"""

from typing import Optional
import pandas as pd


def create_connectors(
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
        # Single series: connect last actual to first forecast
        last_actual = actual_df.sort_values(by=x_field).iloc[-1]
        first_forecast = forecast_df.sort_values(by=x_field).iloc[0]
        
        return pd.DataFrame([
            {x_field: last_actual[x_field], y_field: last_actual[y_field], "type": "Connector"},
            {x_field: first_forecast[x_field], y_field: first_forecast[y_field], "type": "Connector"}
        ])
    
    # Multi-series: connect each category separately
    connectors = []
    for category in sorted(actual_df[category_field].unique()):
        category = str(category)
        cat_actual = actual_df[actual_df[category_field] == category].sort_values(by=x_field)
        cat_forecast = forecast_df[forecast_df[category_field] == category].sort_values(by=x_field)
        
        if not cat_actual.empty and not cat_forecast.empty:
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
