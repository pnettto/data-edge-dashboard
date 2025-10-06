# from components.bar import render_bar_chart
from components.markdown import render_markdown
from components.line import render_line_chart
from components.table import render_table

CHART_RENDERERS = {
    # 'bar': render_bar_chart,
    'bar': lambda config: None,
    'markdown': render_markdown,
    'line': render_line_chart,
    'table': render_table,
}


def render_chart(chart_config):
    return CHART_RENDERERS[chart_config['type']](config=chart_config)
