from pathlib import Path
import pandas as pd


def make_df(filename):
    # Pass in the same folder csv file name ("example" if "example.csv")
    HERE = Path(__file__).parent
    return pd.read_csv(HERE / f"{filename}.csv")


configs = [
    {
        'tab': 'Sample charts',
        'items': [
            {
                'type': 'multi_line',
                'title': 'Revenue by Segment (multi-line)',
                'description': 'Four segments shown as separate lines over time',
                'df': make_df('multi_line'),
                'x_field': 'date',
                'x_label': 'Date',
                'category_field': 'series',
                'y_field': 'value',
                'y_label': 'Revenue'
             },

             {
                'type': 'single_line',
                'title': 'Revenue (invoice date)',
                'description': 'Monthly revenue tracked by invoice date',
                'df': make_df('single_line'),
                'x_field': 'date',
                'x_label': 'Date',
                'y_field': 'value',
                'y_label': 'Revenue'
            },
        ]
    },

    {
        'tab': 'More samples',
        'items': [
            {
                'type': 'bar',
                'title': 'Revenue (bar)',
                'description': 'Monthly revenue totals as bars',
                'df': make_df('bar'),
                'x_field': 'date',
                'x_label': 'Date',
                'y_field': 'value',
                'y_label': 'Revenue'
            },

            {
                'columns': [
                    {
                        'type': 'bar',
                        'title': 'Revenue (bar)',
                        'description': 'Monthly revenue totals as bars',
                        'df': make_df('bar'),
                        'x_field': 'date',
                        'x_label': 'Date',
                        'y_field': 'value',
                        'y_label': 'Revenue'
                    },

                    {
                        'type': 'single_line',
                        'title': 'Revenue (invoice date)',
                        'description': 'Monthly revenue tracked by invoice date',
                        'df': make_df('single_line'),
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
