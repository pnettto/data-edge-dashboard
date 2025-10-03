"""
Entry point for the Data Edge Dashboard (Streamlit).
"""

import streamlit as st

from utils.chart_loader import render_chart
from exploratory_analysis.pedro.output.configs import configs as pedro_configs
# from exploratory_analysis.guillermo.output.configs import configs as guillermo_configs
# from exploratory_analysis.osei.output.configs import configs as osei_configs
# from exploratory_analysis.waldean.output.configs import configs as waldean_configs

# Use plain list concatenation instead of np.concatenate to avoid ValueError
chart_configs = pedro_configs

# Create a dictionary mapping tab names to lists of chart configs for that tab
tab_configs = {}
for item in chart_configs:
    if isinstance(item, list):
        for subitem in item:
            tab = subitem.get("tab", "Other")
            tab_configs.setdefault(tab, []).append(subitem)
    else:
        tab = item.get("tab", "Other")
        tab_configs.setdefault(tab, []).append(item)

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
    tab_titles = list(tab_configs.keys())
    tabs = st.tabs(tab_titles)

    for tab_index, tab in enumerate(tabs):
        with tab:
            st.header(tab_titles[tab_index])
            # Get configs for THIS tab only
            for chart_config in tab_configs[tab_titles[tab_index]]:
                # Handle multi column cases
                if 'columns' in chart_config:
                    cols = st.columns(len(chart_config['columns']))
                    for i, col in enumerate(cols):
                        with col:
                            render_chart(chart_config['columns'][i])
                # Single chart case
                else:
                    render_chart(chart_config)

def main() -> None:
    configure_page()
    render_header()
    render_nav_and_content()


if __name__ == "__main__":
    main()
