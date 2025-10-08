import pandas as pd
def csv_to_df(f): return pd.read_csv(__file__.replace('config.py', f'{f}.csv'))


config = [
    {
        'tab': 'Docs',
        'items': [
            {
                'columns': [
                    {
                        'type': 'markdown',
                        'title': 'Chart Types & Configurations',
                        'content': """
                        This dashboard supports several chart types, each with customizable configuration options:

                        - **Line Chart** (`type: 'line'`): Visualizes trends over time. Supports single/multi-line, reference lines, and trendlines.
                        - **Bar Chart** (`type: 'bar'`): Compares values across categories or time. Supports vertical/horizontal orientation, grouped bars, reference lines, and trendlines.
                        - **Area Chart** (`type: 'area'`): Shows cumulative totals or stacked values across categories over time.
                        """
                    },
                    {
                        'type': 'markdown',
                        'title': 'Common Configuration Fields',
                        'content': """
                        - `df`: DataFrame source for the chart.
                        - `x_field`, `x_label`: Field and label for the x-axis.
                        - `y_field`, `y_label`: Field and label for the y-axis.
                        - `category_field`, `category_label`: For charts with multiple categories.
                        - `reference_line`: Tuple for axis reference markers, e.g. `('y', 7500, 'Target')`.
                        - `trendline`: Boolean to add a regression line.
                        - `orientation`: `'horizontal'` for horizontal bar charts.

                        See each example below for specific configurations.
                        """
                    }
                ]
            },

            {
                'columns': [
                    {
                        'type': 'line',
                        'title': 'Simple Line Chart with Forecast',
                        'description': 'Single line chart with forecasted values',
                        'df': csv_to_df('single_line'),
                        'x_field': 'date',
                        'x_label': 'Date',
                        'y_field': 'value',
                        'y_label': 'Revenue',
                        'forecast': True,
                    },
                    {
                        'type': 'markdown',
                        'title': 'Config',
                        'content': """
                        ```
                        {
                            'type': 'line',
                            'title': 'Simple Line Chart with Forecast',
                            'description': 'Single line chart with forecasted values',
                            'df': your_df,
                            'x_field': 'date',
                            'x_label': 'Date',
                            'y_field': 'value',
                            'y_label': 'Revenue',
                            'forecast': True,
                        },
                        
                        ```

                        **Prophet** is an open-source forecasting library developed by Meta (Facebook) for time series data. It is designed to handle missing data, outliers, and seasonal effects with minimal configuration.

                        - **Usage**: Prophet can be used to forecast future values in your time series charts. Simply set `'forecast': True` in your chart config.
                        - **Features**: Automatic trend detection, seasonality modeling, and support for holidays/events.
                        """
                    },
                ]
            },

            {
                'columns': [
                    {
                        'type': 'line',
                        'title': 'Multi-line with Area Highlight',
                        'description': 'Multiple lines with highlighted area for selected categories',
                        'df': csv_to_df('multi_line'),
                        'x_field': 'date',
                        'x_label': 'Date',
                        'category_field': 'region',
                        'category_label': 'Regions',
                        'category_area_highlight': ['North', 'West'],
                        'y_field': 'value',
                        'y_label': 'Revenue',
                    },
                    {
                        'type': 'markdown',
                        'title': 'Config',
                        'content': """
                        ```
                        {
                            'type': 'line',
                            'title': 'Multi-line with Area Highlight',
                            'description': 'Multiple lines with highlighted area for selected categories',
                            'df': your_df,
                            'x_field': 'date',
                            'x_label': 'Date',
                            'category_field': 'region',
                            'category_label': 'Regions',
                            'category_area_highlight': ['North', 'West'],
                            'y_field': 'value',
                            'y_label': 'Revenue',
                        },
                        ```
                        """
                    },
                ]
            },


            {
                'columns': [
                    {
                        'type': 'line',
                        'title': 'Multi-line Chart',
                        'description': 'Multiple categories shown as separate lines over time',
                        'df': csv_to_df('multi_line'),
                        'x_field': 'date',
                        'x_label': 'Date',
                        'category_field': 'region',
                        'category_label': 'Regions',
                        'y_field': 'value',
                        'y_label': 'Revenue',
                    },
                    {
                        'type': 'markdown',
                        'title': 'Config',
                        'content': """
                        ```
                        {
                            'type': 'line',
                            'title': 'Multi-line Chart',
                            'description': 'Multiple categories shown as separate lines over time',
                            'df': your_df,
                            'x_field': 'date',
                            'x_label': 'Date',
                            'category_field': 'region',
                            'category_label': 'Regions',
                            'y_field': 'value',
                            'y_label': 'Revenue',
                        },
                        ```
                        """
                    },
                ]
            },

            {
                'columns': [
                    {
                        'type': 'line',
                        'title': 'Line Chart with X-axis Reference Line',
                        'description': 'Single line with vertical reference marker',
                        'df': csv_to_df('single_line'),
                        'x_field': 'date',
                        'x_label': 'Date',
                        'y_field': 'value',
                        'y_label': 'Revenue',
                        'reference_line': ('x', '2024-05-01', 'Fiscal Year Start')
                    },
                    {
                        'type': 'markdown',
                        'title': 'Config',
                        'content': """
                        ```
                        {
                            'type': 'line',
                            'title': 'Line Chart with X-axis Reference Line',
                            'description': 'Single line with vertical reference marker',
                            'df': your_df,
                            'x_field': 'date',
                            'x_label': 'Date',
                            'y_field': 'value',
                            'y_label': 'Revenue',
                            'reference_line': ('x', '2024-05-01', 'Fiscal Year Start')
                        },
                        ```
                        """
                    },
                ]
            },

            {
                'columns': [
                    {
                        'type': 'line',
                        'title': 'Line Chart with Y-axis Reference Line',
                        'description': 'Single line with horizontal reference target',
                        'df': csv_to_df('single_line'),
                        'x_field': 'date',
                        'x_label': 'Date',
                        'y_field': 'value',
                        'y_label': 'Revenue',
                        'reference_line': ('y', 7500, 'Revenue Target')
                    },
                    {
                        'type': 'markdown',
                        'title': 'Config',
                        'content': """
                        ```
                        {
                            'type': 'line',
                            'title': 'Line Chart with Y-axis Reference Line',
                            'description': 'Single line with horizontal reference target',
                            'df': your_df,
                            'x_field': 'date',
                            'x_label': 'Date',
                            'y_field': 'value',
                            'y_label': 'Revenue',
                            'reference_line': ('y', 7500, 'Revenue Target')
                        },
                        ```
                        """
                    },
                ]
            },
            {
                'columns': [
                    {
                        'type': 'line',
                        'title': 'Line Chart with Trendline',
                        'description': 'Single line with linear regression trendline',
                        'df': csv_to_df('single_line'),
                        'x_field': 'date',
                        'x_label': 'Date',
                        'y_field': 'value',
                        'y_label': 'Revenue',
                        'trendline': True,
                    },
                    {
                        'type': 'markdown',
                        'title': 'Config',
                        'content': """
                        ```
                        {
                            'type': 'line',
                            'title': 'Line Chart with Trendline',
                            'description': 'Single line with linear regression trendline',
                            'df': your_df,
                            'x_field': 'date',
                            'x_label': 'Date',
                            'y_field': 'value',
                            'y_label': 'Revenue',
                            'trendline': True,
                        },
                        ```
                        """
                    },
                ]
            },

            {
                'columns': [
                    {
                        'type': 'bar',
                        'title': 'Single Bar Chart with Forecast',
                        'description': 'Single bar chart with forecasted values',
                        'df': csv_to_df('single_line'),
                        'x_field': 'date',
                        'x_label': 'Date',
                        'y_field': 'value',
                        'y_label': 'Revenue',
                        'forecast': True,
                    },
                    {
                        'type': 'markdown',
                        'title': 'Config',
                        'content': """
                        ```
                        {
                            'type': 'bar',
                            'title': 'Single Bar Chart with Forecast',
                            'description': 'Single bar chart with forecasted values',
                            'df': your_df,
                            'x_field': 'date',
                            'x_label': 'Date',
                            'y_field': 'value',
                            'y_label': 'Revenue',
                            'forecast': True,
                        },
                        ```
                        """
                    },
                ]
            },

            {
                'columns': [
                    {
                        'type': 'bar',
                        'title': 'Bar Chart with Trendline',
                        'description': 'Vertical bars with linear regression trendline',
                        'df': csv_to_df('quarterly_effort'),
                        'x_field': 'completion_quarter_str',
                        'x_label': 'Quarter',
                        'y_field': 'avg_effort_per_project',
                        'y_label': 'Avg Effort',
                        'trendline': True,
                    },
                    {
                        'type': 'markdown',
                        'title': 'Config',
                        'content': """
                        ```
                        {
                            'type': 'bar',
                            'title': 'Bar Chart with Trendline',
                            'description': 'Vertical bars with linear regression trendline',
                            'df': your_df,
                            'x_field': 'completion_quarter_str',
                            'x_label': 'Quarter',
                            'y_field': 'avg_effort_per_project',
                            'y_label': 'Avg Effort',
                            'trendline': True,
                        },
                        ```
                        """
                    },
                ]
            },
            {
                'columns': [
                    {
                        'type': 'bar',
                        'title': 'Horizontal Bar Chart',
                        'description': 'Bar chart with horizontal orientation',
                        'df': csv_to_df('bar'),
                        'x_field': 'date',
                        'x_label': 'Date',
                        'y_field': 'value',
                        'y_label': 'Revenue',
                        'orientation': 'horizontal',
                    },
                    {
                        'type': 'markdown',
                        'title': 'Config',
                        'content': """
                        ```
                        {
                            'type': 'bar',
                            'title': 'Horizontal Bar Chart',
                            'description': 'Bar chart with horizontal orientation',
                            'df': your_df,
                            'x_field': 'date',
                            'x_label': 'Date',
                            'y_field': 'value',
                            'y_label': 'Revenue',
                            'orientation': 'horizontal',
                        },
                        ```
                        """
                    },
                ]
            },

            {
                'columns': [
                    {
                        'type': 'bar',
                        'title': 'Bar Chart with Y-axis Reference Line',
                        'description': 'Vertical bars with horizontal reference target',
                        'df': csv_to_df('bar'),
                        'x_field': 'date',
                        'x_label': 'Date',
                        'y_field': 'value',
                        'y_label': 'Revenue',
                        'reference_line': ('y', 7500, 'Revenue Target')
                    },
                    {
                        'type': 'markdown',
                        'title': 'Config',
                        'content': """
                        ```
                        {
                            'type': 'bar',
                            'title': 'Bar Chart with Y-axis Reference Line',
                            'description': 'Vertical bars with horizontal reference target',
                            'df': your_df,
                            'x_field': 'date',
                            'x_label': 'Date',
                            'y_field': 'value',
                            'y_label': 'Revenue',
                            'reference_line': ('y', 7500, 'Revenue Target')
                        },
                        ```
                        """
                    },
                ]
            },
            {
                'columns': [
                    {
                        'type': 'bar',
                        'title': 'Bar Chart with X-axis Reference Line',
                        'description': 'Vertical bars with vertical reference marker',
                        'df': csv_to_df('bar'),
                        'x_field': 'date',
                        'x_label': 'Date',
                        'y_field': 'value',
                        'y_label': 'Revenue',
                        'reference_line': ('x', '2024-05-01', 'Fiscal Year Start')
                    },
                    {
                        'type': 'markdown',
                        'title': 'Config',
                        'content': """
                        ```
                        {
                            'type': 'bar',
                            'title': 'Bar Chart with X-axis Reference Line',
                            'description': 'Vertical bars with vertical reference marker',
                            'df': your_df,
                            'x_field': 'date',
                            'x_label': 'Date',
                            'y_field': 'value',
                            'y_label': 'Revenue',
                            'reference_line': ('x', '2024-05-01', 'Fiscal Year Start')
                        },
                        ```
                        """
                    },
                ]
            },

            {
                'columns': [
                    {
                        'type': 'bar',
                        'title': 'Grouped Bar Chart',
                        'description': 'Multiple categories shown as grouped bars',
                        'df': csv_to_df('multi_line'),
                        'x_field': 'date',
                        'x_label': 'Date',
                        'category_field': 'region',
                        'category_label': 'Regions',
                        'y_field': 'value',
                        'y_label': 'Revenue',
                    },
                    {
                        'type': 'markdown',
                        'title': 'Config',
                        'content': """
                        ```
                        {
                            'type': 'bar',
                            'title': 'Grouped Bar Chart',
                            'description': 'Multiple categories shown as grouped bars',
                            'df': your_df,
                            'x_field': 'date',
                            'x_label': 'Date',
                            'category_field': 'region',
                            'category_label': 'Regions',
                            'y_field': 'value',
                            'y_label': 'Revenue',
                        },
                        ```
                        """
                    },
                ]
            },

            {
                'columns': [
                    {
                        'type': 'area',
                        'title': 'Stacked Area Chart',
                        'description': 'Stacked area showing multiple categories',
                        'df': csv_to_df('multi_line'),
                        'x_field': 'date',
                        'x_label': 'Date',
                        'category_field': 'region',
                        'category_label': 'Region',
                        'y_field': 'value',
                        'y_label': 'Revenue',
                    },
                    {
                        'type': 'markdown',
                        'title': 'Config',
                        'content': """
                        ```
                        {
                            'type': 'area',
                            'title': 'Stacked Area Chart with Forecast',
                            'description': 'Stacked area showing multiple categories with forecast visualization',
                            'df': your_df,
                            'x_field': 'date',
                            'x_label': 'Date',
                            'category_field': 'region',
                            'category_label': 'Region',
                            'y_field': 'value',
                            'y_label': 'Revenue',
                        },
                        ```
                        """
                    },
                ],
            },
        ]
    },
]
