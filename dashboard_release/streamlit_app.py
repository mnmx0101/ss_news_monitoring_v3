"""
South Sudan GDELT Risk Monitoring Dashboard
=============================================
6-tab Streamlit app mirroring the analytical pipeline:
  0. Panel Builder   — data overview per source
  1. Volume Trends   — multi-source article volume side-by-side
  2. Alerts & Alarms — heatmaps with static / dynamic thresholds
  3. Convergence     — cross-source alert convergence matrix
  4. National        — national incidence + peak identification
  5. Intelligence    — RAG + LLM summary feed
"""

import sys
from pathlib import Path

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# ── Project imports ───────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.validation import (
    METRIC_CONFIG,
    compute_alert_level,
    get_alert_matrices,
    compute_convergence,
    _build_alert_matrix,
)

RESULTS_DIR = PROJECT_ROOT / "results"

# ── Streamlit config ─────────────────────────────────────────────────────────
st.set_page_config(page_title="GDELT Risk Monitor -- South Sudan", layout="wide")

# ── Metric helpers ────────────────────────────────────────────────────────────
METRIC_LABELS = {k: v["title"] for k, v in METRIC_CONFIG.items()}
ORDERED_METRICS = ["n_events_total", "n_fatality_proxy", "avg_tone_mean", "num_mentions_sum"]
FIVE_SOURCES = ["eyeradio", "allafrica", "radiotamazuj", "sudantribune", "reliefweb"]

ALERT_COLORS = {0: "#F1EFE8", 1: "#FAC775", 2: "#E24B4A", 3: "#B4B2A9"}
ALERT_LABELS = {0: "normal", 1: "alert", 2: "alarm", 3: "no data"}
CONV_COLORS  = ["#F1EFE8", "#9FE1CB", "#FAC775", "#D85A30", "#E24B4A", "#7F77DD"]

# ── Data loading (cached) ────────────────────────────────────────────────────

@st.cache_data
def load_panel():
    try:
        df = pd.read_csv(RESULTS_DIR / "panel_df.csv")
        return df
    except Exception:
        return pd.DataFrame()


@st.cache_data
def load_convergence():
    try:
        return pd.read_csv(RESULTS_DIR / "convergence_df.csv")
    except Exception:
        return pd.DataFrame()


@st.cache_data
def load_summaries():
    try:
        return pd.read_csv(RESULTS_DIR / "summaries_df.csv")
    except Exception:
        return pd.DataFrame()


@st.cache_data
def load_peaks():
    try:
        return pd.read_csv(RESULTS_DIR / "peak_df.csv")
    except Exception:
        return pd.DataFrame()


def build_panels_dict(panel_df):
    """Reconstruct {source: DataFrame} dict from the flat panel CSV."""
    return {
        src: grp.drop(columns=["source"]).copy()
        for src, grp in panel_df.groupby("source")
        if src in FIVE_SOURCES
    }


# ── Dynamic threshold helper ─────────────────────────────────────────────────

def compute_alert_level_dynamic(series, direction, window):
    """Rolling-window alert classification (dynamic threshold)."""
    rolling_mu = series.rolling(window, center=True, min_periods=max(1, window // 2)).mean()
    rolling_sd = series.rolling(window, center=True, min_periods=max(1, window // 2)).std().fillna(0)
    out = pd.Series(0.0, index=series.index)
    obs = series.notna()
    if direction == "high":
        out[obs & (series >= rolling_mu + rolling_sd)]     = 1
        out[obs & (series >= rolling_mu + 2 * rolling_sd)] = 2
    else:
        out[obs & (series <= rolling_mu - rolling_sd)]     = 1
        out[obs & (series <= rolling_mu - 2 * rolling_sd)] = 2
    out[~obs] = 3
    return out


def build_alert_matrix_dynamic(panel, metric, agg_func, direction, window):
    """Like _build_alert_matrix but uses rolling thresholds."""
    plot_panel = panel.copy()
    plot_panel.loc[plot_panel["is_observed"] == 0, metric] = np.nan
    matrix = (
        plot_panel
        .groupby(["year_month", "ADM1_EN"])[metric]
        .agg(agg_func)
        .unstack("ADM1_EN")
    )
    return matrix.apply(
        lambda col: compute_alert_level_dynamic(col, direction=direction, window=window)
    )


def get_alert_matrices_dynamic(panels, metric, agg_func, direction, window):
    """Build dynamic-threshold alert matrices for each source, aligned."""
    matrices = {
        src: build_alert_matrix_dynamic(panel, metric, agg_func, direction, window)
        for src, panel in panels.items()
    }
    all_months = sorted(set().union(*[m.index   for m in matrices.values()]))
    all_adm1   = sorted(set().union(*[m.columns for m in matrices.values()]))
    return {
        src: m.reindex(index=all_months, columns=all_adm1).fillna(3)
        for src, m in matrices.items()
    }


# ── Alert matrix → long-form dataframe for Altair ────────────────────────────

def matrix_to_long(matrix, source_label):
    """Convert (month x ADM1) alert matrix to long-form DataFrame."""
    df = matrix.copy()
    df.index.name = "year_month"
    long = df.reset_index().melt(
        id_vars=["year_month"],
        var_name="ADM1_EN",
        value_name="alert_level",
    )
    long["source"] = source_label
    long["alert_level"] = long["alert_level"].astype(int)
    return long


# ══════════════════════════════════════════════════════════════════════════════
# LOAD DATA
# ══════════════════════════════════════════════════════════════════════════════
panel_df = load_panel()
conv_df  = load_convergence()
summ_df  = load_summaries()
peak_df  = load_peaks()

if panel_df.empty:
    st.error("No panel data found. Run `python run_pipeline.py` first.")
    st.stop()

panels = build_panels_dict(panel_df)

# ── Header ────────────────────────────────────────────────────────────────────
st.title("South Sudan GDELT Risk Monitoring Dashboard")
st.caption(
    "Multi-source anomaly detection, cross-source convergence validation, "
    "and LLM-powered intelligence briefings for conflict early warning."
)

tab0, tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Panel Builder",
    "Volume Trends",
    "Alerts & Alarms",
    "Convergence",
    "National Incidence",
    "Intelligence Feed",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 0 — Panel Builder (data overview)
# ══════════════════════════════════════════════════════════════════════════════
with tab0:
    st.header("Panel Builder -- Data Overview")
    st.markdown(
        "Each source's raw GDELT events are filtered, aggregated to ADM2 x month panels, "
        "balanced, and geo-matched to OCHA administrative boundaries."
    )

    rows = []
    for src in FIVE_SOURCES:
        if src not in panels:
            continue
        p = panels[src]
        rows.append({
            "Source": src,
            "Rows": len(p),
            "ADM2 units": p["ADM2_EN"].nunique(),
            "ADM1 states": p["ADM1_EN"].nunique(),
            "Months": p["year_month"].nunique(),
            "Date range": f"{p['year_month'].min()} -- {p['year_month'].max()}",
            "Total events": int(p["n_events_total"].sum()),
            "Observed rows": int(p["is_observed"].sum()),
        })
    summary_df = pd.DataFrame(rows)
    st.dataframe(summary_df, hide_index=True, width="stretch")

    # Geo-match quality per source
    st.subheader("Geo-match quality by source")
    geo_rows = []
    for src in FIVE_SOURCES:
        if src not in panels:
            continue
        p = panels[src]
        if "geo_match" not in p.columns:
            continue
        vc = p["geo_match"].value_counts()
        for level, count in vc.items():
            geo_rows.append({"Source": src, "Match level": level, "Count": count})
    if geo_rows:
        geo_df = pd.DataFrame(geo_rows)
        geo_pivot = geo_df.pivot_table(index="Source", columns="Match level", values="Count", fill_value=0).reset_index()
        st.dataframe(geo_pivot, hide_index=True, width="stretch")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Multi-Source Volume Trends
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.header("Multi-Source Article Volume Trends")
    st.markdown("Monthly event counts by ADM1, shown side-by-side per source.")

    panel_metrics = [m for m in ORDERED_METRICS if m in panel_df.columns]
    # also add other interesting columns
    extra = ["n_protest", "n_fight", "n_mass_violence", "goldstein_mean"]
    panel_metrics += [m for m in extra if m in panel_df.columns and m not in panel_metrics]

    sel_metric_t1 = st.selectbox(
        "Metric:", panel_metrics,
        format_func=lambda m: METRIC_LABELS.get(m, m),
        index=0,
        key="t1_metric",
    )

    agg_func_t1 = "mean" if sel_metric_t1 in ("avg_tone_mean", "goldstein_mean") else "sum"

    # Build aggregated data for all sources
    trend_parts = []
    for src in FIVE_SOURCES:
        if src not in panels:
            continue
        agg = (
            panels[src]
            .groupby(["year_month", "ADM1_EN"])[sel_metric_t1]
            .agg(agg_func_t1)
            .reset_index()
        )
        agg["source"] = src
        trend_parts.append(agg)

    if trend_parts:
        trend_df = pd.concat(trend_parts, ignore_index=True)
        x_tick_vals_t1 = trend_df["year_month"].sort_values().unique()[::6].tolist()
        chart = (
            alt.Chart(trend_df)
            .mark_bar()
            .encode(
                x=alt.X("year_month:O", title="Month",
                         axis=alt.Axis(labelAngle=-90, labelFontSize=5, values=x_tick_vals_t1)),
                y=alt.Y(f"{sel_metric_t1}:Q",
                         title=METRIC_LABELS.get(sel_metric_t1, sel_metric_t1)),
                color=alt.Color("ADM1_EN:N", title="ADM1"),
                tooltip=["year_month", "ADM1_EN", f"{sel_metric_t1}:Q"],
            )
            .properties(width=220, height=300)
            .facet(
                column=alt.Column("source:N", title="Source",
                                  sort=FIVE_SOURCES,
                                  header=alt.Header(labelFontWeight="bold")),
            )
            .resolve_scale(y="shared")
        )
        st.altair_chart(chart)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Alerts & Alarms Heatmaps
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.header("Alerts & Alarms Heatmaps")
    st.markdown(
        "SD-based anomaly classification per source and ADM1. "
        "**Alert** = 1-2 SD from mean. **Alarm** = 2+ SD from mean."
    )

    col_m, col_mode, col_win = st.columns(3)
    with col_m:
        sel_metric_t2 = st.selectbox(
            "Metric:", ORDERED_METRICS,
            format_func=lambda m: METRIC_LABELS.get(m, m),
            index=0,
            key="t2_metric",
        )
    with col_mode:
        threshold_mode = st.radio(
            "Threshold:", ["Static (full series)", "Dynamic (rolling)"],
            horizontal=True,
            key="t2_mode",
        )
    with col_win:
        roll_win = st.select_slider(
            "Rolling window (months):", [3, 6, 12],
            value=6,
            disabled=(threshold_mode != "Dynamic (rolling)"),
            key="t2_win",
        )

    cfg = METRIC_CONFIG[sel_metric_t2]

    with st.spinner("Computing alert matrices..."):
        if threshold_mode == "Static (full series)":
            matrices = get_alert_matrices(panels, sel_metric_t2, cfg["agg"], cfg["direction"])
        else:
            matrices = get_alert_matrices_dynamic(
                panels, sel_metric_t2, cfg["agg"], cfg["direction"], roll_win
            )

    # Convert to long-form for Altair
    long_parts = []
    for src in FIVE_SOURCES:
        if src not in matrices:
            continue
        long_parts.append(matrix_to_long(matrices[src], src))
    alert_long = pd.concat(long_parts, ignore_index=True)

    # Heatmap faceted by source
    alert_color = alt.Scale(
        domain=[0, 1, 2, 3],
        range=[ALERT_COLORS[0], ALERT_COLORS[1], ALERT_COLORS[2], ALERT_COLORS[3]],
    )
    all_months_sorted = sorted(alert_long["year_month"].unique())
    x_tick_vals = all_months_sorted[::6]

    heatmap = (
        alt.Chart(alert_long)
        .mark_rect()
        .encode(
            x=alt.X("year_month:O", title="Month",
                     axis=alt.Axis(labelAngle=-90, labelFontSize=5, values=x_tick_vals)),
            y=alt.Y("ADM1_EN:N", title="ADM1"),
            color=alt.Color(
                "alert_level:O",
                scale=alert_color,
                legend=alt.Legend(
                    title="Level",
                    labelExpr="datum.value == 0 ? 'normal' : datum.value == 1 ? 'alert' : datum.value == 2 ? 'alarm' : 'no data'",
                ),
            ),
            tooltip=["year_month", "ADM1_EN", "alert_level:O", "source:N"],
        )
        .properties(width=200, height=350)
        .facet(
            column=alt.Column("source:N", title="Source", sort=FIVE_SOURCES,
                              header=alt.Header(labelFontWeight="bold")),
        )
    )
    st.altair_chart(heatmap)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Convergence Matrix
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.header("Cross-Source Convergence")
    st.markdown(
        "How many sources simultaneously flag each ADM1 x month cell. "
        "Higher convergence = stronger signal of genuine ground-truth change."
    )

    col_m3, col_mode3, col_win3 = st.columns(3)
    with col_m3:
        sel_metric_t3 = st.selectbox(
            "Metric:", ORDERED_METRICS,
            format_func=lambda m: METRIC_LABELS.get(m, m),
            index=0,
            key="t3_metric",
        )
    with col_mode3:
        threshold_mode3 = st.radio(
            "Threshold:", ["Static (full series)", "Dynamic (rolling)"],
            horizontal=True,
            key="t3_mode",
        )
    with col_win3:
        roll_win3 = st.select_slider(
            "Rolling window (months):", [3, 6, 12],
            value=6,
            disabled=(threshold_mode3 != "Dynamic (rolling)"),
            key="t3_win",
        )

    cfg3 = METRIC_CONFIG[sel_metric_t3]

    with st.spinner("Computing convergence..."):
        if threshold_mode3 == "Static (full series)":
            mat3 = get_alert_matrices(panels, sel_metric_t3, cfg3["agg"], cfg3["direction"])
        else:
            mat3 = get_alert_matrices_dynamic(
                panels, sel_metric_t3, cfg3["agg"], cfg3["direction"], roll_win3
            )
        conv_matrix = compute_convergence(mat3)

    # Convert to long form
    conv_matrix_named = conv_matrix.copy()
    conv_matrix_named.index.name = "year_month"
    conv_long = conv_matrix_named.reset_index().melt(
        id_vars=["year_month"],
        var_name="ADM1_EN",
        value_name="convergence_score",
    )
    conv_long["convergence_score"] = conv_long["convergence_score"].astype(int)

    # Heatmap
    conv_color = alt.Scale(
        domain=list(range(len(CONV_COLORS))),
        range=CONV_COLORS,
    )
    all_months_conv = sorted(conv_long["year_month"].unique())
    x_ticks_conv = all_months_conv[::6]

    conv_heatmap = (
        alt.Chart(conv_long)
        .mark_rect()
        .encode(
            x=alt.X("year_month:O", title="Month",
                     axis=alt.Axis(labelAngle=-90, labelFontSize=6, values=x_ticks_conv)),
            y=alt.Y("ADM1_EN:N", title="ADM1"),
            color=alt.Color(
                "convergence_score:O",
                scale=conv_color,
                title="# sources at alert+",
            ),
            tooltip=["year_month", "ADM1_EN", "convergence_score"],
        )
        .properties(height=450)
    )
    st.altair_chart(conv_heatmap, width="stretch")

    # Peak table
    st.subheader("Peak periods (convergence >= threshold)")
    conv_thresh = st.slider("Minimum convergence score:", 1, 5, 3, key="t3_thresh")
    peaks = conv_long[conv_long["convergence_score"] >= conv_thresh].sort_values(
        ["convergence_score", "year_month"], ascending=[False, True]
    )
    st.caption(f"{len(peaks)} cells with convergence >= {conv_thresh}")
    st.dataframe(peaks, hide_index=True, height=300, width="stretch")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — National Incidence & Peak Identification
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.header("National Incidence & Peak Identification")
    st.markdown(
        "National-level view: how many ADM1 regions show alerts/alarms per month, "
        "by source and by convergence level."
    )

    # Controls
    col_m4, col_mode4, col_win4, col_roll4 = st.columns(4)
    with col_m4:
        sel_metric_t4 = st.selectbox(
            "Metric:", ORDERED_METRICS,
            format_func=lambda m: METRIC_LABELS.get(m, m),
            index=0,
            key="t4_metric",
        )
    with col_mode4:
        threshold_mode4 = st.radio(
            "Threshold:", ["Static", "Dynamic"],
            horizontal=True,
            key="t4_mode",
        )
    with col_win4:
        roll_win4 = st.select_slider(
            "Alert window:", [3, 6, 12],
            value=6,
            disabled=(threshold_mode4 != "Dynamic"),
            key="t4_win",
        )
    with col_roll4:
        trend_win = st.select_slider(
            "Trend smoothing:", [3, 6, 12],
            value=6,
            key="t4_trend",
        )

    cfg4 = METRIC_CONFIG[sel_metric_t4]

    with st.spinner("Computing national incidence..."):
        if threshold_mode4 == "Static":
            mat4 = get_alert_matrices(panels, sel_metric_t4, cfg4["agg"], cfg4["direction"])
        else:
            mat4 = get_alert_matrices_dynamic(
                panels, sel_metric_t4, cfg4["agg"], cfg4["direction"], roll_win4
            )
        conv4 = compute_convergence(mat4)

    # ── Per-source incidence (# ADM1s at alert+ per month) ────────────────
    st.subheader("Per-source alert incidence")
    src_inc_parts = []
    for src in FIVE_SOURCES:
        if src not in mat4:
            continue
        m = mat4[src]
        alert_count = ((m == 1) | (m == 2)).sum(axis=1)
        s = alert_count.reset_index()
        s.columns = ["year_month", "n_adm1_alert"]
        s["source"] = src
        src_inc_parts.append(s)

    if src_inc_parts:
        src_inc = pd.concat(src_inc_parts, ignore_index=True)
        x_tick_vals_t4 = sorted(src_inc["year_month"].unique())[::6]
        inc_chart = (
            alt.Chart(src_inc)
            .mark_bar(opacity=0.7)
            .encode(
                x=alt.X("year_month:O", title="Month",
                         axis=alt.Axis(labelAngle=-90, labelFontSize=5, values=x_tick_vals_t4)),
                y=alt.Y("n_adm1_alert:Q", title="# ADM1s at alert+"),
                color=alt.Color("source:N", title="Source"),
                tooltip=["year_month", "source", "n_adm1_alert"],
            )
            .properties(width=200, height=250)
            .facet(
                column=alt.Column("source:N", sort=FIVE_SOURCES,
                                  header=alt.Header(labelFontWeight="bold")),
            )
        )
        st.altair_chart(inc_chart)

    # ── National convergence stacked bar ──────────────────────────────────
    st.subheader("Convergence stacked bar (national)")

    conv4_named = conv4.copy()
    conv4_named.index.name = "year_month"
    conv_long4 = conv4_named.reset_index().melt(
        id_vars=["year_month"],
        var_name="ADM1_EN",
        value_name="score",
    )
    conv_long4["score"] = conv_long4["score"].astype(int)

    # For each month, count ADM1s at each convergence level (1,2,3,4,5)
    stacked_parts = []
    for level in range(1, 6):
        grp = (
            conv_long4[conv_long4["score"] == level]
            .groupby("year_month")
            .size()
            .reset_index(name="n_adm1")
        )
        grp["conv_level"] = f"{level} src"
        stacked_parts.append(grp)
    stacked = pd.concat(stacked_parts, ignore_index=True)

    # rolling mean total
    total_per_month = (
        conv_long4[conv_long4["score"] >= 1]
        .groupby("year_month")
        .size()
        .reset_index(name="total")
        .sort_values("year_month")
    )
    total_per_month["rolling"] = (
        total_per_month["total"]
        .rolling(trend_win, center=True, min_periods=1)
        .mean()
    )

    all_months4 = sorted(stacked["year_month"].unique())
    x_ticks4 = all_months4[::6]

    bar4 = (
        alt.Chart(stacked)
        .mark_bar()
        .encode(
            x=alt.X("year_month:O", title="Month",
                     axis=alt.Axis(labelAngle=-90, labelFontSize=6, values=x_ticks4)),
            y=alt.Y("n_adm1:Q", title="# ADM1s"),
            color=alt.Color(
                "conv_level:N",
                scale=alt.Scale(
                    domain=[f"{n} src" for n in range(1, 6)],
                    range=CONV_COLORS[1:6],
                ),
                title="Convergence level",
            ),
            order=alt.Order("conv_level:N"),
            tooltip=["year_month", "conv_level", "n_adm1"],
        )
        .properties(height=350)
    )
    line4 = (
        alt.Chart(total_per_month)
        .mark_line(color="#2C2C2A", strokeWidth=2)
        .encode(
            x="year_month:O",
            y=alt.Y("rolling:Q", title=""),
            tooltip=["year_month", alt.Tooltip("rolling:Q", format=".1f", title="Rolling mean")],
        )
    )
    st.altair_chart((bar4 + line4).resolve_scale(y="shared"), width="stretch")

    # ── Peak table for intelligence feed ──────────────────────────────────
    st.subheader("Peak periods by region")
    st.markdown("Months x ADM1 with highest convergence -- candidates for intelligence feed.")
    peak_thresh4 = st.slider("Minimum convergence:", 1, 5, 2, key="t4_thresh")
    peak_table = (
        conv_long4[conv_long4["score"] >= peak_thresh4]
        .sort_values(["score", "year_month"], ascending=[False, True])
        .rename(columns={"score": "convergence_score"})
    )
    st.caption(f"{len(peak_table)} ADM1-months with convergence >= {peak_thresh4}")
    st.dataframe(peak_table[["year_month", "ADM1_EN", "convergence_score"]],
                 hide_index=True, height=400, width="stretch")
    
    # Pass to session state for Tab 5
    st.session_state['peak_table_from_t4'] = peak_table

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — Intelligence Feed (RAG + LLM)
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.header("Intelligence Feed")
    st.markdown("Monitor and generate contextual briefings for validated signal peaks.")

    # ── API Key Configuration ─────────────────────────────────────────────
    user_api_key = st.text_input("OpenAI API Key (Required for generation):", type="password", help="Enter your personal OpenAI API key to enable on-demand summaries.")

    # ── On-demand generator ───────────────────────────────────────────────
    st.subheader("Generate new intelligence briefing")
    
    # Peak table source: either from Tab 4 session state OR from file if exists (for backwards compat)
    current_peaks = st.session_state.get('peak_table_from_t4', pd.DataFrame())
    
    if current_peaks.empty and not peak_df.empty:
        current_peaks = peak_df.rename(columns={"convergence_score": "score"}) # alignment
        if "convergence_score" not in current_peaks.columns and "score" in current_peaks.columns:
             current_peaks = current_peaks.rename(columns={"score": "convergence_score"})

    if current_peaks.empty:
        st.warning("No peaks identified. Please visit the **National Incidence** tab first to detect signal peaks.")
    else:
        st.markdown(
            "Select a region and period from the peaks identified in the National Incidence tab. "
            "Only specialized sources (ReliefWeb, Radio Tamazuj, Eye Radio) are available for summarization."
        )
        
        adm1_opts = sorted(current_peaks["ADM1_EN"].unique())
        col_g1, col_g2, col_g3 = st.columns(3)
        with col_g1:
            gen_adm1 = st.selectbox("ADM1 Region:", adm1_opts, key="gen_adm1")
        with col_g2:
            relevant_months = sorted(current_peaks[current_peaks["ADM1_EN"] == gen_adm1]["year_month"].unique())
            gen_ym = st.selectbox("Period:", relevant_months, index=len(relevant_months)-1, key="gen_ym")
        with col_g3:
            gen_src = st.selectbox("Source:", ['eyeradio', 'radiotamazuj', 'reliefweb'], key="gen_src")

        col_b1, col_b2 = st.columns(2)
        
        # Lazy loader for raw data to avoid "collapse"
        def get_raw_articles_lazy(adm1, ym, source):
            raw_path = Path("data/gdelt_raw.csv.gz")
            if not raw_path.exists():
                return pd.DataFrame()
            
            from src.sources import categorize_source
            # Load minimal columns and filter
            raw_iter = pd.read_csv(raw_path, compression='gzip', 
                                   usecols=['ActionGeo_ADM2Code', 'SOURCEURL', 'MonthYear'],
                                   chunksize=50000)
            
            # Prepare lookup with consistent type
            adm_lookup = panel_df[['ActionGeo_ADM2Code', 'ADM1_EN']].drop_duplicates()
            adm_lookup['ActionGeo_ADM2Code'] = adm_lookup['ActionGeo_ADM2Code'].astype(str)
            filtered_parts = []
            
            target_ym_code = int(ym.replace("-", ""))
            
            for chunk in raw_iter:
                # Filter by month first (fastest)
                chunk = chunk[chunk['MonthYear'] == target_ym_code]
                if chunk.empty: continue
                
                # Ensure type match for ADM2Code
                chunk['ActionGeo_ADM2Code'] = chunk['ActionGeo_ADM2Code'].astype(str)
                
                # Categorize and filter by source
                chunk['source_grouped'] = chunk['SOURCEURL'].apply(categorize_source)
                chunk = chunk[chunk['source_grouped'] == source]
                if chunk.empty: continue
                
                # Merge and filter by ADM1
                chunk = chunk.merge(adm_lookup, on='ActionGeo_ADM2Code', how='inner')
                chunk = chunk[chunk['ADM1_EN'] == adm1]
                if not chunk.empty:
                    filtered_parts.append(chunk)
            
            if not filtered_parts:
                return pd.DataFrame()
            
            res = pd.concat(filtered_parts)
            res['year_month'] = ym # Add the YYYY-MM column for scraper compatibility
            res['usable'] = True 
            return res

        with col_b1:
            if st.button("Check Stats & Estimate Cost", type="secondary", use_container_width=True):
                with st.spinner("Retrieving article stats..."):
                    from src.scraper import scrape_peak_articles
                    from src.llm import inspect_articles
                    
                    # Lazy load metadata then scrape for stats
                    meta = get_raw_articles_lazy(gen_adm1, gen_ym, gen_src)
                    if meta.empty:
                        st.info(f"No articles found for {gen_adm1} | {gen_ym} | {gen_src}")
                    else:
                        scraped = scrape_peak_articles(meta, gen_adm1, gen_ym, gen_src, delay=0.1)
                        stats_df, total_chars = inspect_articles(scraped)
                        est_tokens = total_chars / 4
                        est_cost = (est_tokens / 1_000_000) * 0.15 # gpt-4o-mini
                        
                        st.success(f"Article stats retrieved.")
                        st.write(f"- **Articles**: {len(scraped)}")
                        st.write(f"- **Est. Input Tokens**: {int(est_tokens):,}")
                        st.write(f"- **Est. Cost (USD)**: < $0.01 (${est_cost:,.5f})")
                        with st.expander("Show article list"):
                            st.dataframe(stats_df[['url', 'n_chars']], hide_index=True)

        with col_b2:
            if st.button("Generate Summary", type="primary", use_container_width=True):
                if not user_api_key:
                    st.error("Please provide an OpenAI API key above.")
                else:
                    with st.spinner("Scraping and summarizing..."):
                        from src.llm import summarize_conflict
                        from src.scraper import scrape_peak_articles # still needed for full text
                        
                        # We use the filtered list to feed into the scraper
                        articles_to_scrape = get_raw_articles_lazy(gen_adm1, gen_ym, gen_src)
                        
                        if articles_to_scrape.empty:
                            st.error("No content found to summarize.")
                        else:
                            # We pass the pre-filtered df to the summarizer
                            # Wait, summarize_conflict expects a df with full text.
                            # scrape_peak_articles would normally do the scraping.
                            # I'll use scrape_peak_articles by passing it my filtered list? 
                            # No, scrape_peak_articles takes peak_df.
                            # I'll create a new helper or modify how I call it.
                            
                            # Actually, I'll pass the filtered df TO summarize_conflict 
                            # BUT summarize_conflict doesn't scrape.
                            # I'll use scrape_peak_articles but use my filtered df AS the 'peak_df'.
                            scraped_with_text = scrape_peak_articles(articles_to_scrape, gen_adm1, gen_ym, gen_src)
                            
                            if scraped_with_text['usable'].sum() == 0:
                                st.error("Failed to extract usable text from sources.")
                            else:
                                summary = summarize_conflict(scraped_with_text, gen_adm1, gen_ym, gen_src, api_key=user_api_key)
                                if summary:
                                    st.markdown("---")
                                    st.subheader("Generated Briefing")
                                    with st.container(border=True):
                                        st.caption(f"**Severity:** {summary.get('severity', 'N/A')} | **Actors:** {', '.join(summary.get('actors', [])) if summary.get('actors') else 'N/A'}")
                                        st.markdown(f"**Briefing:** {summary.get('overall_summary')}")
                                        if summary.get('humanitarian'):
                                            st.markdown(f"**Humanitarian:** {summary.get('humanitarian')}")
                                        
                                        with st.expander("🔍 Show transparency details"):
                                            st.markdown("**Generated Prompt:**")
                                            st.code(summary.get('generated_prompt', 'N/A'), language="text")
                                            st.markdown("**Article Sources:**")
                                            for url in summary.get('source_urls', []):
                                                st.markdown(f"- [{url}]({url})")
                                else:
                                    st.error("Summarization failed.")

    # ── Existing summaries ────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("Saved Intelligence Briefings")
    st.info("💡 **Note:** The briefings below are samples generated during previous pipeline runs. For the most up-to-date analysis of latest signal spikes, use the generator above.")

    if summ_df.empty:
        st.write("No saved briefings available.")
    else:
        col_fa, col_fb, col_fc = st.columns(3)
        with col_fa:
            adm1_opts = sorted(summ_df["adm1"].unique()) if "adm1" in summ_df.columns else []
            sel_adm1 = st.selectbox("Filter Region:", ["All"] + adm1_opts, key="t5_adm1")
        with col_fb:
            src_opts = sorted(summ_df["source"].unique()) if "source" in summ_df.columns else []
            sel_src = st.selectbox("Filter Source:", ["All"] + src_opts, key="t5_src")
        with col_fc:
            ym_opts = sorted(summ_df["year_month"].unique()) if "year_month" in summ_df.columns else (
                sorted(summ_df["period"].unique()) if "period" in summ_df.columns else []
            )
            sel_ym = st.selectbox("Filter Period:", ["All"] + list(ym_opts), key="t5_ym")

        display_df = summ_df.copy()
        if sel_adm1 != "All" and "adm1" in display_df.columns:
            display_df = display_df[display_df["adm1"] == sel_adm1]
        if sel_src != "All" and "source" in display_df.columns:
            display_df = display_df[display_df["source"] == sel_src]
        if sel_ym != "All":
            ym_col = "year_month" if "year_month" in display_df.columns else "period"
            display_df = display_df[display_df[ym_col] == sel_ym]

        st.caption(f"Showing {len(display_df)} sample briefings")

        for _, row in display_df.iterrows():
            with st.container(border=True):
                adm1_val = row.get("adm1", row.get("adm1_region", "Unknown"))
                ym_val = row.get("year_month", row.get("period", "Unknown"))
                src_val = row.get("source", "")
                severity = row.get("severity", "N/A")

                severity_colors = {"low": "green", "medium": "orange", "high": "red", "critical": "red"}
                sev_color = severity_colors.get(str(severity).lower(), "gray")

                st.markdown(f"### {adm1_val} -- {ym_val} ({src_val})")
                st.markdown(f"**Severity:** :{sev_color}[{severity}] &nbsp; | &nbsp; **Actors:** {row.get('actors', 'N/A')}")
                st.markdown(f"**Briefing:** {row.get('overall_summary', 'No summary available.')}")
                humanitarian = row.get("humanitarian")
                if pd.notna(humanitarian) and str(humanitarian).strip():
                    st.markdown(f"**Humanitarian impact:** {humanitarian}")
                key_events = row.get("key_events")
                if pd.notna(key_events) and str(key_events).strip():
                    st.markdown(f"**Key events:** {key_events}")
