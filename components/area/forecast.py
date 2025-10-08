"""Forecasting logic for stacked area charts"""

import pandas as pd


def create_forecast_df(config: dict) -> pd.DataFrame:
    """
    Create forecast DataFrame if forecasting is enabled.

    Args:
        config (dict): Configuration dictionary.

    Returns:
        pd.DataFrame: Forecast data or empty DataFrame if forecasting disabled.
    """
    if not config.get('forecast', False):
        return pd.DataFrame()

    # Placeholder for actual Prophet implementation
    # For now, return empty DataFrame
    return pd.DataFrame()


def create_connector_df(
    actual_df: pd.DataFrame,
    forecast_df: pd.DataFrame,
    x_field: str,
    y_field: str,
    category_field: str = None
) -> pd.DataFrame:
    """
    Create connector points between actual and forecast data.

    Args:
        actual_df (pd.DataFrame): Actual data.
        forecast_df (pd.DataFrame): Forecast data.
        x_field (str): X-axis field name.
        y_field (str): Y-axis field name.
        category_field (str, optional): Category field name.

    Returns:
        pd.DataFrame: Connector data or empty DataFrame.
    """
    if forecast_df.empty:
        return pd.DataFrame()

    # Get last actual point for each category
    if category_field:
        last_actual = actual_df.sort_values(x_field).groupby(category_field).last().reset_index()
    else:
        last_actual = actual_df.sort_values(x_field).tail(1)

    last_actual["type"] = "Connector"
    return last_actual
