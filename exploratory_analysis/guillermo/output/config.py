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
                        'df': csv_to_df('df_person_supply_agg'),
                    },
                    {
                        'type': 'line',
                        'title': 'Guillermo example',
                        'description': 'Monthly revenue tracked by invoice date',
                        'df': csv_to_df('df_person_supply_agg'),
                        'x_field': 'month',
                        'x_label': 'Month',
                        'y_field': 'recorded_supply_hours',
                        'y_label': 'Logged hours',
                        'category_field': 'person_seniority',
                        'category_label': 'Seniority',
                        #'forecast': True
                    },
                ]
            }

        ]
    },
]
