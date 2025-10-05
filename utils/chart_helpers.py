"""Shared utilities for chart components"""

import pandas as pd


def should_show_points(df: pd.DataFrame, category_field: str = None, point_threshold: int = 200) -> bool:
    """Determine if individual points should be shown based on data density."""
    if category_field is not None:
        return all(
            df[df[category_field] == cat].shape[0] < point_threshold
            for cat in df[category_field].unique()
        )
    else:
        return df.shape[0] < point_threshold


def ensure_datetime(df: pd.DataFrame, x_field: str) -> pd.DataFrame:
    """Convert x_field to datetime if not already."""
    df = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(df[x_field]):
        df[x_field] = pd.to_datetime(df[x_field])
    return df


def get_category_label(config: dict, category_field: str) -> str:
    """Get the display label for category field."""
    return config.get('category_label', category_field) if category_field else None
