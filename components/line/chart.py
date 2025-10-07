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
    """Multi-line chart without forecast."""
    encoding = _get_base_encoding(config, include_category=True)
    
    line_chart = alt.Chart(df).mark_line(
        point=True
    ).encode(**encoding)

    if 'category_area_highlight' in config:
        highlight_cats = config['category_area_highlight']
        if len(highlight_cats) == 2:
            area_chart = _build_diff_area(df, config, highlight_cats, forecast=False)
            if area_chart is not None:
                # Independent color scales: area uses diff sign, lines use categories
                return (area_chart + line_chart).resolve_scale(color='independent').properties(height=340)

    return line_chart.properties(height=340)


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
    """Multi-line chart with forecast."""
    base = alt.Chart(df)
    encoding = _get_base_encoding(config, include_type=True, include_category=True)
    
    # Actual lines (solid, color-coded)
    actual = base.transform_filter(
        alt.datum.type == "Actual"
    ).mark_line(point=True).encode(**encoding)
    
    # Forecast lines (dashed, color-coded)
    forecast = base.transform_filter(
        alt.datum.type == "Forecast"
    ).mark_line(point=True, strokeDash=[5, 5]).encode(**encoding)
    
    # Connector lines (dashed, color-coded, no points, minimal encoding)
    category_label = config.get('category_label') or config['category_field']
    connector = base.transform_filter(
        alt.datum.type == "Connector"
    ).mark_line(point=False, strokeDash=[5, 5]).encode(
        x=alt.X(f"{config['x_field']}:T"),
        y=alt.Y(f"{config['y_field']}:Q"),
        color=alt.Color(
            f"{config['category_field']}:N", 
            legend=alt.Legend(title=category_label)
        ),
    )
    
    chart = (actual + forecast + connector)

    if 'category_area_highlight' in config:
        highlight_cats = config['category_area_highlight']
        if len(highlight_cats) == 2:
            # Differential area only over Actual segment for clarity
            area_chart = _build_diff_area(df, config, highlight_cats, forecast=True)
            if area_chart is not None:
                chart = (area_chart + chart).resolve_scale(color='independent')

    return chart.properties(height=340)


def _build_diff_area(df: pd.DataFrame, config: dict, highlight_cats, forecast: bool = False) -> alt.Chart:
    """
    Build a differential area (green when first > second, red otherwise) between two categories.
    Inserts interpolated crossover points so adjacent colored areas meet without gaps.
    """
    category_field = config['category_field']
    x_field = config['x_field']
    y_field = config['y_field']
    baseline, other = highlight_cats

    base_df = df.copy()
    if forecast and "type" in base_df.columns:
        # Shade only the actual (historical) segment to avoid duplicated forecast overlays
        base_df = base_df[base_df['type'] == "Actual"]

    # Keep only the two categories we care about
    base_df = base_df[base_df[category_field].isin(highlight_cats)]

    # Pivot so each category is a column; require both present (dropna)
    pivot_df = (
        base_df
        .pivot(index=x_field, columns=category_field, values=y_field)
        .dropna()
        .reset_index()
    )
    if pivot_df.empty:
        return None  # Nothing to shade

    # Initial diff & sign
    pivot_df['diff'] = pivot_df[baseline] - pivot_df[other]
    pivot_df['is_positive'] = pivot_df['diff'] >= 0

    # --- Insert crossover (intersection) points to avoid visual gaps ---
    # We look between consecutive rows where is_positive changes and
    # linearly interpolate the exact point where the two series cross.
    if pd.api.types.is_datetime64_any_dtype(pivot_df[x_field]):
        # Work with int nanoseconds for interpolation
        x_numeric = pivot_df[x_field].view('int64').to_list()
        to_datetime = True
    else:
        x_numeric = pivot_df[x_field].astype(float).to_list()
        to_datetime = False

    b_vals = pivot_df[baseline].to_list()
    o_vals = pivot_df[other].to_list()
    is_pos = pivot_df['is_positive'].to_list()

    new_rows = []
    for i in range(len(pivot_df) - 1):
        if is_pos[i] != is_pos[i + 1]:
            # Solve for f in: b_i + f*(b_{i+1}-b_i) = o_i + f*(o_{i+1}-o_i)
            db = b_vals[i + 1] - b_vals[i]
            do = o_vals[i + 1] - o_vals[i]
            denom = (db - do)
            if denom == 0:
                continue  # Parallel between points; skip
            f = (o_vals[i] - b_vals[i]) / denom
            if not (0 < f < 1):
                continue  # Crossing outside the segment; skip
            x_cross_num = x_numeric[i] + f * (x_numeric[i + 1] - x_numeric[i])
            y_cross = b_vals[i] + f * db  # same as o line at crossing
            x_cross = pd.to_datetime(int(x_cross_num)) if to_datetime else x_cross_num
            # Two rows: one ending previous group, one starting next group
            new_rows.append({
                x_field: x_cross,
                baseline: y_cross,
                other: y_cross,
                'diff': 0.0,
                'is_positive': is_pos[i]  # belongs to previous segment
            })
            new_rows.append({
                x_field: x_cross,
                baseline: y_cross,
                other: y_cross,
                'diff': 0.0,
                'is_positive': is_pos[i + 1]  # belongs to next segment
            })

    if new_rows:
        pivot_df = pd.concat([pivot_df, pd.DataFrame(new_rows)], ignore_index=True)
        pivot_df = pivot_df.sort_values(x_field, kind='mergesort').reset_index(drop=True)

    # Recompute group ids after inserting crossover rows
    pivot_df['group_id'] = (pivot_df['is_positive'] != pivot_df['is_positive'].shift()).cumsum()
    # Map boolean to labeled categories
    pivot_df['diff_label'] = pivot_df['is_positive'].map({True: 'Surplus', False: 'Deficit'})
    # Bounds
    pivot_df['upper'] = pivot_df[[baseline, other]].max(axis=1)
    pivot_df['lower'] = pivot_df[[baseline, other]].min(axis=1)
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