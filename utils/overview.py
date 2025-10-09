import os
import base64
import mimetypes

def _data_uri_for_image(rel_path: str) -> str:
    # Build absolute path from repo root (utils/.. -> project root)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    abs_path = os.path.join(base_dir, rel_path)
    mime, _ = mimetypes.guess_type(abs_path)
    mime = mime or "image/png"
    with open(abs_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime};base64,{b64}"

config = [
    {
        'tab': 'Overview',
        'items': [
            
            # The process
            {
                'columns': [
                    {
                        'type': 'markdown',
                        'title': 'The process',
                        'content': """
                        - Frequent group discussions and check-ins to define directions and align on goals (divergence/convergence)
                        - Mix of online and in-person work sessions
                        - Focus on modern technologies and trending tools
                        - Goal: create a production-ready, professional dashboard
                        """
                    },
                    {
                        'type': 'image',
                        'src': _data_uri_for_image('resources/screenshots/process.jpg'),
                    }
                ]
            },

            # The reseach
            {
                'columns': [
                    {
                        'type': 'image',
                        'src': _data_uri_for_image('resources/screenshots/research.png'),
                    },
                    {
                        'type': 'markdown',
                        'title': 'The Research',
                        'content': """
                        **How can data inform Data Edge's strategy and performance?**                        
                        - Challenges: 
                            - Anonymized, incomplete, and multi-source data
                            - Defining research line
                        - Main investigation topics: 
                            - Employee utilization across roles and seniority
                            - Resource planning and growth
                            - Operational and strategic decision-making
                        """
                    }
                ]
            },

            # The Dashboard
            {
                'columns': [
                    {
                        'type': 'markdown',
                        'title': 'The Dashboard',
                        'content': """
                        We created a modern dashboard that combines standard business indicators with innovative forecasting features.

                        **Features:**
                        - Built with Streamlit and Prophet forecasting—Prophet makes it easy to generate accurate forecasts, even with complex seasonal trends
                        - Interactive charts with up to 24-month forecast periods
                        - Separates analysis from development via config-file architecture (rapid iteration without coding)
                        - Collaboration via Github
                        """
                    },
                    {
                        'type': 'image',
                        'src': _data_uri_for_image('resources/screenshots/dashboard.png'),
                    },
                ]
            },

        ]
    },
]
