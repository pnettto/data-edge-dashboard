"""
Entry point for the Data Edge Dashboard (Streamlit).
"""

import streamlit as st

from ui.components import sample_charts

from utils.chart_loader import render_chart

from exploratory_analysis.pedro.output.chart_configs import chart_configs as pedro_chart_configs

APP_TITLE = "Data Edge Dashboard"


def configure_page() -> None:
    """Set Streamlit page-wide configuration and base styles."""
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="📊",
        layout="wide"
    )

def render_header() -> None:
    st.title(APP_TITLE)


def render_nav_and_content() -> None:
    tabs = st.tabs([
        "Revenue & Cashflow"
    ])

    with tabs[0]:
        st.header('Revenue & Cashflow')

        st.header('Charts using analysis data')
        for chart_config in pedro_chart_configs:
            print(chart_config)
            render_chart(chart_config['type'], chart_config)
        

        st.header('Sample charts (development purpose)')
        lcol, rcol = st.columns(2)
        with lcol:
            sample_charts.sample_revenue_timeseries()
        with rcol:
            sample_charts.sample_cashflow_timeseries()

        sample_charts.sample_revenue_bar()
        sample_charts.sample_multi_line()



def main() -> None:
    configure_page()
    render_header()
    render_nav_and_content()


if __name__ == "__main__":
    main()
