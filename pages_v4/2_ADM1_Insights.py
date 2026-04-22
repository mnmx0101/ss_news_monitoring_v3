"""
ADM1 Insights V3 — Region drilldown line chart with threshold bands and IPC event overlays.
"""

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

from utils.data_loader import load_data
from thresholds import (
    classify_region, compute_country_stats,
    THRESHOLD_DESCRIPTIONS
)
from ipc_events import expand_validation_events, IPC_VALIDATION_EVENTS
from reference_events import get_events_for_topic_and_adm1

st.title("🗺️ ADM1 — State-Level Insights")
st.markdown(
    "Drill into a specific state's article trend over time. "
    "Alerts and alarms are computed using the same threshold logic as the National Overview. "
    "Known IPC crisis events are annotated directly on the chart for validation."
)

# ── DATA ──────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading data…")
def get_base_df():
    df = load_data()
    df = df[df["retrieve_source"] == "radiotamazuj"].copy()
    # Relabel Abyei Region → Warrap
    df.loc[df["adm1_name_final"].str.contains("Abyei", case=False, na=False), "adm1_name_final"] = "Warrap"
    return df

df_raw = get_base_df()
if df_raw.empty:
    st.error("No data for Radio Tamazuj.")
    st.stop()

all_labels = sorted([l for l in df_raw["Label"].dropna().unique() if l != "Uncategorized"])
all_regions = sorted(df_raw["adm1_name_final"].unique())

# ── SIDEBAR CONTROLS ──────────────────────────────────────────────────────────
with st.sidebar:
    st.header("📊 Controls")

    st.markdown("#### 📍 Region")
    st.caption("Select the state you want to examine closely.")
    selected_region = st.selectbox("State (ADM1)", options=all_regions, label_visibility="collapsed")

    st.markdown("#### 📋 Topic")
    st.caption("The thematic category to analyse (e.g., Conflict and Violence, Food Crisis).")
    selected_topic = st.selectbox("Topic", options=all_labels, label_visibility="collapsed")

    st.markdown("#### 📐 Metric")
    st.caption(
        "**Article Count** — number of unique articles in that month.  \n"
        "**Sentiment Score** — intensity of the selected tone (scales 0–1). Because it measures intensity regardless of direction, it must be interpreted alongside a specific Tone (Positive or Negative)."
    )
    metric = st.radio("Metric", ["Article Count", "Sentiment Score"], label_visibility="collapsed")

    st.markdown("#### 🎭 Tone")
    if metric == "Sentiment Score":
        tone_opts = ["Positive", "Negative", "Neutral"]
        st.caption("Tone is required when using Sentiment Score ('All' is disabled to avoid mixing opposite signals).")
    else:
        tone_opts = ["All", "Positive", "Negative", "Neutral"]
        st.caption("Filter articles by overall tone, or keep 'All' for everything.")
    tone = st.selectbox("Tone", options=tone_opts, label_visibility="collapsed")

    st.markdown("---")
    st.markdown("#### 🔬 Threshold Methods")
    active_methods = st.multiselect(
        "Select Methods (Consensus mode active if >1)",
        options=["categorical", "percentile", "tukey", "zscore"],
        default=["categorical"],
        format_func={"percentile": "Percentile", "tukey": "Tukey Fence (IQR)", "zscore": "Z-Score (SD)", "categorical": "Categorical (National Avg)"}.get,
        label_visibility="collapsed"
    )

    if not active_methods:
        st.warning("Please select at least one method.")
        st.stop()

    with st.expander("ℹ️ Details & Parameters"):
        st.markdown("**Parameters applied unconditionally to the enabled methods:**")
        p1_in = st.slider("Alert percentile (p1)", 50, 99, 75)
        p2_in = st.slider("Alarm percentile (p2)", 51, 100, 90)
        k_in = st.slider("Fence multiplier (k)", 0.5, 3.0, 1.5, 0.1)
        sd1_in = st.slider("Alert SD multiplier", 0.5, 3.0, 1.0, 0.1)
        sd2_in = st.slider("Alarm SD multiplier", 0.5, 4.0, 2.0, 0.1)
        method_params = {"p1": p1_in, "p2": p2_in, "k": k_in, "sd1": sd1_in, "sd2": sd2_in}

    N = st.slider("Min History (N months)", 1, 36, 24)
    st.caption("Regions with fewer than N months use nationally-scaled thresholds (⚠️).")

    st.markdown("---")

# ── APPLY TONE FILTER ─────────────────────────────────────────────────────────
df_filtered = df_raw.copy()
if tone != "All":
    df_filtered = df_filtered[df_filtered["sentiment_label"].str.lower() == tone.lower()]

metric_col = "article_count" if metric == "Article Count" else "sentiment_score"

# ── BUILD PANEL ───────────────────────────────────────────────────────────────
df_clean = df_filtered.drop_duplicates(subset=["adm1_name_final", "yearmon", "Label", "title"])
panel = df_clean.groupby(["adm1_name_final", "yearmon", "Label"]).agg(
    article_count=("url", "count"),
    sentiment_score=("sentiment_score", "mean")
).reset_index()
topic_panel = panel[panel["Label"] == selected_topic].copy()

if topic_panel.empty:
    st.warning(f"No data for **{selected_topic}** with tone **{tone}**.")
    st.stop()

# ── CLASSIFY ──────────────────────────────────────────────────────────────────
region_df = topic_panel[topic_panel["adm1_name_final"] == selected_region].copy()
if region_df.empty:
    st.warning(f"No observations for **{selected_region}** under current filters.")
    st.stop()

# Compute consensus
tooltips_methods = []
for m in active_methods:
    c_p1, c_p2, c_med = compute_country_stats(topic_panel, metric_col, m, method_params)
    m_cls = classify_region(region_df, metric_col, m, method_params, c_p1, c_p2, c_med, N)
    region_df[f"status_{m}"] = m_cls["status"]
    region_df[f"p1_{m}"] = m_cls["p1"]
    region_df[f"p2_{m}"] = m_cls["p2"]
    tooltips_methods.extend([
        alt.Tooltip(f"status_{m}:N", title=f"Status ({m})"),
        alt.Tooltip(f"p1_{m}:Q", title=f"Alert ({m})", format=".2f"),
        alt.Tooltip(f"p2_{m}:Q", title=f"Alarm ({m})", format=".2f"),
    ])

def compute_consensus(row):
    alarms = sum(1 for m in active_methods if row[f"status_{m}"] == "Alarm")
    alerts = sum(1 for m in active_methods if row[f"status_{m}"] == "Alert")
    if len(active_methods) > 1:
        if alarms >= 2: return "Alarm"
        if (alarms + alerts) >= 2: return "Alert"
        return "No Concern"
    else:
        return row[f"status_{active_methods[0]}"]

region_df["status"] = region_df.apply(compute_consensus, axis=1)
region_df["yearmon_date"] = pd.to_datetime(region_df["yearmon"])
reg_data = region_df.sort_values("yearmon_date")

is_fallback = len(reg_data) < N
if is_fallback:
    st.warning(
        f"⚠️ **{selected_region}** has fewer than {N} observed months — thresholds are "
        f"nationally-scaled. Interpret signals with extra caution."
    )

c1, c2, c3 = st.columns(3)
c1.metric("Observed Months", len(reg_data))
latest_status = reg_data.iloc[-1]["status"]
status_icon = {"No Concern": "🟢", "Alert": "🟠", "Alarm": "🔴"}.get(latest_status, "⚪")
c2.metric("Latest Consensus Status", f"{status_icon} {latest_status}")
c3.metric("Methods Running", len(active_methods))

st.markdown("---")

# ── CHART ─────────────────────────────────────────────────────────────────────
chart_layers = []

if len(active_methods) == 1:
    m = active_methods[0]
    p1_val = reg_data[f"p1_{m}"].iloc[0]
    p2_val = reg_data[f"p2_{m}"].iloc[0]
    p1_rule = alt.Chart(pd.DataFrame({"p1": [p1_val]})).mark_rule(
        strokeDash=[6, 4], color="#ff9800", strokeWidth=2
    ).encode(y="p1:Q")
    p2_rule = alt.Chart(pd.DataFrame({"p2": [p2_val]})).mark_rule(
        strokeDash=[6, 4], color="#f44336", strokeWidth=2
    ).encode(y="p2:Q")
    chart_layers.extend([p1_rule, p2_rule])

line = alt.Chart(reg_data).mark_line(strokeWidth=2.5, color="#1565C0").encode(
    x=alt.X("yearmon_date:T", title="Month"),
    y=alt.Y(f"{metric_col}:Q", title=metric),
    tooltip=["yearmon:N", f"{metric_col}:Q", "status:N"]
)

points = alt.Chart(reg_data).mark_circle(size=100).encode(
    x="yearmon_date:T",
    y=f"{metric_col}:Q",
    color=alt.Color("status:N", scale=alt.Scale(
        domain=["No Concern", "Alert", "Alarm"],
        range=["#4CAF50", "#ff9800", "#f44336"]
    )),
    tooltip=["yearmon:N", alt.Tooltip(f"{metric_col}:Q", title="Metric"), alt.Tooltip("status:N", title="Consensus")] + tooltips_methods
)

chart_layers.extend([line, points])

# Overlay reference events for this topic + region
ev_df = get_events_for_topic_and_adm1(selected_topic, selected_region)
if not ev_df.empty:
    t_min = reg_data["yearmon_date"].min()
    t_max = reg_data["yearmon_date"].max()
    ev_df = ev_df[(ev_df["date"] >= t_min) & (ev_df["date"] <= t_max)]
    if not ev_df.empty:
        ev_rules = alt.Chart(ev_df).mark_rule(
            strokeDash=[4, 3], color="#333", strokeWidth=1
        ).encode(
            x="date:T",
            tooltip=[alt.Tooltip("label:N", title="Event"),
                     alt.Tooltip("period:N", title="Period")]
        )
        ev_labels = alt.Chart(ev_df).mark_text(
            align="left", angle=270, fontSize=9, dy=-5, dx=3, color="#333"
        ).encode(
            x="date:T",
            text="label:N"
        )
        chart_layers.extend([ev_rules, ev_labels])

st.subheader(f"📈 {selected_region} — {selected_topic}")
st.caption(
    "The blue line shows monthly article count (or sentiment). "
    + ("Orange/Red dashed lines are Alert/Alarm thresholds." if len(active_methods) == 1 else "Threshold lines hidden in Consensus mode to avoid clutter.")
    + " Dashed black vertical lines mark reference events."
)

final_chart = alt.layer(*chart_layers).properties(height=450).interactive()
st.altair_chart(final_chart, use_container_width=True)

# ── CONSENSUS HEATMAP (always shown) ─────────────────────────────────────────
st.markdown("---")
st.subheader("🔬 Method × Month Breakdown")
METHOD_LABELS = {"percentile": "Percentile", "tukey": "Tukey (IQR)", "zscore": "Z-Score (SD)", "categorical": "Categorical (Nat. Avg)"}

if len(active_methods) == 1:
    st.caption(
        "Only one method is active — the chart above already shows its thresholds as dashed lines. "
        "Enable additional methods via the sidebar to see how they agree or disagree over time."
    )
else:
    st.caption(
        "Each row is a threshold method; the bottom row shows the final **Consensus** outcome. "
        "A month reaches **Alarm** only when ≥ 2 methods flag Alarm; **Alert** when ≥ 2 flag Alert or Alarm. "
        "Use this heatmap to see where methods agree (all red/orange) vs. diverge (mixed colours)."
    )

# Build long-form dataframe: one row per (method, month)
heatmap_rows = []
for m in active_methods:
    for _, row in reg_data.iterrows():
        heatmap_rows.append({
            "Month": row["yearmon"],
            "Method": METHOD_LABELS.get(m, m),
            "Status": row[f"status_{m}"],
            "SortKey": 0  # methods above consensus
        })
# Add consensus row
for _, row in reg_data.iterrows():
    heatmap_rows.append({
        "Month": row["yearmon"],
        "Method": "⚡ Consensus",
        "Status": row["status"],
        "SortKey": 1
    })

hm_df = pd.DataFrame(heatmap_rows)

# Row order: methods first (sorted), then Consensus at the bottom
method_order = [METHOD_LABELS.get(m, m) for m in active_methods] + ["⚡ Consensus"]

heatmap = alt.Chart(hm_df).mark_rect(stroke="white", strokeWidth=1.5).encode(
    x=alt.X("Month:O",
            sort=sorted(hm_df["Month"].unique()),
            title="Month",
            axis=alt.Axis(labelAngle=-45, labelOverlap="greedy")),
    y=alt.Y("Method:N",
            sort=method_order,
            title=None,
            axis=alt.Axis(labelFontSize=12)),
    color=alt.Color("Status:N",
                    scale=alt.Scale(
                        domain=["No Concern", "Alert", "Alarm"],
                        range=["#4CAF50", "#ff9800", "#f44336"]
                    ),
                    legend=alt.Legend(title="Status")),
    tooltip=["Month:O", "Method:N", "Status:N"]
).properties(height=max(80, 45 * (len(active_methods) + 1)))

st.altair_chart(heatmap, use_container_width=True)
