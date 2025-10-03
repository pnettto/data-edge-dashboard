import pandas as pd
csv_to_df = lambda f: pd.read_csv(__file__.replace('config.py', f'{f}.csv'))

config = [
    {
        'tab': 'Sample charts',
        'items': [
             {
                'type': 'single_line',
                'title': 'Guillermo example',
                'description': 'Monthly revenue tracked by invoice date',
                'df': csv_to_df('single_line'),
                'x_field': 'date',
                'x_label': 'Date',
                'y_field': 'value',
                'y_label': 'Revenue'
            },
        ]
    },
]
