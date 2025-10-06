"""Data preparation utilities for line charts"""

from typing import Optional
import pandas as pd


# Constants
POINT_THRESHOLD = 200


def ensure_datetime(df: pd.DataFrame, x_field: str) -> pd.DataFrame:
    """Convert x_field to datetime if not already."""
    df = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(df[x_field]):
        df[x_field] = pd.to_datetime(df[x_field])
    return df


def prepare_actual_data(
    df: pd.DataFrame,
    x_field: str,
    y_field: str,
    category_field: Optional[str] = None,
    with_type: bool = True
) -> pd.DataFrame:
    """Add type column to historical data for visualization."""
    df = df.copy()
    if with_type:
        df["type"] = "Actual"
    return df


def create_connector_data(
    actual_df: pd.DataFrame,
    forecast_df: pd.DataFrame,
    x_field: str,
    y_field: str,
    category_field: Optional[str] = None
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


def should_show_points(
    df: pd.DataFrame, 
    category_field: Optional[str] = None, 
    point_threshold: int = POINT_THRESHOLD
) -> bool:
    """Determine if individual points should be shown based on data density."""
    if category_field is not None:
        return all(
            df[df[category_field] == cat].shape[0] < point_threshold
            for cat in df[category_field].unique()
        )
    else:
        return df.shape[0] < point_threshold
