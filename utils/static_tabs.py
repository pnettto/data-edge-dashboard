import streamlit as st 

def render_overview_tab(intro_tab_title):
    left_col, right_col = st.columns(2)
    with left_col:
        st.header(intro_tab_title)
        st.markdown(
            """
            This dashboard presents a collection of exploratory analyses and visualizations from Group 6:
            **Guillermo Contreras, Osei Caesar, Pedro Netto, and Waldean Nelson**.

            **Project Overview:**
            - Explore revenue forecasting, trends, and data-driven insights.
            - Interactive charts and tables for in-depth analysis.
            - Modular design: each tab showcases different contributors' work.
            """
        )
    with right_col:
        st.image(
            "https://plus.unsplash.com/premium_photo-1681487769650-a0c3fbaed85a?q=80&w=2455&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
            use_column_width=True,
        )