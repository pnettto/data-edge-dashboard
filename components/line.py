"""Line chart component with Prophet-based forecasting capability"""

import streamlit as st
import altair as alt
import pandas as pd
from prophet import Prophet


#######################
# Forecasting Engine
#######################

@st.cache_data(show_spinner=False)
def _compute_forecast(df: pd.DataFrame, x_field: str, y_field: str, periods: int, freq: str, category: str = None) -> pd.DataFrame:
    """Core forecasting function using Prophet model."""
    model_params = dict(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False,
        n_changepoints=10,
        seasonality_mode="additive",
        interval_width=0.0,
    )
    # Prepare dataframe for Prophet: rename columns to 'ds' (date) and 'y' (value)
    prophet_df = df[[x_field, y_field]].rename(columns={x_field: "ds", y_field: "y"})
    # Instantiate Prophet model with provided parameters
    model = Prophet(**model_params)
    model.fit(prophet_df)
    # Create future dates for forecasting (no history included)
    future = model.make_future_dataframe(periods=periods, freq=freq, include_history=False)
    # Predict future values using the trained model
    forecast = model.predict(future)
    result = forecast[["ds", "yhat"]].copy()
    if category is not None:
        result["category"] = category
    return result


#######################
# Data Preparation Functions
#######################

def prepare_actual_data(df: pd.DataFrame, x_field: str, y_field: str, category_field: str = None, with_type: bool = True) -> pd.DataFrame:
    """Prepare historical data by adding type column for visualization."""
    df = df.copy()
    if with_type:
        df["type"] = "Actual"
    return df


def create_forecast_data(df: pd.DataFrame, x_field: str, y_field: str, forecast_periods: int, freq: str, category_field: str = None, max_periods: int = 12) -> pd.DataFrame:
    """Generate forecasted data points using Prophet model with specified parameters."""
    if category_field is None:
        # Generate max forecast and slice to requested periods
        forecast = _compute_forecast(df, x_field, y_field, max_periods, freq)
        forecast = forecast.iloc[:forecast_periods]
        return pd.DataFrame({
            x_field: forecast['ds'],
            y_field: forecast['yhat'],
            "type": ["Forecast"] * len(forecast)
        })
    else:
        # Multi-line forecast: generate forecast per category
        all_forecasts = []
        categories = sorted(df[category_field].unique())
        for category in categories:
            category_df = df[df[category_field] == category].copy()
            if len(category_df) >= 2:
                # Infer frequency for this specific category
                category_freq = infer_frequency(category_df, x_field)
                # Generate max forecast and slice to requested periods
                forecast = _compute_forecast(category_df, x_field, y_field, max_periods, category_freq, str(category))
                forecast = forecast.iloc[:forecast_periods]
                forecast_data = pd.DataFrame({
                    x_field: forecast['ds'],
                    y_field: forecast['yhat'],
                    category_field: str(category),
                    "type": ["Forecast"] * len(forecast)
                })
                all_forecasts.append(forecast_data)
        
        if all_forecasts:
            return pd.concat(all_forecasts, ignore_index=True)
        return pd.DataFrame()


def create_connector_data(actual_df: pd.DataFrame, forecast_df: pd.DataFrame, x_field: str, y_field: str, category_field: str = None) -> pd.DataFrame:
    """Create connecting points between actual and forecasted data for smooth visualization."""
    if forecast_df.empty:
        return pd.DataFrame()

    if category_field is None:
        last_actual = actual_df.sort_values(by=x_field).iloc[-1]
        first_forecast = forecast_df.sort_values(by=x_field).iloc[0]

        return pd.DataFrame([
            {
                x_field: last_actual[x_field],
                y_field: last_actual[y_field],
                "type": "Connector"
            },
            {
                x_field: first_forecast[x_field],
                y_field: first_forecast[y_field],
                "type": "Connector"
            }
        ])
    else:
        # Multi-line connector: create connectors per category
        all_connectors = []
        categories = sorted(actual_df[category_field].unique())
        for category in categories:
            category = str(category)
            category_actual = actual_df[actual_df[category_field] == category].sort_values(by=x_field)
            category_forecast = forecast_df[forecast_df[category_field] == category].sort_values(by=x_field)
            
            if not category_actual.empty and not category_forecast.empty:
                last_actual = category_actual.iloc[-1]
                first_forecast = category_forecast.iloc[0]
                
                connectors = pd.DataFrame([
                    {
                        x_field: last_actual[x_field],
                        y_field: last_actual[y_field],
                        category_field: category,
                        "type": "Connector"
                    },
                    {
                        x_field: first_forecast[x_field],
                        y_field: first_forecast[y_field],
                        category_field: category,
                        "type": "Connector"
                    }
                ])
                all_connectors.append(connectors)
        
        if all_connectors:
            return pd.concat(all_connectors, ignore_index=True)
        return pd.DataFrame()


def infer_frequency(df: pd.DataFrame, x_field: str) -> str:
    """Determine the time frequency of the data series for forecasting."""
    freq = pd.infer_freq(df[x_field].sort_values())
    if freq is not None:
        return freq

    if len(df) > 1:
        delta = (df[x_field].sort_values().iloc[1] - df[x_field].sort_values().iloc[0])
        if hasattr(delta, 'days') and delta.days >= 1:
            return f"{delta.days}D"

    return "D"


#######################
# Main Chart Rendering
#######################

def render_line_chart(config):
    """Render the forecast chart with actual and predicted values."""
    
    # Setup and configuration
    st.subheader(config['title'])
    st.caption(config['description'])
    
    # Data preparation
    df = config['df'].copy()
    x_field = config['x_field']
    y_field = config['y_field']
    category_field = config.get('category_field', None)
    enable_forecast = config.get('forecast', False)

    # User controls - only show slider if forecast is enabled
    if enable_forecast:
        base_key = id(config)
        forecast_periods = st.slider("Forecast periods", 1, 12, 6, key=f"slider_{base_key}")

    # Ensure datetime format
    if not pd.api.types.is_datetime64_any_dtype(df[x_field]):
        df[x_field] = pd.to_datetime(df[x_field])

    # Generate all required dataframes
    if enable_forecast:
        actual_df = prepare_actual_data(df, x_field, y_field, category_field, with_type=True)
        forecast_df = pd.DataFrame()
        connector_df = pd.DataFrame()

        if len(df) >= 2:
            with st.spinner("Generating forecast..."):
                if category_field is None:
                    freq = infer_frequency(df, x_field)
                    forecast_df = create_forecast_data(df, x_field, y_field, forecast_periods, freq, category_field)
                else:
                    forecast_df = create_forecast_data(df, x_field, y_field, forecast_periods, None, category_field)
                
                connector_df = create_connector_data(actual_df, forecast_df, x_field, y_field, category_field)
            
            if not forecast_df.empty:
                plot_df = pd.concat([actual_df, forecast_df], ignore_index=True)
            else:
                plot_df = actual_df.copy()
        else:
            plot_df = actual_df.copy()
    else:
        plot_df = prepare_actual_data(df, x_field, y_field, category_field, with_type=False)

    #######################
    # Chart Construction
    #######################

    # Base chart settings
    base_color = "#0b7dcfff"
    base = alt.Chart(plot_df)
    
    if enable_forecast:
        actual_data = plot_df[plot_df["type"] == "Actual"]
        if category_field is not None:
            # For multi-line, check points per category
            show_points = all(actual_data[actual_data[category_field] == cat].shape[0] < 200 
                            for cat in actual_data[category_field].unique())
        else:
            show_points = actual_data.shape[0] < 200
    else:
        if category_field is not None:
            show_points = all(plot_df[plot_df[category_field] == cat].shape[0] < 200 
                            for cat in plot_df[category_field].unique())
        else:
            show_points = plot_df.shape[0] < 200

    # Determine if multi-line chart
    is_multi_line = category_field is not None

    # Create actual data line
    if enable_forecast:
        if is_multi_line:
            actual_line = base.transform_filter(
                alt.datum.type == "Actual"
            ).mark_line(point=show_points).encode(
                x=alt.X(f"{x_field}:T", title=config['x_label']),
                y=alt.Y(f"{y_field}:Q", title=config['y_label'], axis=alt.Axis(format=",.0f")),
                color=alt.Color(f"{category_field}:N", title=config.get('category_label', category_field)),
                tooltip=[
                    alt.Tooltip(f"{x_field}:T", title=config['x_label']),
                    alt.Tooltip(f"{y_field}:Q", title=config['y_label'], format=","),
                    alt.Tooltip(f"{category_field}:N", title=config.get('category_label', category_field)),
                    alt.Tooltip("type:N", title="Type"),
                ],
            )
            
            forecast_line = base.transform_filter(
                alt.datum.type == "Forecast"
            ).mark_line(point=show_points, strokeDash=[5, 5]).encode(
                x=alt.X(f"{x_field}:T", title=config['x_label']),
                y=alt.Y(f"{y_field}:Q", title=config['y_label'], axis=alt.Axis(format=",.0f")),
                color=alt.Color(f"{category_field}:N", title=config.get('category_label', category_field)),
                tooltip=[
                    alt.Tooltip(f"{x_field}:T", title=config['x_label']),
                    alt.Tooltip(f"{y_field}:Q", title=config['y_label'], format=","),
                    alt.Tooltip(f"{category_field}:N", title=config.get('category_label', category_field)),
                    alt.Tooltip("type:N", title="Type"),
                ],
            )
            
            if not connector_df.empty:
                connector_chart = alt.Chart(connector_df).mark_line(point=False, strokeDash=[5, 5]).encode(
                    x=alt.X(f"{x_field}:T"),
                    y=alt.Y(f"{y_field}:Q"),
                    color=alt.Color(f"{category_field}:N", title=config.get('category_label', category_field)),
                )
                chart = (actual_line + forecast_line + connector_chart).properties(height=340)
            else:
                chart = (actual_line + forecast_line).properties(height=340)
        else:
            actual_line = base.transform_filter(
                alt.datum.type == "Actual"
            ).mark_line(point=show_points, color=base_color).encode(
                x=alt.X(f"{x_field}:T", title=config['x_label']),
                y=alt.Y(f"{y_field}:Q", title=config['y_label'], axis=alt.Axis(format=",.0f")),
                tooltip=[
                    alt.Tooltip(f"{x_field}:T", title=config['x_label']),
                    alt.Tooltip(f"{y_field}:Q", title=config['y_label'], format=","),
                    alt.Tooltip("type:N", title="Type"),
                ],
            )

            forecast_line = base.transform_filter(
                alt.datum.type == "Forecast"
            ).mark_line(point=show_points, color=base_color, strokeDash=[5, 5]).encode(
                x=alt.X(f"{x_field}:T", title=config['x_label']),
                y=alt.Y(f"{y_field}:Q", title=config['y_label'], axis=alt.Axis(format=",.0f")),
                tooltip=[
                    alt.Tooltip(f"{x_field}:T", title=config['x_label']),
                    alt.Tooltip(f"{y_field}:Q", title=config['y_label'], format=","),
                    alt.Tooltip("type:N", title="Type"),
                ],
            )

            if not connector_df.empty:
                connector_chart = alt.Chart(connector_df).mark_line(point=False, color=base_color, strokeDash=[5, 5]).encode(
                    x=alt.X(f"{x_field}:T"),
                    y=alt.Y(f"{y_field}:Q"),
                )
                chart = (actual_line + forecast_line + connector_chart).properties(height=340)
            else:
                chart = (actual_line + forecast_line).properties(height=340)
    else:
        # Simple line chart without forecast
        if is_multi_line:
            chart = base.mark_line(point=show_points).encode(
                x=alt.X(f"{x_field}:T", title=config['x_label']),
                y=alt.Y(f"{y_field}:Q", title=config['y_label'], axis=alt.Axis(format=",.0f")),
                color=alt.Color(f"{category_field}:N", title=config.get('category_label', category_field)),
                tooltip=[
                    alt.Tooltip(f"{x_field}:T", title=config['x_label']),
                    alt.Tooltip(f"{y_field}:Q", title=config['y_label'], format=","),
                    alt.Tooltip(f"{category_field}:N", title=config.get('category_label', category_field)),
                ],
            ).properties(height=340)
        else:
            chart = base.mark_line(point=show_points, color=base_color).encode(
                x=alt.X(f"{x_field}:T", title=config['x_label']),
                y=alt.Y(f"{y_field}:Q", title=config['y_label'], axis=alt.Axis(format=",.0f")),
                tooltip=[
                    alt.Tooltip(f"{x_field}:T", title=config['x_label']),
                    alt.Tooltip(f"{y_field}:Q", title=config['y_label'], format=","),
                ],
            ).properties(height=340)

    # Render the final chart
    st.altair_chart(chart, use_container_width=True)
