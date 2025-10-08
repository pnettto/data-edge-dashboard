"""
Entry point for the Data Edge Dashboard (Streamlit).
"""

import streamlit as st
from collections import defaultdict

from utils.chart_loader import render_chart

from utils.overview import config as overview_config
from exploratory_analysis.pedro.output.config import config as pedro_config
from exploratory_analysis.guillermo.output.config import config as guillermo_config
from exploratory_analysis.osei.output.config import config as osei_config
# from exploratory_analysis.waldean.output.config import config as waldean_config

all_configs = overview_config + pedro_config + guillermo_config + osei_config # + waldean_config

# Merge tabs with same name
merged = defaultdict(list)
for config in all_configs:
    merged[config['tab']].extend(config['items'])

chart_configs = [{'tab': tab, 'items': items} for tab, items in merged.items()]

APP_TITLE = ":material/query_stats: Data Edge Dashboard"

def configure_page() -> None:
    """Set Streamlit page-wide configuration and base styles."""
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="📊",
        layout="wide"
    )

    st.markdown("""
    <style>
    /* Gap between columns */
    [data-testid="stHorizontalBlock"] {
        gap: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

def render_header() -> None:
    """Render the main page header."""
    st.title(APP_TITLE)
    st.markdown("""
    Group 6: Guillermo Contreras, Osei Caesar, Pedro Netto and Waldean Nelson
    """)

def render_nav_and_content() -> None:
    """Render navigation tabs and chart content, with a standalone summary/intro tab."""
    # Create a summary/intro tab as the first tab
    tab_titles = [config['tab'] for config in chart_configs]
    tabs = st.tabs(tab_titles)

    # Render the intro/summary tab
    for tab_index, tab in enumerate(tabs):
        with tab:
            st.header(tab_titles[tab_index])
            items = chart_configs[tab_index]['items']
            
            for item in items:
                if 'columns' in item:
                    # Handle multi-column layout
                    column_items = item['columns']
                    cols = st.columns(len(column_items))
                    for i, col in enumerate(cols):
                        with col:
                            render_chart(column_items[i])
                else:
                    # Single chart
                    render_chart(item)
            
                # Add a spacer between charts/sections
                st.markdown('<div style="height:5rem;"></div>', unsafe_allow_html=True)

def main() -> None:
    configure_page()
    render_header()
    render_nav_and_content()


if __name__ == "__main__":
    main()