from charts.single_line import render_single_line_chart
from charts.multi_line import render_multi_line_chart
from charts.bar import render_bar_chart

CHART_RENDERERS = {
    'single_line': render_single_line_chart,
    'multi_line': render_multi_line_chart,
    'bar': render_bar_chart,
}

def render_chart(chart_config):
    return CHART_RENDERERS[chart_config['type']](config=chart_config)