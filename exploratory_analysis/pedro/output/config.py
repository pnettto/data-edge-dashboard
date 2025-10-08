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
                'forecast': True
            },

            {
                'columns': [
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
                ]
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
                        'reference_line': ('x', '2024-05-01', 'Fiscal Year Start')
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
                        'title': 'Revenue (invoice date)',
                        'description': 'Monthly revenue tracked by invoice date',
                        'df': csv_to_df('single_line'),
                        'x_field': 'date',
                        'x_label': 'Date',
                        'y_field': 'value',
                        'y_label': 'Revenue',
                        'trendline': True,
                    },
                ]
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
                        'orientation': 'horizontal',
                    },
                ]
            },

            {
                'columns': [
                    {
                        'type': 'bar',
                        'title': 'Revenue with Y-axis Target',
                        'description': 'Bar chart with horizontal reference line',
                        'df': csv_to_df('bar'),
                        'x_field': 'date',
                        'x_label': 'Date',
                        'y_field': 'value',
                        'y_label': 'Revenue',
                        'reference_line': ('y', 7500, 'Revenue Target')
                    },
                    {
                        'type': 'bar',
                        'title': 'Revenue with X-axis Marker',
                        'description': 'Bar chart with vertical reference line',
                        'df': csv_to_df('bar'),
                        'x_field': 'date',
                        'x_label': 'Date',
                        'y_field': 'value',
                        'y_label': 'Revenue',
                        'reference_line': ('x', '2024-05-01', 'Fiscal Year Start')
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
    },

    {
        'tab': 'Area charts',
        'items': [
            {
                'type': 'area',
                'title': 'Revenue by Product (Stacked)',
                'description': 'Stacked area chart showing revenue contribution by product over time',
                'df': csv_to_df('stacked_area'),
                'x_field': 'date',
                'x_label': 'Date',
                'category_field': 'category',
                'category_label': 'Product',
                'y_field': 'value',
                'y_label': 'Revenue',
            },

            {
                'columns': [
                    {
                        'type': 'area',
                        'title': 'Revenue by Product with Target',
                        'description': 'Stacked area with reference line',
                        'df': csv_to_df('stacked_area'),
                        'x_field': 'date',
                        'x_label': 'Date',
                        'category_field': 'category',
                        'category_label': 'Product',
                        'y_field': 'value',
                        'y_label': 'Revenue',
                        'reference_line': ('y', 4000, 'Total Revenue Target')
                    },
                    {
                        'type': 'markdown',
                        'title': 'Stacked Area Charts',
                        'content': """
                        Stacked area charts show the evolution of multiple categories over time, 
                        making it easy to see both individual trends and the total.

                        **Use cases:**
                        - Product revenue composition
                        - Resource allocation over time
                        - Market share evolution

                        The total height represents the sum of all categories at each point in time.
                        """
                    },
                ]
            },

            {
                'type': 'area',
                'title': 'Revenue by Region (Stacked)',
                'description': 'Regional revenue contribution over time',
                'df': csv_to_df('multi_line'),
                'x_field': 'date',
                'x_label': 'Date',
                'category_field': 'region',
                'category_label': 'Region',
                'y_field': 'value',
                'y_label': 'Revenue',
            },
        ]
    }
]
