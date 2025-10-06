"""Chart building logic for line charts"""

from typing import Optional
import pandas as pd
import altair as alt

from .config import LineChartConfig
from .data import should_show_points


# Constants
BASE_COLOR = "#0b7dcfff"
CHART_HEIGHT = 340


class ChartBuilder:
    """Builds Altair charts based on configuration."""
    
    def __init__(self, config: LineChartConfig):
        self.config = config
    
    def build(
        self, 
        plot_df: pd.DataFrame, 
        connector_df: pd.DataFrame, 
        enable_forecast: bool
    ) -> alt.Chart:
        """
        Build the appropriate Altair chart based on configuration.
        
        Chooses between 4 chart types:
        1. Single line without forecast
        2. Multi-line without forecast
        3. Single line with forecast
        4. Multi-line with forecast
        """
        # Determine whether to show individual points on lines
        if enable_forecast:
            actual_data = plot_df[plot_df["type"] == "Actual"]
            show_points = should_show_points(actual_data, self.config.category_field)
        else:
            show_points = should_show_points(plot_df, self.config.category_field)

        # Check if this is a multi-line chart
        is_multi_line = self.config.category_field is not None
        
        # Build the appropriate chart type
        if enable_forecast:
            if is_multi_line:
                return self._build_multi_line_forecast(plot_df, connector_df, show_points)
            else:
                return self._build_single_line_forecast(plot_df, connector_df, show_points)
        else:
            if is_multi_line:
                return self._build_multi_line(plot_df, show_points)
            else:
                return self._build_single_line(plot_df, show_points)
    
    def _build_single_line(self, plot_df: pd.DataFrame, show_points: bool) -> alt.Chart:
        """Build a simple single-line chart without forecasting."""
        return alt.Chart(plot_df).mark_line(point=show_points, color=BASE_COLOR).encode(
            x=alt.X(f"{self.config.x_field}:T", title=self.config.x_label),
            y=alt.Y(f"{self.config.y_field}:Q", title=self.config.y_label, axis=alt.Axis(format=",.0f")),
            tooltip=[
                alt.Tooltip(f"{self.config.x_field}:T", title=self.config.x_label),
                alt.Tooltip(f"{self.config.y_field}:Q", title=self.config.y_label, format=","),
            ],
        ).properties(height=CHART_HEIGHT)
    
    def _build_multi_line(self, plot_df: pd.DataFrame, show_points: bool) -> alt.Chart:
        """Build a multi-line chart (one line per category) without forecasting."""
        category_label = get_category_label(self.config)
        
        return alt.Chart(plot_df).mark_line(point=show_points).encode(
            x=alt.X(f"{self.config.x_field}:T", title=self.config.x_label),
            y=alt.Y(f"{self.config.y_field}:Q", title=self.config.y_label, axis=alt.Axis(format=",.0f")),
            color=alt.Color(f"{self.config.category_field}:N", legend=alt.Legend(title=category_label)),
            tooltip=[
                alt.Tooltip(f"{self.config.x_field}:T", title=self.config.x_label),
                alt.Tooltip(f"{self.config.y_field}:Q", title=self.config.y_label, format=","),
                alt.Tooltip(f"{self.config.category_field}:N", title=category_label),
            ],
        ).properties(height=CHART_HEIGHT)
    
    def _build_single_line_forecast(
        self, 
        plot_df: pd.DataFrame, 
        connector_df: pd.DataFrame, 
        show_points: bool
    ) -> alt.Chart:
        """Build a single-line chart with forecasting."""
        base = alt.Chart(plot_df)
        
        # Create the actual data line (solid)
        actual_line = base.transform_filter(
            alt.datum.type == "Actual"
        ).mark_line(point=show_points, color=BASE_COLOR).encode(
            **get_base_encoding(self.config),
            tooltip=get_tooltip_with_type(self.config)
        )

        # Create the forecast line (dashed)
        forecast_line = base.transform_filter(
            alt.datum.type == "Forecast"
        ).mark_line(point=show_points, color=BASE_COLOR, strokeDash=[5, 5]).encode(
            **get_base_encoding(self.config),
            tooltip=get_tooltip_with_type(self.config)
        )

        # Combine layers
        chart = actual_line + forecast_line
        
        # Add connector line if available
        if not connector_df.empty:
            connector_chart = alt.Chart(connector_df).mark_line(
                point=False, color=BASE_COLOR, strokeDash=[5, 5]
            ).encode(
                x=alt.X(f"{self.config.x_field}:T"),
                y=alt.Y(f"{self.config.y_field}:Q"),
            )
            chart = chart + connector_chart
        
        return chart.properties(height=CHART_HEIGHT)
    
    def _build_multi_line_forecast(
        self, 
        plot_df: pd.DataFrame, 
        connector_df: pd.DataFrame, 
        show_points: bool
    ) -> alt.Chart:
        """Build a multi-line chart with forecasting."""
        category_label = get_category_label(self.config)
        base = alt.Chart(plot_df)
        
        # Create the actual data lines (solid, color-coded by category)
        actual_line = base.transform_filter(
            alt.datum.type == "Actual"
        ).mark_line(point=show_points).encode(
            **get_base_encoding(self.config),
            color=alt.Color(f"{self.config.category_field}:N", legend=alt.Legend(title=category_label)),
            tooltip=get_tooltip_with_type_and_category(self.config, category_label)
        )
        
        # Create the forecast lines (dashed, color-coded by category)
        forecast_line = base.transform_filter(
            alt.datum.type == "Forecast"
        ).mark_line(point=show_points, strokeDash=[5, 5]).encode(
            **get_base_encoding(self.config),
            color=alt.Color(f"{self.config.category_field}:N", legend=alt.Legend(title=category_label)),
            tooltip=get_tooltip_with_type_and_category(self.config, category_label)
        )
        
        # Combine layers
        chart = actual_line + forecast_line
        
        # Add connector lines if available
        if not connector_df.empty:
            connector_chart = alt.Chart(connector_df).mark_line(
                point=False, strokeDash=[5, 5]
            ).encode(
                x=alt.X(f"{self.config.x_field}:T"),
                y=alt.Y(f"{self.config.y_field}:Q"),
                color=alt.Color(f"{self.config.category_field}:N", legend=alt.Legend(title=category_label)),
            )
            chart = chart + connector_chart
        
        return chart.properties(height=CHART_HEIGHT)


def get_category_label(config: LineChartConfig) -> Optional[str]:
    """Get the display label for category field."""
    return config.category_label if config.category_field else None


def get_base_encoding(config: LineChartConfig) -> dict:
    """Get the basic x and y axis encodings used across chart types."""
    return {
        'x': alt.X(f"{config.x_field}:T", title=config.x_label),
        'y': alt.Y(f"{config.y_field}:Q", title=config.y_label, axis=alt.Axis(format=",.0f"))
    }


def get_tooltip_with_type(config: LineChartConfig) -> list:
    """Get tooltip configuration for forecast charts (single-line)."""
    return [
        alt.Tooltip(f"{config.x_field}:T", title=config.x_label),
        alt.Tooltip(f"{config.y_field}:Q", title=config.y_label, format=","),
        alt.Tooltip("type:N", title="Type"),
    ]


def get_tooltip_with_type_and_category(config: LineChartConfig, category_label: str) -> list:
    """Get tooltip configuration for forecast charts (multi-line)."""
    return [
        alt.Tooltip(f"{config.x_field}:T", title=config.x_label),
        alt.Tooltip(f"{config.y_field}:Q", title=config.y_label, format=","),
        alt.Tooltip(f"{config.category_field}:N", title=category_label),
        alt.Tooltip("type:N", title="Type"),
    ]
