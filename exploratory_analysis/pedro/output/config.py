import pandas as pd
def csv_to_df(f): return pd.read_csv(__file__.replace('config.py', f'{f}.csv'))


config = [
    {
        'tab': 'Line charts',
        'items': [
            {
                'type': 'line',
                'title': 'Revenue by Segment',
                'description': 'Four segments shown as separate lines over time',
                'df': csv_to_df('multi_line'),
                'x_field': 'date',
                'x_label': 'Date',
                'category_field': 'region',
                'category_label': 'Regions',
                'category_area_highlight': ['North', 'West'],
                'y_field': 'value',
                'y_label': 'Revenue',
                # 'forecast': True
            },
            {
                'type': 'line',
                'title': 'Revenue by Segment',
                'description': 'Four segments shown as separate lines over time',
                'df': csv_to_df('multi_line'),
                'x_field': 'date',
                'x_label': 'Date',
                'category_field': 'region',
                'category_label': 'Regions',
                'y_field': 'value',
                'y_label': 'Revenue',
                # 'forecast': True
            },
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
                        'type': 'line',
                        'title': 'Revenue (invoice date)',
                        'description': 'Monthly revenue tracked by invoice date',
                        'df': csv_to_df('single_line'),
                        'x_field': 'date',
                        'x_label': 'Date',
                        'y_field': 'value',
                        'y_label': 'Revenue',
                        'reference_line': ('x', '2024-01-01', 'Fiscal Year Start')
                    },
                ]
            },

            {
                'columns': [
                    {
                        'type': 'line',
                        'title': 'Revenue (invoice date)',
                        'description': 'Monthly revenue tracked by invoice date',
                        'df': csv_to_df('single_line'),
                        'x_field': 'date',
                        'x_label': 'Date',
                        'y_field': 'value',
                        'y_label': 'Revenue',
                        'reference_line': ('y', 7500, 'Revenue Target')
                    },
                    {
                        'type': 'line',
                        'title': 'Revenue by Segment',
                        'description': 'Four segments shown as separate lines over time',
                        'df': csv_to_df('multi_line'),
                        'x_field': 'date',
                        'x_label': 'Date',
                        'category_field': 'region',
                        'category_label': 'Regions',
                        'category_area_highlight': ['North', 'South'],
                        'y_field': 'value',
                        'y_label': 'Revenue',
                        # 'forecast': True
                    },
                ]
            }
        ]
    },

    {
        'tab': 'Bar charts',
        'items': [
            {
                'columns': [
                    {
                        'type': 'bar',
                        'title': 'Quarterly effort',
                        'description': 'Quarterly effort as bars',
                        'df': csv_to_df('quarterly_effort'),
                        'x_field': 'completion_quarter_str',
                        'x_label': 'Quarter',
                        'y_field': 'avg_effort_per_project',
                        'y_label': 'Avg Effort',
                        'trendline': True,
                        # 'forecast': True
                    },
                    {
                        'type': 'bar',
                        'title': 'Revenue (bar)',
                        'description': 'Monthly revenue totals as bars',
                        'df': csv_to_df('bar'),
                        'x_field': 'date',
                        'x_label': 'Date',
                        'y_field': 'value',
                        'y_label': 'Revenue',
                        'trendline': True,
                        'orientation': 'horizontal',
                        # 'forecast': True
                    },
                ]
            },

            {
                'type': 'bar',
                'title': 'Revenue (bar)',
                'description': 'Monthly revenue totals as bars',
                'df': csv_to_df('multi_line'),
                'x_field': 'date',
                'x_label': 'Date',
                'category_field': 'region',
                'category_label': 'Regions',
                'y_field': 'value',
                'y_label': 'Revenue',
                # 'forecast': True
            },
        ]
    }
]
