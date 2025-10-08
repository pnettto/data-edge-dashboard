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
                'title': 'Revenue (invoice date, net)',
                'description': 'Monthly revenue summed by invoice date',
                'df': csv_to_df('revenue_monthly'),
                'x_field': 'date',
                'x_label': 'Month',
                'y_field': 'revenue',
                'y_label': 'Revenue'
            }
        ]
    }
]

