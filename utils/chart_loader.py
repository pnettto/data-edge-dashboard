from components.bar import render_bar_chart
from components.markdown import render_markdown
from components.multi_line import render_multi_line_chart
from components.single_line import render_single_line_chart
from components.table import render_table

CHART_RENDERERS = {
    'bar': render_bar_chart,
    'markdown': render_markdown,
    'multi_line': render_multi_line_chart,
    'single_line': render_single_line_chart,
    'table': render_table,
}


def render_chart(chart_config):
    return CHART_RENDERERS[chart_config['type']](config=chart_config)
