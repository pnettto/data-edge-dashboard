from pathlib import Path
import pandas as pd

HERE = Path(__file__).parent
example_df = pd.read_csv(HERE / "example.csv")

chart_configs = [
    {
        'type': 'single_line',
        'title': 'Revenue by Segment (multi-line)',
        'description': 'Four segments shown as separate lines over time',
        'df': example_df,
        'x_field': 'Month',
        'x_label': 'Month',
        'category_field': 'series',
        'y_field': 'Sales',
        'y_label': 'Sales'
    }
]