from ...utils import csv_to_df

configs = [
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
