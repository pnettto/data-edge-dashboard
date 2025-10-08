from pathlib import Path
import pandas as pd

HERE = Path(__file__).resolve()
def csv_to_df(name): return pd.read_csv(HERE.parent / f"{name}.csv")

config = [
    {
        'tab': 'Revenue & Sales',
        'items': [
            {
                'type': 'line',
                'title': 'Revenue',
                'description': 'Monthly revenue summed by invoice date',
                'df': csv_to_df('revenue_monthly'),
                'x_field': 'date',
                'x_label': 'Month',
                'y_field': 'revenue',
                'y_label': 'Revenue (SEK)',
                'trendline': True
            },
            {
                'type': 'line',
                'title': 'Cash-in (Monthly)',
                'description': 'Monthly cash flow summed by final pay date',
                'df': csv_to_df('cash_in_monthly'),
                'x_field': 'date',
                'x_label': 'Month',
                'y_field': 'cash',
                'y_label': 'Cash-in (SEK)',
                'trendline': True
            }
        ]
    }
]
