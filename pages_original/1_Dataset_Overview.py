"""
Improved Dataset Overview - Shows article volume by source with distinct colors.
"""

import streamlit as st
import pandas as pd
import altair as alt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils.data_loader import load_data, get_taxonomy_table
from utils.filters import render_date_filter, render_summary_metrics

st.set_page_config(page_title="Dataset Overview - Improved", layout="wide")

st.title("Dataset Overview")
st.markdown("High-level view of article volume, labels, and regional distribution over time.")

# Load data
df = load_data()

# Sidebar filters (only date range, no source filter)
st.sidebar.header("Filters")
date_range = render_date_filter(df, "overview_new")

# Apply date filter only
if date_range:
    filtered_df = df[
        (df["date"] >= pd.to_datetime(date_range[0])) & 
        (df["date"] <= pd.to_datetime(date_range[1]))
    ]
else:
    filtered_df = df.copy()

# Summary metrics
render_summary_metrics(filtered_df)

st.markdown("---")

if filtered_df.empty:
    st.warning("No articles match the current filters.")
else:
    # 1. Total Article Counts Over Time BY SOURCE
    st.subheader("1. Article Volume Over Time by Source")
    st.caption("Each line represents a different news source")
    
    # Group by source and month
    ts_by_source = filtered_df.groupby(["retrieve_source", "yearmon"]).size().reset_index(name="count")
    ts_by_source["yearmon_date"] = pd.to_datetime(ts_by_source["yearmon"])
    
    # Get unique sources and assign colors
    sources = sorted(ts_by_source["retrieve_source"].unique())
    
    # Create color palette - using Tableau10 colors
    color_palette = [
        "#1f77b4",  # blue
        "#ff7f0e",  # orange
        "#2ca02c",  # green
        "#d62728",  # red
        "#9467bd",  # purple
        "#8c564b",  # brown
        "#e377c2",  # pink
        "#7f7f7f",  # gray
        "#bcbd22",  # olive
        "#17becf"   # cyan
    ]
    
    # Multi-line chart with distinct colors per source
    chart_by_source = alt.Chart(ts_by_source).mark_line(point=True, strokeWidth=2.5).encode(
        x=alt.X("yearmon_date:T", title="Month", axis=alt.Axis(format="%Y-%m")),
        y=alt.Y("count:Q", title="Article Count"),
        color=alt.Color(
            "retrieve_source:N", 
            title="Source",
            scale=alt.Scale(domain=sources, range=color_palette[:len(sources)])
        ),
        tooltip=[
            alt.Tooltip("yearmon_date:T", title="Month", format="%Y-%m"),
            alt.Tooltip("retrieve_source:N", title="Source"),
            alt.Tooltip("count:Q", title="Articles", format=",d")
        ]
    ).properties(height=400).interactive()
    
    st.altair_chart(chart_by_source, use_container_width=True)
    
    # Show source statistics
    st.markdown("### Source Statistics")
    source_stats = filtered_df.groupby("retrieve_source").agg({
        "title": "count",
        "date": ["min", "max"]
    }).reset_index()
    source_stats.columns = ["Source", "Total Articles", "First Article", "Last Article"]
    source_stats = source_stats.sort_values("Total Articles", ascending=False)
    
    st.dataframe(source_stats, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # 2. Article Counts by Label -- Separate Subplots
    st.subheader("2. Article Counts by Label Over Time")
    st.caption("Each label shown in its own subplot with a **12-month rolling mean** (orange dashed) and **full-span mean** (red dotted).")
    
    all_labels = sorted([l for l in filtered_df["Label"].dropna().unique() if l != "Uncategorized"])
    
    n_cols = 2
    rows = [all_labels[i:i + n_cols] for i in range(0, len(all_labels), n_cols)]
    
    for row_labels in rows:
        cols = st.columns(len(row_labels))
        for col, label_name in zip(cols, row_labels):
            with col:
                label_ts = filtered_df[filtered_df["Label"] == label_name].copy()
                label_ts = label_ts.groupby("yearmon").size().reset_index(name="count")
                label_ts["yearmon_date"] = pd.to_datetime(label_ts["yearmon"])
                label_ts = label_ts.sort_values("yearmon_date")
                
                if label_ts.empty:
                    st.info(f"No data for '{label_name}'")
                    continue
                
                full_mean = label_ts["count"].mean()
                label_ts["rolling_12m"] = label_ts["count"].rolling(window=12, min_periods=1).mean()
                
                line = alt.Chart(label_ts).mark_line(strokeWidth=2, color="#1f77b4").encode(
                    x=alt.X("yearmon_date:T", title=""),
                    y=alt.Y("count:Q", title="Articles"),
                    tooltip=[
                        alt.Tooltip("yearmon_date:T", title="Month", format="%Y-%m"),
                        alt.Tooltip("count:Q", title="Articles", format=",d")
                    ]
                )
                
                rolling_line = alt.Chart(label_ts).mark_line(
                    strokeDash=[6, 4], strokeWidth=2, color="#ff9800"
                ).encode(
                    x="yearmon_date:T",
                    y=alt.Y("rolling_12m:Q"),
                    tooltip=[
                        alt.Tooltip("yearmon_date:T", title="Month", format="%Y-%m"),
                        alt.Tooltip("rolling_12m:Q", title="12M Rolling Mean", format=".1f")
                    ]
                )
                
                mean_rule = alt.Chart(pd.DataFrame({"y": [full_mean]})).mark_rule(
                    strokeDash=[2, 2], strokeWidth=1.5, color="#f44336"
                ).encode(
                    y="y:Q"
                )
                
                chart = alt.layer(line, rolling_line, mean_rule).properties(
                    height=220,
                    title=label_name
                ).interactive()
                
                st.altair_chart(chart, use_container_width=True)
    
    # Legend
    st.markdown("""
    <div style="display:flex; gap:24px; font-size:0.85em; margin-top:-8px; margin-bottom:12px;">
        <span><span style="display:inline-block;width:16px;height:3px;background:#1f77b4;margin-right:4px;vertical-align:middle;"></span> <b>Monthly Count</b></span>
        <span><span style="display:inline-block;width:16px;height:0;border-top:2px dashed #ff9800;margin-right:4px;vertical-align:middle;"></span> <b>12-Month Rolling Mean</b></span>
        <span><span style="display:inline-block;width:16px;height:0;border-top:2px dotted #f44336;margin-right:4px;vertical-align:middle;"></span> <b>Full-Span Mean</b></span>
    </div>
    """, unsafe_allow_html=True)
    
    # 3. Article Counts by Label x ADM1
    st.subheader("3. Article Counts by Label x ADM1 Region")
    
    cross_adm1 = filtered_df.groupby(["adm1_name_final", "Label"]).size().reset_index(name="count")
    
    top_n_adm1 = st.slider("Top N ADM1 Regions", 5, 20, 10, key="overview_new_topn_adm1")
    top_adm1 = filtered_df["adm1_name_final"].value_counts().head(top_n_adm1).index.tolist()
    cross_adm1 = cross_adm1[cross_adm1["adm1_name_final"].isin(top_adm1)]
    
    chart_heatmap_adm1 = alt.Chart(cross_adm1).mark_rect().encode(
        x=alt.X("Label:N", title="Article Label"),
        y=alt.Y("adm1_name_final:N", title="ADM1 Region", sort=top_adm1),
        color=alt.Color("count:Q", title="Count", scale=alt.Scale(scheme="blues")),
        tooltip=[
            alt.Tooltip("adm1_name_final:N", title="Region"),
            alt.Tooltip("Label:N", title="Label"),
            alt.Tooltip("count:Q", title="Articles", format=",d")
        ]
    ).properties(height=400)
    
    st.altair_chart(chart_heatmap_adm1, use_container_width=True)
    
    # 4. Article Counts by Label x ADM2
    st.subheader("4. Article Counts by Label x ADM2 County")
    
    cross_adm2 = filtered_df[filtered_df["adm2_name_final"] != "Unknown County"].copy()
    cross_adm2 = cross_adm2.groupby(["adm2_name_final", "Label"]).size().reset_index(name="count")
    
    top_n_adm2 = st.slider("Top N ADM2 Counties", 10, 50, 20, key="overview_new_topn_adm2")
    adm2_counts = filtered_df[filtered_df["adm2_name_final"] != "Unknown County"]["adm2_name_final"].value_counts()
    top_adm2 = adm2_counts.head(top_n_adm2).index.tolist()
    cross_adm2 = cross_adm2[cross_adm2["adm2_name_final"].isin(top_adm2)]
    
    chart_heatmap_adm2 = alt.Chart(cross_adm2).mark_rect().encode(
        x=alt.X("Label:N", title="Article Label"),
        y=alt.Y("adm2_name_final:N", title="ADM2 County", sort=top_adm2),
        color=alt.Color("count:Q", title="Count", scale=alt.Scale(scheme="greens")),
        tooltip=[
            alt.Tooltip("adm2_name_final:N", title="County"),
            alt.Tooltip("Label:N", title="Label"),
            alt.Tooltip("count:Q", title="Articles", format=",d")
        ]
    ).properties(height=max(400, top_n_adm2 * 20))
    
    st.altair_chart(chart_heatmap_adm2, use_container_width=True)
    
    # Taxonomy reference
    st.markdown("---")
    with st.expander("How are Article Labels assigned? (Keyword Taxonomy)", expanded=False):
        st.markdown("""
        Article labels are generated by matching **lemmatized unigrams** from article text
        against the keyword taxonomy below. This is a pragmatic screening approach and may
        include false positives or false negatives.
        """)
        st.dataframe(get_taxonomy_table(), use_container_width=True, hide_index=True)
