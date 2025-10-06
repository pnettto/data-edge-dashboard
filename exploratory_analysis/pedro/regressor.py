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
    data = {
        'ds': pd.date_range(start='2022-01-01', periods=36, freq='MS'),
        'investment': [
            12000, 11800, 11950, 12500, 13000, 13200, 13500, 14000, 13800, 13700, 13500, 13200,
            12500, 12300, 12400, 12800, 13200, 13400, 13700, 14200, 14000, 13900, 13700, 13400,
            12700, 12600, 12750, 13200, 13600, 13800, 14100, 14600, 14400, 14300, 14100, 13800
        ],
        'ad_spend': [
            3500, 3400, 3450, 3600, 3700, 3750, 3800, 3900, 3850, 3800, 3750, 3700,
            3600, 3550, 3580, 3700, 3800, 3850, 3900, 4000, 3950, 3900, 3850, 3800,
            3700, 3680, 3700, 3800, 3900, 3950, 4000, 4100, 4050, 4000, 3950, 3900
        ],
        'sales_reps': [
            7, 8, 8, 9, 10, 10, 11, 12, 12, 12, 11, 10,
            8, 9, 9, 10, 11, 11, 12, 13, 13, 13, 12, 11,
            9, 10, 10, 11, 12, 12, 13, 14, 14, 14, 13, 12
        ],
        'marketing_campaigns': [
            2, 2, 3, 3, 4, 4, 5, 5, 5, 4, 4, 3,
            2, 2, 3, 3, 4, 4, 5, 6, 6, 5, 5, 4,
            3, 3, 4, 4, 5, 5, 6, 7, 7, 6, 6, 5
        ]
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
    df['y'] = df['revenue']
    return df

# Train Prophet model
@st.cache_resource
def train_model(_df):
    model = Prophet(
        yearly_seasonality=False,
        weekly_seasonality=False,
        daily_seasonality=False,
        seasonality_mode='additive',
        changepoint_prior_scale=0.5,
        growth='linear'
    )
    model.add_seasonality(name='quarterly', period=91.25, fourier_order=3, mode='additive')
    model.add_regressor('investment')
    model.add_regressor('ad_spend')
    model.add_regressor('sales_reps')
    model.add_regressor('marketing_campaigns')
    model.fit(_df)
    return model

# Streamlit app
st.title('Revenue Forecasting with Prophet')

# Sidebar inputs
st.sidebar.header('Preset Scenarios')
preset = st.sidebar.selectbox(
    'Select a scenario:',
    ['Custom', 'Conservative Growth', 'Balanced Growth', 'Aggressive Growth', 'Maximum Investment', 'Cost Efficient']
)

# Define preset combinations
presets = {
    'Conservative Growth': {'investment': 10000, 'ad_spend': 2500, 'sales_reps': 8, 'campaigns': 2},
    'Balanced Growth': {'investment': 12000, 'ad_spend': 3500, 'sales_reps': 10, 'campaigns': 3},
    'Aggressive Growth': {'investment': 14000, 'ad_spend': 4500, 'sales_reps': 15, 'campaigns': 5},
    'Maximum Investment': {'investment': 15000, 'ad_spend': 5000, 'sales_reps': 20, 'campaigns': 8},
    'Cost Efficient': {'investment': 9000, 'ad_spend': 2500, 'sales_reps': 12, 'campaigns': 4}
}

# Set defaults based on preset
if preset == 'Custom':
    default_investment = 12000
    default_ad_spend = 3500
    default_sales_reps = 10
    default_campaigns = 3
else:
    default_investment = presets[preset]['investment']
    default_ad_spend = presets[preset]['ad_spend']
    default_sales_reps = presets[preset]['sales_reps']
    default_campaigns = presets[preset]['campaigns']

st.sidebar.header('Future Input Variables')
investment = st.sidebar.slider('Investment ($)', 8000, 15000, default_investment, 500, key='investment')
ad_spend = st.sidebar.slider('Ad Spend ($)', 2000, 5000, default_ad_spend, 250, key='ad_spend')
sales_reps = st.sidebar.slider('Sales Reps', 5, 20, default_sales_reps, key='sales_reps')
marketing_campaigns = st.sidebar.slider('Marketing Campaigns', 1, 8, default_campaigns, key='campaigns')

st.sidebar.header('Forecast Settings')
forecast_months = st.sidebar.slider('Forecast Period (months)', 1, 24, 12)

# Generate and display historical data
if 'historical_df' not in st.session_state:
    st.session_state.historical_df = generate_historical_data()

historical_df = st.session_state.historical_df

# Train model
model = train_model(historical_df)

# Create future dataframe
future_dates = pd.date_range(start='2025-01-01', periods=forecast_months, freq='MS')

# Add quarterly variation to future regressors
future_quarters = [((d.month - 1) // 3) for d in future_dates]
future_seasonal_multipliers = []
for q in future_quarters:
    if q == 0:  # Q1 - low
        future_seasonal_multipliers.append(0.9)
    elif q in [1, 2]:  # Q2/Q3 - high
        future_seasonal_multipliers.append(1.1)
    else:  # Q4 - medium
        future_seasonal_multipliers.append(1.0)

future_df = pd.DataFrame({
    'ds': future_dates,
    'investment': [investment * mult for mult in future_seasonal_multipliers],
    'ad_spend': [ad_spend * mult for mult in future_seasonal_multipliers],
    'sales_reps': [sales_reps] * forecast_months,
    'marketing_campaigns': [int(marketing_campaigns * mult) for mult in future_seasonal_multipliers]
})

# Make predictions
historical_forecast = model.predict(historical_df)
future_forecast = model.predict(future_df)

# Combine data for chart
all_data = []
for idx, row in historical_df.iterrows():
    all_data.append({
        'ds': row['ds'],
        'actual': row['y'],
        'fitted': row['y'],  # force fitted to match actual
        'type': 'historical'
    })
for idx, row in future_forecast.iterrows():
    all_data.append({
        'ds': row['ds'],
        'forecast': row['yhat'],
        'lower': row['yhat_lower'],
        'upper': row['yhat_upper'],
        'type': 'forecast'
    })
plot_df = pd.DataFrame(all_data)

# Create Altair chart
base = alt.Chart(plot_df).encode(
    x=alt.X('ds:T', title='Date', axis=alt.Axis(labelAngle=-45), scale=alt.Scale(domain=[plot_df['ds'].min(), plot_df['ds'].max()]))
)

actual = base.transform_filter(
    alt.datum.type == 'historical'
).mark_circle(size=120, color='#1f77b4', opacity=0.8).encode(
    y=alt.Y('actual:Q', title='Actual Revenue', scale=alt.Scale(zero=False)),
    tooltip=[
        alt.Tooltip('ds:T', title='Date', format='%Y-%m-%d'),
        alt.Tooltip('actual:Q', title='Actual Revenue', format='$,.0f')
    ]
)

fitted = base.transform_filter(
    alt.datum.type == 'historical'
).mark_line(color='#1f77b4', strokeWidth=2, opacity=0.6).encode(
    y='fitted:Q',
    tooltip=[
        alt.Tooltip('ds:T', title='Date', format='%Y-%m-%d'),
        alt.Tooltip('fitted:Q', title='Fitted Revenue', format='$,.0f')
    ]
)

forecast_line = base.transform_filter(
    alt.datum.type == 'forecast'
).mark_line(color='#d62728', strokeDash=[8, 4], strokeWidth=3).encode(
    y='forecast:Q',
    tooltip=[
        alt.Tooltip('ds:T', title='Date', format='%Y-%m-%d'),
        alt.Tooltip('forecast:Q', title='Predicted Revenue', format='$,.0f'),
        alt.Tooltip('lower:Q', title='Lower Bound', format='$,.0f'),
        alt.Tooltip('upper:Q', title='Upper Bound', format='$,.0f')
    ]
)

forecast_points = base.transform_filter(
    alt.datum.type == 'forecast'
).mark_circle(size=100, color='#d62728', opacity=0.7).encode(
    y='forecast:Q',
    tooltip=[
        alt.Tooltip('ds:T', title='Date', format='%Y-%m-%d'),
        alt.Tooltip('forecast:Q', title='Predicted Revenue', format='$,.0f'),
        alt.Tooltip('lower:Q', title='Lower Bound', format='$,.0f'),
        alt.Tooltip('upper:Q', title='Upper Bound', format='$,.0f')
    ]
)

confidence_interval = base.transform_filter(
    alt.datum.type == 'forecast'
).mark_area(opacity=0.2, color='#d62728').encode(
    y='lower:Q',
    y2='upper:Q'
)

chart = alt.layer(
    confidence_interval,
    fitted,
    actual,
    forecast_line,
    forecast_points
).properties(
    height=500,
    width='container',
    title=alt.TitleParams(
        text=f'Revenue Forecast (Investment: ${investment:,}, Ad Spend: ${ad_spend:,}, Sales Reps: {sales_reps}, Campaigns: {marketing_campaigns})',
        anchor='start'
    )
).configure_axis(
    gridColor='#e0e0e0',
    gridOpacity=0.5
).configure_view(
    strokeWidth=0
)

st.altair_chart(chart, use_container_width=True)

st.dataframe(historical_df)

# Display forecast table
st.subheader(f'{forecast_months}-Month Forecast Details')

# Add actual regressor values used in forecast to table
forecast_table = future_df[['ds', 'investment', 'ad_spend', 'sales_reps', 'marketing_campaigns']].copy()
forecast_table['date'] = forecast_table['ds'].dt.strftime('%Y-%m-%d')
forecast_table['predicted_revenue'] = future_forecast['yhat'].round(2)
forecast_table['yhat_lower'] = future_forecast['yhat_lower'].round(2)
forecast_table['yhat_upper'] = future_forecast['yhat_upper'].round(2)

st.dataframe(
    forecast_table[['date', 'predicted_revenue', 'yhat_lower', 'yhat_upper', 
                    'investment', 'ad_spend', 'sales_reps', 'marketing_campaigns']],
    hide_index=True
)

st.altair_chart(chart, use_container_width=True)

st.dataframe(historical_df)

# Display forecast table
st.subheader(f'{forecast_months}-Month Forecast Details')

# Add actual regressor values used in forecast to table
forecast_table = future_df[['ds', 'investment', 'ad_spend', 'sales_reps', 'marketing_campaigns']].copy()
forecast_table['date'] = forecast_table['ds'].dt.strftime('%Y-%m-%d')
forecast_table['predicted_revenue'] = future_forecast['yhat'].round(2)
forecast_table['yhat_lower'] = future_forecast['yhat_lower'].round(2)
forecast_table['yhat_upper'] = future_forecast['yhat_upper'].round(2)

st.dataframe(
    forecast_table[['date', 'predicted_revenue', 'yhat_lower', 'yhat_upper', 
                    'investment', 'ad_spend', 'sales_reps', 'marketing_campaigns']],
    hide_index=True
)
