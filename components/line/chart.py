"""Chart building for line charts"""

import pandas as pd
import altair as alt


def build_chart(plot_df: pd.DataFrame, config: dict) -> alt.Chart:
    """Build Altair chart based on configuration."""
    has_forecast = config.get('forecast', False) and "type" in plot_df.columns
    has_categories = config.get('category_field') is not None
    
    if has_forecast and has_categories:
        return _build_multi_forecast(plot_df, config)
    elif has_forecast:
        return _build_single_forecast(plot_df, config)
    elif has_categories:
        return _build_multi_line(plot_df, config)
    else:
        return _build_single_line(plot_df, config)


def _get_base_encoding(config: dict, include_type: bool = False, include_category: bool = False) -> dict:
    """Get common encoding configuration."""
    category_label = config.get('category_label') or config.get('category_field', '')
    
    tooltip = [
        alt.Tooltip(f"{config['x_field']}:T", title=config['x_label']),
        alt.Tooltip(f"{config['y_field']}:Q", title=config['y_label'], format=","),
    ]
    
    if include_category and config.get('category_field'):
        tooltip.append(alt.Tooltip(f"{config['category_field']}:N", title=category_label))
    
    if include_type:
        tooltip.append(alt.Tooltip("type:N", title="Type"))
    
    encoding = {
        'x': alt.X(f"{config['x_field']}:T", title=config['x_label']),
        'y': alt.Y(f"{config['y_field']}:Q", title=config['y_label'], axis=alt.Axis(format=",.0f")),
        'tooltip': tooltip,
    }
    
    if include_category and config.get('category_field'):
        encoding['color'] = alt.Color(
            f"{config['category_field']}:N", 
            legend=alt.Legend(title=category_label)
        )
    
    return encoding


def _build_single_line(df: pd.DataFrame, config: dict) -> alt.Chart:
    """Single line chart without forecast."""
    encoding = _get_base_encoding(config)
    
    return alt.Chart(df).mark_line(
        point=True, 
        color="#0b7dcfff"
    ).encode(**encoding).properties(height=340)


def _build_multi_line(df: pd.DataFrame, config: dict) -> alt.Chart:
    """Multi-line chart without forecast + interactive toggling."""
    category_field = config['category_field']
    highlight_cats = config.get('category_area_highlight', [])
    all_categories = sorted(df[category_field].unique())
    has_highlight_pair = len(highlight_cats) == 2

    # Selection (legend) applies only to non-highlight categories (or all if no highlight pair)
    selectable_categories = [c for c in all_categories if (not has_highlight_pair or c not in highlight_cats)]
    selection = None
    if selectable_categories:
        selection = alt.selection_point(
            fields=[category_field],
            bind='legend',
            toggle='true',
            empty='all'
        )

    # Area (if highlight pair)
    area_chart = None
    if has_highlight_pair:
        area_chart = _build_diff_area(df, config, highlight_cats, forecast=False)

    # Highlight lines (always visible, no legend entries)
    highlight_layer = None
    if has_highlight_pair:
        highlight_df = df[df[category_field].isin(highlight_cats)]
        highlight_layer = alt.Chart(highlight_df).mark_line(point=True).encode(
            x=alt.X(f"{config['x_field']}:T", title=config['x_label']),
            y=alt.Y(f"{config['y_field']}:Q", title=config['y_label'], axis=alt.Axis(format=",.0f")),
            color=alt.Color(
                f"{category_field}:N",
                scale=alt.Scale(domain=all_categories),
                legend=None  # keep legend clean for toggle categories
            ),
            tooltip=[
                alt.Tooltip(f"{config['x_field']}:T", title=config['x_label']),
                alt.Tooltip(f"{config['y_field']}:Q", title=config['y_label'], format=","),
                alt.Tooltip(f"{category_field}:N", title=config.get('category_label') or category_field),
            ]
        )

    # Other (toggle) lines
    other_df = df if not has_highlight_pair else df[~df[category_field].isin(highlight_cats)]
    other_layer = alt.Chart(other_df).mark_line(point=True)
    other_encoding = {
        'x': alt.X(f"{config['x_field']}:T", title=config['x_label']),
        'y': alt.Y(f"{config['y_field']}:Q", title=config['y_label'], axis=alt.Axis(format=",.0f")),
        'color': alt.Color(
            f"{category_field}:N",
            scale=alt.Scale(domain=all_categories),
            legend=alt.Legend(title=config.get('category_label') or category_field)
        ),
        'tooltip': [
            alt.Tooltip(f"{config['x_field']}:T", title=config['x_label']),
            alt.Tooltip(f"{config['y_field']}:Q", title=config['y_label'], format=","),
            alt.Tooltip(f"{category_field}:N", title=config.get('category_label') or category_field),
        ]
    }
    if selection:
        other_encoding['opacity'] = alt.condition(
            selection,
            alt.value(1),
            alt.value(0) if selectable_categories else alt.value(1)  # was 0.15
        )
        other_layer = other_layer.add_params(selection)

    other_layer = other_layer.encode(**other_encoding)

    layers = []
    if area_chart is not None:
        layers.append(area_chart)
    if highlight_layer is not None:
        layers.append(highlight_layer)
    layers.append(other_layer)

    chart = alt.layer(*layers)
    if area_chart is not None:
        chart = chart.resolve_scale(color='independent')  # diff area vs line colors

    return chart.properties(height=340)


def _build_single_forecast(df: pd.DataFrame, config: dict) -> alt.Chart:
    """Single line chart with forecast."""
    base = alt.Chart(df)
    encoding = _get_base_encoding(config, include_type=True)
    
    # Actual line (solid)
    actual = base.transform_filter(
        alt.datum.type == "Actual"
    ).mark_line(point=True, color="#0b7dcfff").encode(**encoding)
    
    # Forecast line (dashed)
    forecast = base.transform_filter(
        alt.datum.type == "Forecast"
    ).mark_line(point=True, color="#0b7dcfff", strokeDash=[5, 5]).encode(**encoding)
    
    # Connector line (dashed, no points, minimal encoding)
    connector = base.transform_filter(
        alt.datum.type == "Connector"
    ).mark_line(point=False, color="#0b7dcfff", strokeDash=[5, 5]).encode(
        x=alt.X(f"{config['x_field']}:T"),
        y=alt.Y(f"{config['y_field']}:Q"),
    )
    
    return (actual + forecast + connector).properties(height=340)


def _build_multi_forecast(df: pd.DataFrame, config: dict) -> alt.Chart:
    """Multi-line forecast chart + interactive toggling for non-highlight categories."""
    category_field = config['category_field']
    highlight_cats = config.get('category_area_highlight', [])
    has_highlight_pair = len(highlight_cats) == 2
    all_categories = sorted(df[category_field].unique())
    selectable_categories = [c for c in all_categories if (not has_highlight_pair or c not in highlight_cats)]

    selection = None
    if selectable_categories:
        selection = alt.selection_point(
            fields=[category_field],
            bind='legend',
            toggle='true',
            empty='all'
        )

    # Area only for Actual data
    area_chart = None
    if has_highlight_pair:
        area_chart = _build_diff_area(df, config, highlight_cats, forecast=True)

    def _line_layer(sub_df, type_value, dash=None, legend=True):
        mark = alt.Chart(sub_df[sub_df['type'] == type_value]).mark_line(
            point=True,
            strokeDash=dash
        )
        enc = {
            'x': alt.X(f"{config['x_field']}:T", title=config['x_label']),
            'y': alt.Y(f"{config['y_field']}:Q", title=config['y_label'], axis=alt.Axis(format=",.0f")),
            'color': alt.Color(
                f"{category_field}:N",
                scale=alt.Scale(domain=all_categories),
                legend=alt.Legend(title=config.get('category_label') or category_field) if legend else None
            ),
            'tooltip': [
                alt.Tooltip(f"{config['x_field']}:T", title=config['x_label']),
                alt.Tooltip(f"{config['y_field']}:Q", title=config['y_label'], format=","),
                alt.Tooltip(f"{category_field}:N", title=config.get('category_label') or category_field),
                alt.Tooltip("type:N", title="Type")
            ]
        }
        if selection and legend:
            enc['opacity'] = alt.condition(selection, alt.value(1), alt.value(0))  # was 0.15
            mark = mark.add_params(selection)
        return mark.encode(**enc)

    # Split highlight vs others
    highlight_df = df[df[category_field].isin(highlight_cats)] if has_highlight_pair else pd.DataFrame(columns=df.columns)
    other_df = df if not has_highlight_pair else df[~df[category_field].isin(highlight_cats)]

    layers = []

    if area_chart is not None:
        layers.append(area_chart)

    # Highlight layers (always full opacity, no legend)
    if has_highlight_pair and not highlight_df.empty:
        layers.append(_line_layer(highlight_df, "Actual", legend=False))
        layers.append(_line_layer(highlight_df, "Forecast", dash=[5, 5], legend=False))
        connector = alt.Chart(highlight_df[highlight_df['type'] == "Connector"]).mark_line(
            point=False, strokeDash=[5, 5]
        ).encode(
            x=alt.X(f"{config['x_field']}:T"),
            y=alt.Y(f"{config['y_field']}:Q"),
            color=alt.Color(
                f"{category_field}:N",
                scale=alt.Scale(domain=all_categories),
                legend=None
            )
        )
        layers.append(connector)

    # Toggle-enabled layers
    layers.append(_line_layer(other_df, "Actual", legend=True))
    layers.append(_line_layer(other_df, "Forecast", dash=[5, 5], legend=True))
    connector_other = alt.Chart(other_df[other_df['type'] == "Connector"]).mark_line(
        point=False, strokeDash=[5, 5]
    ).encode(
        x=alt.X(f"{config['x_field']}:T"),
        y=alt.Y(f"{config['y_field']}:Q"),
        color=alt.Color(
            f"{category_field}:N",
            scale=alt.Scale(domain=all_categories),
            legend=None  # connector doesn't need duplicate legend
        ),
        opacity=alt.condition(selection, alt.value(1), alt.value(0)) if selection else alt.value(1)  # was 0.15
    )
    if selection:
        connector_other = connector_other.add_params(selection)
    layers.append(connector_other)

    chart = alt.layer(*layers)
    if area_chart is not None:
        chart = chart.resolve_scale(color='independent')

    return chart.properties(height=340)


def _build_diff_area(df: pd.DataFrame, config: dict, highlight_cats, forecast: bool = False) -> alt.Chart:
    """
    Orchestrates building the differential (Surplus/Deficit) area layer.
    """
    category_field = config['category_field']
    x_field = config['x_field']
    y_field = config['y_field']
    baseline, other = highlight_cats

    pivot_df, to_datetime = _prepare_diff_area_base(
        df=df,
        config=config,
        highlight_cats=highlight_cats,
        forecast=forecast
    )
    if pivot_df is None:
        return None

    pivot_df, to_datetime = _insert_crossover_points(
        pivot_df=pivot_df,
        x_field=x_field,
        baseline=baseline,
        other=other,
        to_datetime=to_datetime
    )

    pivot_df = _finalize_diff_area_df(
        pivot_df=pivot_df,
        baseline=baseline,
        other=other
    )

    return _encode_diff_area(
        pivot_df=pivot_df,
        config=config,
        baseline=baseline,
        other=other,
        to_datetime=to_datetime
    )


# ---------------------------
# Differential area helpers
# ---------------------------

def _prepare_diff_area_base(df: pd.DataFrame, config: dict, highlight_cats, forecast: bool):
    """
    Filter, pivot and compute initial diff state.
    Returns (pivot_df, to_datetime_flag) or (None, None).
    """
    category_field = config['category_field']
    x_field = config['x_field']
    y_field = config['y_field']
    baseline, other = highlight_cats

    base_df = df.copy()
    if forecast and "type" in base_df.columns:
        base_df = base_df[base_df['type'] == "Actual"]

    base_df = base_df[base_df[category_field].isin(highlight_cats)]

    pivot_df = (
        base_df
        .pivot(index=x_field, columns=category_field, values=y_field)
        .dropna()
        .reset_index()
    )
    if pivot_df.empty:
        return None, None

    pivot_df['diff'] = pivot_df[baseline] - pivot_df[other]
    pivot_df['is_positive'] = pivot_df['diff'] >= 0

    to_datetime = pd.api.types.is_datetime64_any_dtype(pivot_df[x_field])
    return pivot_df, to_datetime


def _insert_crossover_points(pivot_df: pd.DataFrame, x_field: str, baseline: str, other: str, to_datetime: bool):
    """
    Insert interpolated crossover points so adjacent positive/negative
    areas meet without gaps.
    """
    # Determine if we need datetime conversion
    needs_datetime_conversion = False
    if to_datetime:
        x_numeric = pivot_df[x_field].view('int64').to_list()
    else:
        # Check if x_field is numeric, if not try to convert to datetime first
        if pd.api.types.is_numeric_dtype(pivot_df[x_field]):
            x_numeric = pivot_df[x_field].astype(float).to_list()
        else:
            # Likely datetime strings - convert to datetime then to numeric
            pivot_df[x_field] = pd.to_datetime(pivot_df[x_field])
            x_numeric = pivot_df[x_field].view('int64').to_list()
            to_datetime = True
            needs_datetime_conversion = True

    b_vals = pivot_df[baseline].to_list()
    o_vals = pivot_df[other].to_list()
    is_pos = pivot_df['is_positive'].to_list()

    new_rows = []
    for i in range(len(pivot_df) - 1):
        if is_pos[i] != is_pos[i + 1]:
            db = b_vals[i + 1] - b_vals[i]
            do = o_vals[i + 1] - o_vals[i]
            denom = (db - do)
            if denom == 0:
                continue
            f = (o_vals[i] - b_vals[i]) / denom
            if not (0 < f < 1):
                continue
            x_cross_num = x_numeric[i] + f * (x_numeric[i + 1] - x_numeric[i])
            y_cross = b_vals[i] + f * db
            x_cross = pd.to_datetime(int(x_cross_num)) if to_datetime else x_cross_num
            new_rows.append({
                x_field: x_cross,
                baseline: y_cross,
                other: y_cross,
                'diff': 0.0,
                'is_positive': is_pos[i]
            })
            new_rows.append({
                x_field: x_cross,
                baseline: y_cross,
                other: y_cross,
                'diff': 0.0,
                'is_positive': is_pos[i + 1]
            })

    if new_rows:
        pivot_df = pd.concat([pivot_df, pd.DataFrame(new_rows)], ignore_index=True)
        pivot_df = pivot_df.sort_values(x_field, kind='mergesort').reset_index(drop=True)

    return pivot_df, to_datetime


def _finalize_diff_area_df(pivot_df: pd.DataFrame, baseline: str, other: str) -> pd.DataFrame:
    """
    After crossover insertion, recompute grouping and bounds.
    """
    pivot_df['group_id'] = (pivot_df['is_positive'] != pivot_df['is_positive'].shift()).cumsum()
    pivot_df['diff_label'] = pivot_df['is_positive'].map({True: 'Surplus', False: 'Deficit'})
    pivot_df['upper'] = pivot_df[[baseline, other]].max(axis=1)
    pivot_df['lower'] = pivot_df[[baseline, other]].min(axis=1)
    return pivot_df


def _encode_diff_area(pivot_df: pd.DataFrame, config: dict, baseline: str, other: str, to_datetime: bool):
    """
    Encode the Altair differential area chart.
    """
    x_field = config['x_field']
    area = alt.Chart(pivot_df).mark_area().encode(
        x=f"{x_field}:T" if to_datetime else alt.X(f"{x_field}:Q"),
        y="upper:Q",
        y2="lower:Q",
        detail="group_id:N",
        color=alt.Color(
            "diff_label:N",
            scale=alt.Scale(domain=["Surplus", "Deficit"], range=["#a5d6a780", "#ef9a9a80"]),
            legend=alt.Legend(title="Difference")
        ),
        tooltip=[
            alt.Tooltip(f"{x_field}:T", title=config['x_label']) if to_datetime else alt.Tooltip(f"{x_field}:Q", title=config['x_label']),
            alt.Tooltip(f"{baseline}:Q", title=baseline, format=","),
            alt.Tooltip(f"{other}:Q", title=other, format=","),
            alt.Tooltip("diff_label:N", title="Status")
        ]
    )
    return area