import pandas as pd
def csv_to_df(f): return pd.read_csv(__file__.replace('config.py', f'{f}.csv'))


config = [
    {
        'tab': 'Sample charts',
        'items': [
            {
                'columns': [
                    {
                        'type': 'table',
                        'title': 'Sample table',
                        'description': 'Monthly revenue per segment totals as table',
                        'df': csv_to_df('single_line'),
                    },
                    {
                        'type': 'line',
                        'title': 'Guillermo example',
                        'description': 'Monthly revenue tracked by invoice date',
                        'df': csv_to_df('single_line'),
                        'x_field': 'date',
                        'x_label': 'Date',
                        'y_field': 'value',
                        'y_label': 'Revenue',
                        'forecast': True
                    },
                ]
            }

        ]
    },
]
