"""Configuration management for line charts"""

from dataclasses import dataclass
from typing import Optional
import pandas as pd


@dataclass
class LineChartConfig:
    """Configuration for line chart rendering."""
    title: str
    description: str
    df: pd.DataFrame
    x_field: str
    y_field: str
    x_label: str
    y_label: str
    category_field: Optional[str] = None
    category_label: Optional[str] = None
    forecast: bool = False


def validate_config(config: dict) -> LineChartConfig:
    """
    Validate and normalize chart configuration.
    
    Args:
        config: Raw configuration dictionary
        
    Returns:
        Validated LineChartConfig instance with defaults applied
    """
    # Set defaults for optional fields
    category_field = config.get('category_field', None)
    
    return LineChartConfig(
        title=config['title'],
        description=config['description'],
        df=config['df'].copy(),
        x_field=config['x_field'],
        y_field=config['y_field'],
        x_label=config['x_label'],
        y_label=config['y_label'],
        category_field=category_field,
        category_label=config.get('category_label', category_field),
        forecast=config.get('forecast', False)
    )
