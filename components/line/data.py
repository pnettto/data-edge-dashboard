"""Data utilities for line charts"""

import pandas as pd
from typing import Optional


def should_show_points(df: pd.DataFrame, category_field: Optional[str] = None) -> bool:
    """Determine if individual points should be shown based on data density."""
    threshold = 200
    
    if category_field:
        return all(
            df[df[category_field] == cat].shape[0] < threshold
            for cat in df[category_field].unique()
        )
    return df.shape[0] < threshold
