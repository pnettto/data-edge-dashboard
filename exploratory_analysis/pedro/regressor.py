import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
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

# Sliders in two columns
col1, col2 = st.columns(2)

with col1:
    future_investment = st.slider(
        "Set future monthly investment (for forecast)", 
        min_value=int(df['investment'].min()), 
        max_value=int(df['investment'].max()) + 2000, 
        value=int(df['investment'].iloc[-1]), 
        step=1000
    )

    future_sales_reps = st.slider(
        "Set future number of sales reps (for forecast)",
        min_value=int(df['sales_reps'].min()),
        max_value=int(df['sales_reps'].max()) + 5,
        value=int(df['sales_reps'].iloc[-1]),
        step=1
    )

with col2:
    future_ad_spend = st.slider(
        "Set future monthly ad spend (for forecast)",
        min_value=int(df['ad_spend'].min()),
        max_value=int(df['ad_spend'].max()) + 1000,
        value=int(df['ad_spend'].iloc[-1]),
        step=500
    )

    future_marketing_campaigns = st.slider(
        "Set future number of marketing campaigns (for forecast)",
        min_value=int(df['marketing_campaigns'].min()),
        max_value=int(df['marketing_campaigns'].max()) + 3,
        value=int(df['marketing_campaigns'].iloc[-1]),
        step=1
    )

periods = 24
future_dates = pd.date_range(start=df['date'].iloc[-1] + pd.offsets.MonthBegin(1), periods=periods, freq='MS')

# Use slider values for future periods
future_df = pd.DataFrame({'date': future_dates})
future_df['investment'] = future_investment
future_df['ad_spend'] = future_ad_spend
future_df['sales_reps'] = future_sales_reps
future_df['marketing_campaigns'] = future_marketing_campaigns

# Calculate forecast revenue using the same formula
trend = np.linspace(0, 8000, periods)
seasonality = np.sin(np.arange(periods) / 6 * 2 * np.pi) * 4000
future_df['value'] = (
    60000 +
    future_df['investment'] * 2.2 +
    future_df['ad_spend'] * 3.8 +
    future_df['sales_reps'] * 1600 +
    future_df['marketing_campaigns'] * 2200 +
    trend +
    seasonality
)
future_df['type'] = 'Forecast'

# Prepare historical for plotting
plot_df = df.copy()
plot_df['type'] = 'Actual'
plot_df = plot_df.rename(columns={'revenue': 'value'})
plot_df = plot_df[['date', 'value', 'investment', 'ad_spend', 'sales_reps', 'marketing_campaigns', 'type']]

combined_df = pd.concat([plot_df, future_df], ignore_index=True)

# Connector line
connector = pd.DataFrame({
    'date': [df['date'].iloc[-1], future_df['date'].iloc[0]],
    'value': [df['revenue'].iloc[-1], future_df['value'].iloc[0]],
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
    title='Revenue Over Time with Forecast'
)

dots = alt.Chart(combined_df).mark_point(size=60).encode(
    x='date:T',
    y='value:Q',
    color=alt.Color('type:N', scale=alt.Scale(domain=['Actual', 'Forecast'], range=['#1f77b4', '#ff7f0e'])),
    tooltip=['date', 'value', 'investment', 'ad_spend', 'sales_reps', 'marketing_campaigns', 'type']
)

connector_line = alt.Chart(connector).mark_line(strokeDash=[5,5], color='gray').encode(
    x='date:T',
    y='value:Q'
)

st.altair_chart(base + dots + connector_line, use_container_width=True)

st.subheader('Df with forecast')
st.dataframe(combined_df)

st.subheader('Historical data df')
st.dataframe(df)