from pathlib import Path
import pandas as pd

HERE = Path(__file__).resolve()
def csv_to_df(name): 
    return pd.read_csv(HERE.parent / f"{name}.csv")

INTRO_RS = """
**Why this matters**
- Track growth, cash timing, and reliance on brokers (goal: increase **Direct** share).

**What you’re seeing**
- **Revenue (net)** by invoice month.
- **Cash-in** by final pay month (includes VAT).
- **Channel mix**: Direct vs Brokered.

**Insights**
- Revenue shows trend & seasonality; cash-in usually lags → collections timing.
- Brokered currently leads → opportunity to grow **Direct**.
"""

config = [
    {
        'tab': 'Revenue & Sales',
        'items': [
            {
                'type': 'markdown',
                'content': INTRO_RS,
            },
            {
                'columns': [
                    {
                        'type': 'line',
                        'title': 'Revenue',
                        'description': 'Monthly revenue summed by invoice date',
                        'df': csv_to_df('revenue_monthly'),
                        'x_field': 'date',
                        'x_label': 'Month',
                        'y_field': 'revenue',
                        'y_label': 'Revenue (SEK)',
                        'trendline': True,
                    },
                    {
                        'type': 'line',
                        'title': 'Cash-in',
                        'description': 'Monthly cash flow summed by final pay date',
                        'df': csv_to_df('cash_in_monthly'),
                        'x_field': 'date',
                        'x_label': 'Month',
                        'y_field': 'cash',
                        'y_label': 'Cash-in (SEK)',
                        'trendline': True,
                    },
                ]
            },
            {
                'type': 'line',
                'title': 'Sales — Direct vs Brokered',
                'description': 'Monthly invoice revenue split by channel (net)',
                'df': csv_to_df('sales_brokered_vs_direct_monthly'),
                'x_field': 'month',
                'x_label': 'Month',
                'category_field': 'channel',
                'category_label': 'Type',
                'y_field': 'revenue',
                'y_label': 'Revenue (SEK)',
                'trendline': True,
            },
        ]
    }
]
