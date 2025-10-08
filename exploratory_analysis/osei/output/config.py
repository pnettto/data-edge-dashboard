import pandas as pd
import os

# Helper function to read CSVs from outputs folder
def csv_to_df(f):
    # Get the directory where this config.py file is located
    config_dir = os.path.dirname(os.path.abspath(__file__))
    # Look for CSV in outputs/ subfolder
    csv_path = os.path.join(config_dir, '', f'{f}.csv')
    return pd.read_csv(csv_path)

# Read KPIs for markdown
kpis = csv_to_df('utilization_kpis')
current_util = kpis[kpis['metric'] == 'Current Utilization']['value'].values[0]
target_util = kpis[kpis['metric'] == 'Target Utilization']['value'].values[0]
util_gap = kpis[kpis['metric'] == 'Gap to Target']['value'].values[0]
hours_needed = kpis[kpis['metric'] == 'Hours Needed']['value'].values[0]
revenue_opp = kpis[kpis['metric'] == 'Revenue Opportunity']['value'].values[0]

config = [
    {
        'tab': 'Utilization',
        'items': [
            # 1. KPI Summary Markdown
            {
                'columns': [
                    {
                        'type': 'markdown',
                        'content': f"""
                        **What is Utilization?**
                        
                        Utilization measures the percentage of total workforce hours spent on client-facing work. 
                        Our target is 80%, meaning 20% for internal activities (training, admin, vacation, etc.).
                        
                        **Why it matters:**
                        - Higher utilization = More revenue without hiring
                        - Low utilization = Wasted capacity and missed opportunities
                        - Optimal range: 80-95% (above 95% risks burnout)
                        """
                    },
                    {
                        'type': 'markdown',
                        'content': f"""
                        **Current State:**
                        
                        - **Current Utilization:** {current_util:.1%}
                        - **Target Utilization:** {target_util:.1%}
                        - **Gap to Target:** {util_gap:.1%}
                        
                        **Opportunity:**
                        - **Hours needed to reach target:** {hours_needed:,.0f} hours
                        - **Revenue opportunity:** ${revenue_opp:,.0f}
                        """
                    },
                ]
            },
            
            # 2. Monthly Utilization Trend
            {
                'type': 'line',
                'title': 'Monthly Utilization Trend',
                'description': 'Client-facing utilization over time (target: 80%)',
                'df': csv_to_df('monthly_utilization'),
                'x_field': 'month',
                'x_label': 'Month',
                'y_field': 'utilization',
                'y_label': 'Utilization %',
            },
            
            # 3. Employee Distribution by Category
            {
                'type': 'bar',
                'title': 'Employee Distribution by Utilization Category',
                'description': 'How many employees fall into each utilization range',
                'df': csv_to_df('employee_util_categories'),
                'x_field': 'category',
                'x_label': 'Utilization Category',
                'y_field': 'count',
                'y_label': 'Number of Employees',
            },
            
            # 4-5. Role Analysis (Side by Side)
            {
                'columns': [
                    {
                        'type': 'bar',
                        'title': 'Average Utilization by Role',
                        'description': 'Which roles have capacity?',
                        'df': csv_to_df('role_utilization'),
                        'x_field': 'role',
                        'x_label': 'Role Category',
                        'y_field': 'utilization',
                        'y_label': 'Avg Utilization %',
                    },
                    {
                        'type': 'bar',
                        'title': 'Total Hours by Role',
                        'description': 'Volume of work per role',
                        'df': csv_to_df('role_hours'),
                        'x_field': 'role',
                        'x_label': 'Role Category',
                        'y_field': 'hours',
                        'y_label': 'Total Hours',
                    },
                ]
            },
            
            # 6-7. Internal Time Analysis (Side by Side)
            {
                'columns': [
                    {
                        'type': 'bar',
                        'title': 'Internal Time Breakdown',
                        'description': 'Where are non-billable hours going?',
                        'df': csv_to_df('internal_time_breakdown'),
                        'x_field': 'category',
                        'x_label': 'Internal Category',
                        'y_field': 'hours',
                        'y_label': 'Total Hours',
                    },
                    {
                        'type': 'area',
                        'title': 'Internal Time Trend',
                        'description': 'Internal hours by category over time',
                        'df': csv_to_df('internal_time_trend'),
                        'x_field': 'month',
                        'x_label': 'Month',
                        'category_field': 'category',
                        'category_label': 'Internal Categories',
                        'y_field': 'hours',
                        'y_label': 'Hours',
                    },
                ]
            },
        ]
    }
]