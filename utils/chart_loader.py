from typing import Literal, Callable
from ui.components.components.single_line import render_single_line_chart
from ui.components.components.multi_line import render_multi_line_chart
from ui.components.components.bar import render_bar_chart

ChartType = Literal['single_line', 'multi_line', 'bar']

CHART_RENDERERS: dict[ChartType, Callable] = {
    'single_line': render_single_line_chart,
    'multi_line': render_multi_line_chart,
    'bar': render_bar_chart,
}

def render_chart(chart_type: ChartType, chart_config):
    return CHART_RENDERERS[chart_type](config=chart_config)