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
            },

             {
                'type': 'line',
                'title': 'Workload vs. Capacity Over Time',
                'description': 'Comparison of potential capacity, defined work, and recorded work hours.',
                'df': csv_to_df('df_combined'),
                'x_field': 'month',
                'x_label': 'Month',
                'category_field': 'metric_type',
                'category_label': 'Metric',
                'category_area_highlight': ['recorded_logged_hours', 'defined_role_hours'],
                'y_field': 'hours',
                'y_label': 'Total Hours per Month',
            },

            {
                'type': 'bar',
                'title': 'Revenue (bar)',
                'description': 'Monthly revenue totals as bars',
                'df': csv_to_df('utilization_by_seniority'),
                'x_field': 'seniority',
                'x_label': 'Seniority',            
                'y_field': 'logged_based_utilization',
                'y_label': 'Utilization',
                # 'forecast': True
            },
            {
                'type': 'line',
                'title': 'Utilization by Seniority',
                'description': 'Logged Utilization over time by seniority',
                'df': csv_to_df('monthly_logged_utilization'),
                'x_field': 'month',
                'x_label': 'Month',
                'y_field': 'logged_based_utilization',
                'y_label': 'Utilization',
                'category_field': 'seniority',
                'category_label': 'Seniority'
            },

        ]
    },
]
