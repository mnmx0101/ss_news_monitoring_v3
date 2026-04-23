"""
National Overview V3 — ADM1 & ADM2 heatmaps with 3 threshold methods,
interactive threshold editor, and fallback warnings.
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
    classify_region, compute_country_stats, compute_thresholds,
    THRESHOLD_DESCRIPTIONS
)
from reference_events import get_events_for_topic

st.title("🌍 National Signal Overview")
st.markdown(
    "Monitor alert and alarm patterns across all South Sudan states and counties. "
    "All data comes from Radio Tamazuj. Use the sidebar to configure your analysis parameters."
)

# ── SHARED DATA LOAD ──────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading Radio Tamazuj articles…")
def get_base_df():
    df = load_data()
    df = df[df["retrieve_source"] == "radiotamazuj"].copy()
    # Relabel Abyei Region → Warrap (disputed area administered under Warrap for analysis)
    df.loc[df["adm1_name_final"].str.contains("Abyei", case=False, na=False), "adm1_name_final"] = "Warrap"
    return df

df_raw = get_base_df()

if df_raw.empty:
    st.error("No data available for Radio Tamazuj.")
    st.stop()

all_labels = sorted([l for l in df_raw["Label"].dropna().unique() if l != "Uncategorized"])

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("📊 Analysis Controls")

    st.markdown("#### 📋 Topic")
    st.caption(
        "Choose the thematic category to analyse. Each article is tagged with the topic "
        "that most closely matches its content (e.g., Conflict, Food Crisis)."
    )
    selected_topic = st.selectbox("Topic", options=all_labels, label_visibility="collapsed")

    st.markdown("#### 📐 Metric")
    st.caption(
        "**Article Count** — how many deduplicated articles were published in a given month. "
        "Higher counts often signal growing media attention to a crisis.  \n"
        "**Sentiment Score** — intensity of the selected tone (scales 0–1). Because it measures intensity regardless of direction, it must be interpreted alongside a specific Tone (Positive or Negative)."
    )
    metric = st.radio("Metric", ["Article Count", "Sentiment Score"], label_visibility="collapsed")

    st.markdown("#### 🎭 Tone")
    if metric == "Sentiment Score":
        tone_opts = ["Positive", "Negative", "Neutral"]
        st.caption("When using Sentiment Score, 'All' is disabled because averaging opposite tones is misleading.")
    else:
        tone_opts = ["All", "Positive", "Negative", "Neutral"]
        st.caption("Filter articles by their overall tone. 'All' includes every article regardless of sentiment.")
    tone = st.selectbox("Tone", options=tone_opts, label_visibility="collapsed")

    st.markdown("---")
    st.markdown("#### 🔬 Threshold Method")
    st.caption("Choose how alert and alarm levels are calculated. Each method has different assumptions.")
    method = st.selectbox(
        "Method",
        options=["categorical", "percentile", "tukey", "zscore"],
        format_func={"percentile": "Percentile", "tukey": "Tukey Fence (IQR)", "zscore": "Z-Score (SD)", "categorical": "Categorical (National Avg)"}.get,
        label_visibility="collapsed"
    )
    with st.expander("ℹ️ What does this method mean?"):
        st.markdown(THRESHOLD_DESCRIPTIONS[method])

    st.markdown("#### ⚙️ Method Parameters")
    if method == "percentile":
        st.caption("Set the percentile cutoffs. 75 means a month is flagged only if it beats 75% of all past months.")
        p1_in = st.slider("Alert percentile (p1)", 50, 99, 75)
        p2_in = st.slider("Alarm percentile (p2)", 51, 100, 90)
        method_params = {"p1": p1_in, "p2": p2_in}

    elif method == "tukey":
        st.caption(
            "k controls how far beyond the typical range a month must fall to trigger. "
            "k=1.5 is the standard statistical threshold; larger k = fewer alarms."
        )
        k_in = st.slider("Fence multiplier (k)", 0.5, 3.0, 1.5, 0.1)
        method_params = {"k": k_in}

    elif method == "zscore":
        st.caption(
            "sd1 and sd2 determine how many standard deviations above average trigger an alert or alarm. "
            "sd1=1 flags the top ~16% of months; sd2=2 flags the top ~2.5%."
        )
        sd1_in = st.slider("Alert SD multiplier", 0.5, 3.0, 1.0, 0.1)
        sd2_in = st.slider("Alarm SD multiplier", 0.5, 4.0, 2.0, 0.1)
        method_params = {"sd1": sd1_in, "sd2": sd2_in}

    else:  # categorical
        st.caption(
            "Uses the national average Alert bound (P1) and Alarm bound (P2) computed "
            "across all regions using the Percentile method (75th / 90th percentile). "
            "The same bar is applied to every region for spatial comparability."
        )
        method_params = {}  # thresholds computed dynamically in classify_panel

    st.markdown("---")
    st.markdown("#### 📅 Minimum History (N)")
    st.caption(
        "Minimum number of months of data required to compute a region's own thresholds. "
        "If a region has fewer months, the national average is scaled to fill in — "
        "those regions are marked with ⚠️."
    )
    N = st.slider("N months", 1, 36, 24)

# ── FILTER TONE ──────────────────────────────────────────────────────────────
df_filtered = df_raw.copy()
if tone != "All":
    df_filtered = df_filtered[df_filtered["sentiment_label"].str.lower() == tone.lower()]

metric_col = "article_count" if metric == "Article Count" else "sentiment_score"


# ── SHARED PANEL BUILDER ──────────────────────────────────────────────────────
def build_panel(df, adm_col):
    """Deduplicate → aggregate → classify thresholds."""
    df = df.drop_duplicates(subset=[adm_col, "yearmon", "Label", "title"])
    panel = df.groupby([adm_col, "yearmon", "Label"]).agg(
        article_count=("url", "count"),
        sentiment_score=("sentiment_score", "mean")
    ).reset_index()
    topic_df = panel[panel["Label"] == selected_topic].copy()
    return topic_df


def classify_panel(topic_df, adm_col):
    """Apply region-level threshold classification with fallback suppression."""
    if topic_df.empty:
        return topic_df
    c_p1, c_p2, c_med = compute_country_stats(topic_df, metric_col, method, method_params)

    # For categorical method: compute per-region P1/P2 then average nationally
    if method == "categorical":
        per_region_thresholds = (
            topic_df.groupby(adm_col)[metric_col]
            .apply(lambda v: compute_thresholds(v, "percentile", {"p1": 75, "p2": 90}))
        )
        cat_p1 = float(per_region_thresholds.apply(lambda t: t[0]).mean())
        cat_p2 = float(per_region_thresholds.apply(lambda t: t[1]).mean())
        cat_params = {"p1": cat_p1, "p2": cat_p2}
    else:
        cat_params = method_params

    result = (
        topic_df
        .groupby(adm_col, group_keys=False)
        .apply(lambda g: classify_region(g, metric_col, method, cat_params, c_p1, c_p2, c_med, N))
        .reset_index(drop=True)
    )
    result["yearmon_date"] = pd.to_datetime(result["yearmon"])
    return result


# ── HEATMAP BUILDER ───────────────────────────────────────────────────────────
def build_heatmap(classified, display_col, label_title, height):
    all_names = sorted(classified[display_col].unique())
    yearmons = sorted(classified["yearmon"].unique())
    grid = pd.MultiIndex.from_product([all_names, yearmons], names=[display_col, "yearmon"]).to_frame(index=False)
    hp = grid.merge(classified[[display_col, "yearmon", "status", metric_col, "p1", "p2"]], on=[display_col, "yearmon"], how="left")
    hp["status"] = hp["status"].fillna("No Data")
    hp[metric_col] = hp[metric_col].fillna(0)

    return alt.Chart(hp).mark_rect().encode(
        x=alt.X("yearmon:O", title="Month"),
        y=alt.Y(f"{display_col}:N", title=label_title, sort=all_names),
        color=alt.Color("status:N", scale=alt.Scale(
            domain=["No Data", "No Concern", "Alert", "Alarm"],
            range=["#D3D3D3", "#4CAF50", "#ff9800", "#f44336"]
        ), legend=alt.Legend(title="Status")),
        tooltip=[
            alt.Tooltip(f"{display_col}:N", title=label_title),
            "yearmon:N",
            alt.Tooltip(f"{metric_col}:Q", title="Metric Value", format=".2f"),
            "status:N",
            alt.Tooltip("p1:Q", title="Alert threshold", format=".2f"),
            alt.Tooltip("p2:Q", title="Alarm threshold", format=".2f"),
        ]
    ).properties(height=height, width="container")


# ── NATIONAL TS BUILDER ───────────────────────────────────────────────────────
def build_nat_ts(classified, topic_name=None):
    STATUS_ORDER = {"Alarm": 0, "Alert": 1, "No Concern": 2, "No Data": 3}
    nat = classified.groupby(["yearmon_date", "status"]).size().reset_index(name="n_regions")
    if nat.empty:
        return None
    nat["status_order"] = nat["status"].map(STATUS_ORDER)
    bars = alt.Chart(nat).mark_bar().encode(
        x=alt.X("yearmon_date:T", title="Month"),
        y=alt.Y("n_regions:Q", title="Regions Affected"),
        color=alt.Color("status:N", scale=alt.Scale(
            domain=["Alarm", "Alert", "No Concern", "No Data"],
            range=["#f44336", "#ff9800", "#4CAF50", "#D3D3D3"]
        )),
        order=alt.Order("status_order:Q", sort="ascending"),
        tooltip=["yearmon_date:T", "status:N", "n_regions:Q"]
    ).properties(height=280)

    # Overlay explicit National reference events
    if topic_name:
        NATIONAL_EVENTS = [
            {"topic": "Conflict and Violence", "date": pd.Timestamp("2022-11-15"), "label": "Factional War & ICV", "period": "Upper Nile + Warrap + Jonglei: CF factional war (Kitgwang-Agwelek) + multi-state ICV"},
            {"topic": "Conflict and Violence", "date": pd.Timestamp("2024-06-15"), "label": "Sustained Elevated Baseline", "period": "Unity + Upper Nile (CF) + Jonglei + Lakes + E. Equatoria (ICV): sustained elevated baseline"},
            {"topic": "Conflict and Violence", "date": pd.Timestamp("2025-02-15"), "label": "Nasir -> Akobo Cascade", "period": "Upper Nile + Jonglei: SSPDF offensive (Nasir -> Akobo cascade)"},
            {"topic": "Conflict and Violence", "date": pd.Timestamp("2025-05-15"), "label": "Massive Multi-Region Collapse", "period": "Upper Nile + Jonglei + W. Equatoria (CF) // Warrap + Lakes + E. Equatoria + Abyei (ICV)"}
        ]
        
        ev_list = [e for e in NATIONAL_EVENTS if e["topic"] == topic_name]
        ev_df = pd.DataFrame(ev_list)
        
        if not ev_df.empty:
            rules = alt.Chart(ev_df).mark_rule(
                strokeDash=[4, 3], strokeWidth=2
            ).encode(
                x="date:T",
                color=alt.Color("label:N", legend=None),
                tooltip=[alt.Tooltip("label:N", title="Event"),
                         alt.Tooltip("period:N", title="Description")]
            )
            labels = alt.Chart(ev_df).mark_text(
                align="left", angle=270, fontSize=9, dy=-5, dx=3
            ).encode(
                x="date:T",
                color=alt.Color("label:N", legend=None),
                text="label:N"
            )
            return alt.layer(bars, rules, labels).resolve_scale(color='independent').properties(height=280)
    return bars


# ── THRESHOLD TABLE ───────────────────────────────────────────────────────────
def threshold_editor(classified, adm_col, level_key):
    total_months = classified["yearmon"].nunique()  # full observed time range
    alarm_counts  = classified[classified["status"] == "Alarm"].groupby(adm_col).size().rename("n_alarm")
    alert_counts  = classified[classified["status"] == "Alert"].groupby(adm_col).size().rename("n_alert")
    obs_counts    = classified.groupby(adm_col).size().rename("n_obs")
    thresh = (
        classified.groupby(adm_col)
        .agg(
            Calc_P1=("p1", "first"),
            Calc_P2=("p2", "first"),
            History=("yearmon", "count"),
            Scaled_Fallback=("fallback", "first")
        )
        .reset_index()
    )
    thresh = thresh.join(alarm_counts, on=adm_col).join(alert_counts, on=adm_col).join(obs_counts, on=adm_col)
    thresh["% Alarm"]   = (thresh["n_alarm"].fillna(0) / thresh["n_obs"] * 100).round(1)
    thresh["% Alert"]   = (thresh["n_alert"].fillna(0) / thresh["n_obs"] * 100).round(1)
    # % No Data = months with zero articles (not in the classified df at all)
    thresh["% No Data"] = ((total_months - thresh["n_obs"]) / total_months * 100).round(1)
    thresh = thresh.drop(columns=["n_alarm", "n_alert", "n_obs"])
    st.caption(
        "Threshold values below were computed automatically using your chosen method and parameters. "
        "You may **override individual rows** by directly editing the P1 / P2 cells in the table. "
        "Regions marked ⚠️ in *Scaled Fallback?* used the national-scaled estimate — "
        "interpret their signals with extra caution."
    )
    edited = st.data_editor(
        thresh,
        column_config={
            adm_col: st.column_config.TextColumn("Region", disabled=True),
            "Calc_P1": st.column_config.NumberColumn("Alert Bound (P1)", format="%.2f"),
            "Calc_P2": st.column_config.NumberColumn("Alarm Bound (P2)", format="%.2f"),
            "History": st.column_config.NumberColumn("Observed Months", disabled=True),
            "Scaled_Fallback": st.column_config.CheckboxColumn("Scaled Fallback ⚠️?", disabled=True),
            "% Alarm": st.column_config.NumberColumn("% Alarm", disabled=True, format="%.1f%%"),
            "% Alert": st.column_config.NumberColumn("% Alert", disabled=True, format="%.1f%%"),
            "% No Data": st.column_config.NumberColumn("% No Data", disabled=True, format="%.1f%%"),
        },
        hide_index=True,
        key=f"editor_{level_key}"
    )
    return edited


def reclassify_with_overrides(classified, edited_thresh, adm_col):
    """Re-apply status using user-overridden thresholds from the editor."""
    rows = []
    for _, override in edited_thresh.iterrows():
        mask = classified[adm_col] == override[adm_col]
        chunk = classified[mask].copy()
        p1 = override["Calc_P1"]
        p2 = override["Calc_P2"]
        chunk["status"] = "No Concern"
        chunk.loc[chunk[metric_col] >= p1, "status"] = "Alert"
        chunk.loc[chunk[metric_col] >= p2, "status"] = "Alarm"
        chunk["p1"] = p1
        chunk["p2"] = p2
        rows.append(chunk)
    return pd.concat(rows) if rows else classified


# ═══════════════════ TABS ════════════════════════════════════════════════════

tab_adm1, tab_adm2 = st.tabs(["🗺️ ADM1 — States", "📍 ADM2 — Counties"])

# ── ADM1 TAB ──────────────────────────────────────────────────────────────────
with tab_adm1:
    if df_filtered.empty:
        st.warning("No data after applying tone filter.")
    else:
        topic_adm1 = build_panel(df_filtered, "adm1_name_final")
        if topic_adm1.empty:
            st.warning(f"No ADM1 data for topic '{selected_topic}' and tone '{tone}'.")
        else:
            classified_adm1 = classify_panel(topic_adm1, "adm1_name_final")

            st.subheader("National Incident Aggregation")
            st.caption("How many states are in Alert or Alarm status each month? Higher bars mean a wider geographic spread of the crisis signal.")
            nat_chart = build_nat_ts(classified_adm1, topic_name=selected_topic)
            if nat_chart:
                st.altair_chart(nat_chart, use_container_width=True)
            else:
                st.info("🟢 No Alert or Alarm signals detected at this setting.")

            st.subheader("State-Level Signal Heatmap")
            st.caption(
                "Each row is a state; each column is a month. "
                "**Green** = observed, normal volume. **Orange** = Alert. **Red** = Alarm. **Gray** = no articles recorded that month."
            )
            hm = build_heatmap(classified_adm1, "display_name", "State", 400)
            st.altair_chart(hm, use_container_width=True)

            st.markdown("---")
            st.subheader("📋 Threshold Review & Adjustments")
            edited_adm1 = threshold_editor(classified_adm1, "adm1_name_final", "adm1")

            # Reclassify with overrides and refresh heatmap
            reclassified_adm1 = reclassify_with_overrides(
                classified_adm1, edited_adm1, "adm1_name_final"
            )
            st.subheader("Updated Heatmap (after threshold adjustments)")
            st.caption("This heatmap reflects any threshold values you edited in the table above.")
            hm2 = build_heatmap(reclassified_adm1, "display_name", "State", 400)
            st.altair_chart(hm2, use_container_width=True)


# ── ADM2 TAB ──────────────────────────────────────────────────────────────────
with tab_adm2:
    if df_filtered.empty:
        st.warning("No data after applying tone filter.")
    else:
        # Deduplicate on adm2 level and retain adm1 for grouping
        df_adm2 = df_filtered.drop_duplicates(subset=["adm2_name_final", "yearmon", "Label", "title"])
        panel_adm2 = df_adm2.groupby(["adm1_name_final", "adm2_name_final", "yearmon", "Label"]).agg(
            article_count=("url", "count"),
            sentiment_score=("sentiment_score", "mean")
        ).reset_index()
        topic_adm2 = panel_adm2[panel_adm2["Label"] == selected_topic].copy()

        if topic_adm2.empty:
            st.warning(f"No ADM2 data for topic '{selected_topic}' and tone '{tone}'.")
        else:
            c_p1, c_p2, c_med = compute_country_stats(topic_adm2, metric_col, method, method_params)

            # Wire categorical national avg thresholds for ADM2 tab
            if method == "categorical":
                per_region_t = (
                    topic_adm2.groupby("adm2_name_final")[metric_col]
                    .apply(lambda v: compute_thresholds(v, "percentile", {"p1": 75, "p2": 90}))
                )
                cat_p1_adm2 = float(per_region_t.apply(lambda t: t[0]).mean())
                cat_p2_adm2 = float(per_region_t.apply(lambda t: t[1]).mean())
                adm2_params = {"p1": cat_p1_adm2, "p2": cat_p2_adm2}
            else:
                adm2_params = method_params

            def classify_adm2(group):
                return classify_region(group, metric_col, method, adm2_params, c_p1, c_p2, c_med, N)

            classified_adm2 = (
                topic_adm2
                .groupby("adm2_name_final", group_keys=False)
                .apply(classify_adm2)
                .reset_index(drop=True)
            )
            classified_adm2["yearmon_date"] = pd.to_datetime(classified_adm2["yearmon"])

            # Build ordered y-axis: sort by adm1 name, then district alphabetically
            adm_lookup = (
                classified_adm2[["adm1_name_final", "adm2_name_final", "display_name"]]
                .drop_duplicates()
                .sort_values(["adm1_name_final", "adm2_name_final"])
            )
            ordered_display = adm_lookup["display_name"].tolist()

            st.subheader("National Incident Aggregation")
            st.caption("How many counties are in Alert or Alarm status each month? Higher bars mean a wider geographic spread of the crisis signal.")
            nat_chart_adm2 = build_nat_ts(classified_adm2, topic_name=selected_topic)
            if nat_chart_adm2:
                st.altair_chart(nat_chart_adm2, use_container_width=True)
            else:
                st.info("🟢 No Alert or Alarm signals detected at this setting.")

            st.subheader("County-Level Signal Heatmap")
            st.caption(
                "Counties are grouped by state (ordered alphabetically) then sorted alphabetically within each state. "
                "⚠️ marks counties without enough history to compute their own thresholds."
            )

            # Build full grid
            yearmons = sorted(classified_adm2["yearmon"].unique())
            grid = pd.MultiIndex.from_product([ordered_display, yearmons], names=["display_name", "yearmon"]).to_frame(index=False)
            hp_adm2 = grid.merge(
                classified_adm2[["display_name", "yearmon", "status", metric_col, "p1", "p2", "adm1_name_final"]],
                on=["display_name", "yearmon"], how="left"
            )
            hp_adm2["status"] = hp_adm2["status"].fillna("No Data")
            hp_adm2[metric_col] = hp_adm2[metric_col].fillna(0)

            hm_adm2 = alt.Chart(hp_adm2).mark_rect().encode(
                x=alt.X("yearmon:O", title="Month"),
                y=alt.Y("display_name:N", title="County (grouped by State)",
                        sort=ordered_display,
                        axis=alt.Axis(labelLimit=300, labelFontSize=10)),
                color=alt.Color("status:N", scale=alt.Scale(
                    domain=["No Data", "No Concern", "Alert", "Alarm"],
                    range=["#D3D3D3", "#4CAF50", "#ff9800", "#f44336"]
                ), legend=alt.Legend(title="Status")),
                tooltip=[
                    alt.Tooltip("display_name:N", title="County"),
                    alt.Tooltip("adm1_name_final:N", title="State"),
                    "yearmon:N",
                    alt.Tooltip(f"{metric_col}:Q", title="Metric Value", format=".2f"),
                    "status:N",
                    alt.Tooltip("p1:Q", title="Alert threshold", format=".2f"),
                    alt.Tooltip("p2:Q", title="Alarm threshold", format=".2f"),
                ]
            ).properties(
                height=max(800, len(ordered_display) * 22),
                width="container"
            )
            st.altair_chart(hm_adm2, use_container_width=True)

            st.markdown("---")
            st.subheader("📋 Threshold Review & Adjustments")
            edited_adm2 = threshold_editor(classified_adm2, "adm2_name_final", "adm2")
