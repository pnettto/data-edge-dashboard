"""
Entry point for the Data Edge Dashboard (Streamlit).
"""

import streamlit as st
import numpy as np

from utils.chart_loader import render_chart
from exploratory_analysis.pedro.output.configs import configs as pedro_configs
# from exploratory_analysis.guillermo.output.configs import configs as guillermo_configs
# from exploratory_analysis.osei.output.configs import configs as osei_configs
# from exploratory_analysis.waldean.output.configs import configs as waldean_configs

chart_configs = np.concatenate([pedro_configs])

APP_TITLE = "Data Edge Dashboard"

def configure_page() -> None:
    """Set Streamlit page-wide configuration and base styles."""
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="📊",
        layout="wide"
    )

def render_header() -> None:
    """Render the main page header."""
    st.title(APP_TITLE)

def render_nav_and_content() -> None:
    """Render navigation tabs and chart content."""
    tab_titles = ["Sample charts"]
    tabs = st.tabs(tab_titles)

    with tabs[0]:
        st.header(tab_titles[0])
        for chart_config in chart_configs:
            # Handle multi column cases
            if isinstance(chart_config, list):
                cols = st.columns(len(chart_config))
                for i, col in enumerate(cols):
                    with col:
                        render_chart(chart_config[i])
            # Single column case
            else:
                render_chart(chart_config)

def main() -> None:
    configure_page()
    render_header()
    render_nav_and_content()


if __name__ == "__main__":
    main()
