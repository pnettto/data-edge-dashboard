import streamlit as st
import pandas as pd
import numpy as np
from prophet import Prophet
import altair as alt
from datetime import datetime, timedelta

# Set page config
st.set_page_config(layout="wide")

# Set seed for reproducibility
np.random.seed(42)

# Generate mock historical data
def generate_historical_data():
    # Manually create 36 months of realistic data for a marketing agency with 15 employees
    months = pd.date_range(start='2022-01-01', periods=36, freq='MS')
    base_investment = 12000 + np.linspace(0, 3000, 36)
    investment = base_investment + np.sin(np.arange(36) / 6 * 2 * np.pi) * 800 + np.random.normal(0, 350, 36)

    base_ad_spend = 3500 + np.linspace(0, 900, 36)
    ad_spend = base_ad_spend + np.sin(np.arange(36) / 12 * 2 * np.pi) * 400 + np.random.normal(0, 180, 36)

    sales_reps = 7 + np.round(np.linspace(0, 7, 36) + np.sin(np.arange(36) / 12 * 2 * np.pi) * 1.5 + np.random.normal(0, 0.7, 36)).astype(int)

    marketing_campaigns = 2 + np.round(np.linspace(0, 5, 36) + np.sin(np.arange(36) / 6 * 2 * np.pi) * 1.2 + np.random.normal(0, 0.5, 36)).astype(int)

    data = {
        'date': months,
        'investment': investment.round(0).astype(int),
        'ad_spend': ad_spend.round(0).astype(int),
        'sales_reps': sales_reps,
        'marketing_campaigns': marketing_campaigns
    }
    df = pd.DataFrame(data)
    # Realistic revenue calculation
    df['revenue'] = (
        60000 +
        df['investment'] * 2.2 +
        df['ad_spend'] * 3.8 +
        df['sales_reps'] * 1600 +
        df['marketing_campaigns'] * 2200 +
        np.linspace(0, 8000, 36) +  # slow growth trend
        np.sin(np.arange(36) / 6 * 2 * np.pi) * 4000  # seasonality
    )
    return df



df = generate_historical_data()

# Sidebar controls
st.sidebar.header("Forecast Settings")
variable = st.sidebar.selectbox(
    "Select variable to control for forecast",
    ["sales_reps", "investment", "ad_spend", "marketing_campaigns"]
)

if variable == "sales_reps":
    slider_value = st.sidebar.slider(
        "Number of Sales Reps for Forecast",
        min_value=int(df['sales_reps'].min()),
        max_value=int(df['sales_reps'].max()) + 5,
        value=int(df['sales_reps'].iloc[-1]),
        step=1
    )
elif variable == "investment":
    slider_value = st.sidebar.slider(
        "Investment Amount for Forecast",
        min_value=int(df['investment'].min()),
        max_value=int(df['investment'].max()) + 5000,
        value=int(df['investment'].iloc[-1]),
        step=500
    )
elif variable == "ad_spend":
    slider_value = st.sidebar.slider(
        "Ad Spend Amount for Forecast",
        min_value=int(df['ad_spend'].min()),
        max_value=int(df['ad_spend'].max()) + 2000,
        value=int(df['ad_spend'].iloc[-1]),
        step=100
    )
elif variable == "marketing_campaigns":
    slider_value = st.sidebar.slider(
        "Marketing Campaigns for Forecast",
        min_value=int(df['marketing_campaigns'].min()),
        max_value=int(df['marketing_campaigns'].max()) + 5,
        value=int(df['marketing_campaigns'].iloc[-1]),
        step=1
    )

# Prophet forecast with selected regressor
prophet_df = df[['date', 'revenue', 'sales_reps', 'investment', 'ad_spend', 'marketing_campaigns']].rename(columns={'date': 'ds', 'revenue': 'y'})
model = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False)
model.add_regressor(variable)
model.fit(prophet_df)

future = model.make_future_dataframe(periods=24, freq='MS')
for col in ['sales_reps', 'investment', 'ad_spend', 'marketing_campaigns']:
    if col == variable:
        future[col] = list(df[col]) + [slider_value] * 24
    else:
        future[col] = list(df[col]) + [df[col].iloc[-1]] * 24

forecast = model.predict(future)
forecast_df = forecast[['ds', 'yhat']].tail(24).rename(columns={'ds': 'date', 'yhat': 'forecast_revenue'})

# Combine for plotting
plot_df = df.copy()
plot_df['type'] = 'Actual'
forecast_df['investment'] = future['investment'].tail(24).values
forecast_df['ad_spend'] = future['ad_spend'].tail(24).values
forecast_df['sales_reps'] = future['sales_reps'].tail(24).values
forecast_df['marketing_campaigns'] = future['marketing_campaigns'].tail(24).values
forecast_df['type'] = 'Forecast'
forecast_df = forecast_df[['date', 'forecast_revenue', 'investment', 'ad_spend', 'sales_reps', 'marketing_campaigns', 'type']]
plot_df = plot_df[['date', 'revenue', 'investment', 'ad_spend', 'sales_reps', 'marketing_campaigns', 'type']]
plot_df = plot_df.rename(columns={'revenue': 'value'})
forecast_df = forecast_df.rename(columns={'forecast_revenue': 'value'})
combined_df = pd.concat([plot_df, forecast_df], ignore_index=True)

# Connector line
connector = pd.DataFrame({
    'date': [df['date'].iloc[-1], forecast_df['date'].iloc[0]],
    'value': [df['revenue'].iloc[-1], forecast_df['value'].iloc[0]],
    'type': ['Connector', 'Connector'],
    'investment': [np.nan, np.nan],
    'ad_spend': [np.nan, np.nan],
    'sales_reps': [np.nan, np.nan],
    'marketing_campaigns': [np.nan, np.nan]
})

# Plot
base = alt.Chart(combined_df).mark_line().encode(
    x='date:T',
    y='value:Q',
    color=alt.Color('type:N', scale=alt.Scale(domain=['Actual', 'Forecast'], range=['#1f77b4', '#ff7f0e'])),
    tooltip=['date', 'value', 'investment', 'ad_spend', 'sales_reps', 'marketing_campaigns', 'type']
).properties(
    width=900,
    height=400,
    title='Revenue Over Time with Prophet Forecast'
)

dots = alt.Chart(combined_df).mark_point(size=60).encode(
    x='date:T',
    y='value:Q',
    color=alt.Color('type:N', scale=alt.Scale(domain=['Actual', 'Forecast'], range=['#1f77b4', '#ff7f0e'])),
    tooltip=['date', 'value', 'investment', 'ad_spend', 'sales_reps', 'marketing_campaigns', 'type']
)

connector_line = alt.Chart(connector).mark_line(color='#ff7f0e').encode(
    x='date:T',
    y='value:Q'
)

st.altair_chart(base + dots + connector_line, use_container_width=True)

st.dataframe(generate_historical_data())