import pandas as pd
def csv_to_df(f): return pd.read_csv(__file__.replace('config.py', f'{f}.csv'))


config = [
    {
        'tab': 'Sample charts',
        'items': [
            {
                'columns': [
                    {
                        'type': 'markdown',
                        'title': 'Revenue Forecasting Overview',
                        'content': """
                        Revenue forecasting combines historical data analysis with market trends to predict future income streams. 

                        **Key Components:**
                        - Historical sales patterns and seasonality
                        - Market conditions and competitive landscape
                        - Product pipeline and pricing strategies

                        Accurate forecasts enable better resource allocation, budgeting decisions, and strategic planning. 
                        Regular model updates ensure predictions remain aligned with changing business conditions.
                        """
                    },

                    {
                        'type': 'single_line',
                        'title': 'Revenue (invoice date)',
                        'description': 'Monthly revenue tracked by invoice date',
                        'df': csv_to_df('single_line'),
                        'x_field': 'date',
                        'x_label': 'Date',
                        'y_field': 'value',
                        'y_label': 'Revenue',
                        'forecast': False
                    },
                ]
            },

            {
                'columns': [
                    {
                        'type': 'single_line',
                        'title': 'Revenue by Segment',
                        'description': 'Four segments shown as separate lines over time',
                        'df': csv_to_df('multi_line'),
                        'x_field': 'date',
                        'x_label': 'Date',
                        'category_field': 'series',
                        'y_field': 'value',
                        'y_label': 'Revenue',
                        'forecast': True
                    },
                    
                    {
                        'type': 'table',
                        'title': 'Sample table',
                        'description': 'Monthly revenue per segment totals as table',
                        'df': csv_to_df('multi_line'),
                    }                    
                ]
            }


        ]
    },

    {
        'tab': 'More samples',
        'items': [
            {
                'type': 'bar_forecast',
                'title': 'Revenue (bar)',
                'description': 'Monthly revenue totals as bars',
                'df': csv_to_df('bar'),
                'x_field': 'date',
                'x_label': 'Date',
                'y_field': 'value',
                'y_label': 'Revenue'
            },

            {
                'type': 'bar',
                'title': 'Revenue (bar)',
                'description': 'Monthly revenue totals as bars',
                'df': csv_to_df('bar'),
                'x_field': 'date',
                'x_label': 'Date',
                'y_field': 'value',
                'y_label': 'Revenue'
            },

            {
                'columns': [
                    {
                        'type': 'single_line',
                        'title': 'Revenue (invoice date)',
                        'description': 'Monthly revenue tracked by invoice date',
                        'df': csv_to_df('single_line'),
                        'x_field': 'date',
                        'x_label': 'Date',
                        'y_field': 'value',
                        'y_label': 'Revenue'
                    },

                    {
                        'type': 'single_line',
                        'title': 'Revenue (invoice date)',
                        'description': 'Monthly revenue tracked by invoice date',
                        'df': csv_to_df('single_line'),
                        'x_field': 'date',
                        'x_label': 'Date',
                        'y_field': 'value',
                        'y_label': 'Revenue'
                    },
                ]
            }
        ]
    }
]
