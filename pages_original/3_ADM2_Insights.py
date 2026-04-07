"""
Improved ADM2 Insights - Shows one county and one topic by default with filters.
"""

import streamlit as st
import pandas as pd
import altair as alt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils.data_loader import load_data
from utils.filters import (
    render_source_filter, render_date_filter, render_sentiment_filter,
    apply_filters, render_summary_metrics
)

st.set_page_config(page_title="ADM2 Insights - Improved", layout="wide")

st.title("ADM2 Insights (County Level)")
st.markdown("Interactive line graphs showing article volume trends with **static** and **dynamic** thresholds for alert/alarm detection at the county level.")

# Load data
df = load_data()

# Sidebar filters
st.sidebar.header("Filters")
sources = render_source_filter(df, "adm2_new", default=["radiotamazuj"])
sentiments = render_sentiment_filter(df, "adm2_new", default=["Negative"])

# Apply filters (no date range)
filtered_df = apply_filters(
    df, sources=sources, sentiments=sentiments
)

# Summary metrics
render_summary_metrics(filtered_df)

st.markdown("---")

if filtered_df.empty:
    st.warning("No articles match the current filters.")
else:
    # Get available regions and labels
    all_regions = sorted(filtered_df["adm1_name_final"].unique())
    all_labels = sorted([l for l in filtered_df["Label"].dropna().unique() if l != "Uncategorized"])
    
    # Region, County, and Topic selectors
    col1, col2, col3 = st.columns(3)
    
    with col1:
        selected_region = st.selectbox(
            "🗺️ Select State (ADM1)",
            options=all_regions,
            index=0,
            key="region_select_adm2"
        )
    
    # Filter counties by selected region
    region_df = filtered_df[filtered_df["adm1_name_final"] == selected_region]
    available_counties = sorted(region_df[region_df["adm2_name_final"] != "Unknown County"]["adm2_name_final"].unique())
    
    if not available_counties:
        st.warning(f"No county data available for **{selected_region}** with current filters.")
    else:
        with col2:
            selected_county = st.selectbox(
                "📍 Select County (ADM2)",
                options=available_counties,
                index=0,
                key="county_select"
            )
        
        with col3:
            selected_label = st.selectbox(
                "📋 Select Topic",
                options=all_labels,
                index=0,
                key="label_select_adm2"
            )
        
        st.markdown("---")
        
        # Alert legend
        st.markdown("""
        <div style="display:flex; gap:24px; font-size:0.9em; padding:12px; background:#f0f2f6; border-radius:8px; margin-bottom:20px;">
            <span><span style="display:inline-block;width:12px;height:12px;background:#808080;border-radius:50%;margin-right:6px;vertical-align:middle;"></span> <b>Normal</b>: Within 1 SD</span>
            <span><span style="display:inline-block;width:12px;height:12px;background:#ff9800;border-radius:50%;margin-right:6px;vertical-align:middle;"></span> <b>Alert-high</b>: 1-2 SD above mean</span>
            <span><span style="display:inline-block;width:12px;height:12px;background:#f44336;border-radius:50%;margin-right:6px;vertical-align:middle;"></span> <b>Alarm-high</b>: >2 SD above mean</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Filter data for selected region, county, and label
        county_label_df = region_df[
            (region_df["adm2_name_final"] == selected_county) & 
            (region_df["Label"] == selected_label)
        ]
        
        if county_label_df.empty:
            st.warning(f"No articles found for **{selected_region} > {selected_county}** with label **{selected_label}**. Try different filters.")
        else:
            st.subheader(f"📊 {selected_region} > {selected_county} - {selected_label}")
            
            # Prepare time series data
            ts_data = county_label_df.groupby("yearmon").size().reset_index(name="article_count")
            ts_data["yearmon_date"] = pd.to_datetime(ts_data["yearmon"])
            ts_data = ts_data.sort_values("yearmon_date")
            
            # Create tabs for static and dynamic thresholds
            tab1, tab2 = st.tabs(["📈 Static Thresholds (Full-Span)", "📊 Dynamic Thresholds (12-Month Rolling)"])
            
            with tab1:
                st.caption("Thresholds calculated from the entire time period")
                
                # Calculate static thresholds
                mean_val = ts_data["article_count"].mean()
                std_val = ts_data["article_count"].std()
                
                threshold_1sd = mean_val + std_val
                threshold_2sd = mean_val + 2 * std_val
                
                # Add threshold data
                ts_static = ts_data.copy()
                ts_static["mean"] = mean_val
                ts_static["threshold_1sd"] = threshold_1sd
                ts_static["threshold_2sd"] = threshold_2sd
                
                # Add alert status
                ts_static["status"] = "Normal"
                ts_static.loc[ts_static["article_count"] > threshold_1sd, "status"] = "Alert-high"
                ts_static.loc[ts_static["article_count"] > threshold_2sd, "status"] = "Alarm-high"
                
                # Article count line
                line = alt.Chart(ts_static).mark_line(
                    point=True, strokeWidth=3, color="#1f77b4"
                ).encode(
                    x=alt.X("yearmon_date:T", title="Month", axis=alt.Axis(format="%Y-%m")),
                    y=alt.Y("article_count:Q", title="Article Count"),
                    tooltip=[
                        alt.Tooltip("yearmon_date:T", title="Month", format="%Y-%m"),
                        alt.Tooltip("article_count:Q", title="Articles"),
                        alt.Tooltip("status:N", title="Status")
                    ]
                )
                
                # Mean line
                mean_line = alt.Chart(ts_static).mark_rule(
                    strokeDash=[2, 2], strokeWidth=2, color="#666"
                ).encode(
                    y="mean:Q"
                )
                
                # Alert threshold (1 SD)
                alert_line = alt.Chart(ts_static).mark_rule(
                    strokeDash=[4, 4], strokeWidth=2.5, color="#ff9800"
                ).encode(
                    y="threshold_1sd:Q"
                )
                
                # Alarm threshold (2 SD)
                alarm_line = alt.Chart(ts_static).mark_rule(
                    strokeDash=[4, 4], strokeWidth=2.5, color="#f44336"
                ).encode(
                    y="threshold_2sd:Q"
                )
                
                # Color points by status
                points = alt.Chart(ts_static).mark_circle(size=150).encode(
                    x="yearmon_date:T",
                    y="article_count:Q",
                    color=alt.Color("status:N", 
                        scale=alt.Scale(
                            domain=["Normal", "Alert-high", "Alarm-high"],
                            range=["#808080", "#ff9800", "#f44336"]
                        ),
                        legend=None
                    ),
                    tooltip=[
                        alt.Tooltip("yearmon_date:T", title="Month", format="%Y-%m"),
                        alt.Tooltip("article_count:Q", title="Articles"),
                        alt.Tooltip("status:N", title="Status"),
                        alt.Tooltip("mean:Q", title="Mean", format=".1f"),
                        alt.Tooltip("threshold_1sd:Q", title="Alert Threshold", format=".1f"),
                        alt.Tooltip("threshold_2sd:Q", title="Alarm Threshold", format=".1f")
                    ]
                )
                
                chart = alt.layer(mean_line, alert_line, alarm_line, line, points).properties(
                    height=400,
                    title=f"Article Volume Trend - Static Thresholds"
                ).interactive()
                
                st.altair_chart(chart, use_container_width=True)
                
                # Show current status with descriptions
                latest = ts_static.iloc[-1]
                status_color = {"Normal": "🟢", "Alert-high": "🟠", "Alarm-high": "🔴"}
                
                st.markdown(f"### Current Status: {latest['yearmon']}")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Status", f"{status_color.get(latest['status'], '⚪')} {latest['status']}")
                    st.caption("Current alert level based on thresholds")
                with col2:
                    st.metric("Latest Count", f"{latest['article_count']:.0f}")
                    st.caption(f"Articles in {latest['yearmon']}")
                with col3:
                    st.metric("Mean", f"{mean_val:.1f}")
                    st.caption("Average over entire period")
                with col4:
                    st.metric("Alert / Alarm", f"{threshold_1sd:.1f} / {threshold_2sd:.1f}")
                    st.caption("Thresholds: Mean+1SD / Mean+2SD")
            
            with tab2:
                st.caption("Thresholds calculated using 12-month rolling window")
                
                # Calculate dynamic thresholds
                ts_dynamic = ts_data.copy()
                ts_dynamic["rolling_mean"] = ts_dynamic["article_count"].rolling(window=12, min_periods=1).mean()
                ts_dynamic["rolling_std"] = ts_dynamic["article_count"].rolling(window=12, min_periods=1).std()
                
                ts_dynamic["threshold_1sd"] = ts_dynamic["rolling_mean"] + ts_dynamic["rolling_std"]
                ts_dynamic["threshold_2sd"] = ts_dynamic["rolling_mean"] + 2 * ts_dynamic["rolling_std"]
                
                # Add alert status
                ts_dynamic["status"] = "Normal"
                ts_dynamic.loc[ts_dynamic["article_count"] > ts_dynamic["threshold_1sd"], "status"] = "Alert-high"
                ts_dynamic.loc[ts_dynamic["article_count"] > ts_dynamic["threshold_2sd"], "status"] = "Alarm-high"
                
                # Article count line
                line = alt.Chart(ts_dynamic).mark_line(
                    point=True, strokeWidth=3, color="#1f77b4"
                ).encode(
                    x=alt.X("yearmon_date:T", title="Month", axis=alt.Axis(format="%Y-%m")),
                    y=alt.Y("article_count:Q", title="Article Count"),
                    tooltip=[
                        alt.Tooltip("yearmon_date:T", title="Month", format="%Y-%m"),
                        alt.Tooltip("article_count:Q", title="Articles"),
                        alt.Tooltip("status:N", title="Status")
                    ]
                )
                
                # Rolling mean line
                mean_line = alt.Chart(ts_dynamic).mark_line(
                    strokeDash=[2, 2], strokeWidth=2, color="#666"
                ).encode(
                    x="yearmon_date:T",
                    y="rolling_mean:Q"
                )
                
                # Alert threshold (1 SD)
                alert_line = alt.Chart(ts_dynamic).mark_line(
                    strokeDash=[4, 4], strokeWidth=2.5, color="#ff9800"
                ).encode(
                    x="yearmon_date:T",
                    y="threshold_1sd:Q"
                )
                
                # Alarm threshold (2 SD)
                alarm_line = alt.Chart(ts_dynamic).mark_line(
                    strokeDash=[4, 4], strokeWidth=2.5, color="#f44336"
                ).encode(
                    x="yearmon_date:T",
                    y="threshold_2sd:Q"
                )
                
                # Color points by status
                points = alt.Chart(ts_dynamic).mark_circle(size=150).encode(
                    x="yearmon_date:T",
                    y="article_count:Q",
                    color=alt.Color("status:N", 
                        scale=alt.Scale(
                            domain=["Normal", "Alert-high", "Alarm-high"],
                            range=["#808080", "#ff9800", "#f44336"]
                        ),
                        legend=None
                    ),
                    tooltip=[
                        alt.Tooltip("yearmon_date:T", title="Month", format="%Y-%m"),
                        alt.Tooltip("article_count:Q", title="Articles"),
                        alt.Tooltip("status:N", title="Status"),
                        alt.Tooltip("rolling_mean:Q", title="12M Mean", format=".1f"),
                        alt.Tooltip("threshold_1sd:Q", title="Alert Threshold", format=".1f"),
                        alt.Tooltip("threshold_2sd:Q", title="Alarm Threshold", format=".1f")
                    ]
                )
                
                chart = alt.layer(mean_line, alert_line, alarm_line, line, points).properties(
                    height=400,
                    title=f"Article Volume Trend - Dynamic Thresholds (12-Month Rolling)"
                ).interactive()
                
                st.altair_chart(chart, use_container_width=True)
                
                # Show current status with descriptions
                latest = ts_dynamic.iloc[-1]
                status_color = {"Normal": "🟢", "Alert-high": "🟠", "Alarm-high": "🔴"}
                
                st.markdown(f"### Current Status: {latest['yearmon']}")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Status", f"{status_color.get(latest['status'], '⚪')} {latest['status']}")
                    st.caption("Current alert level based on thresholds")
                with col2:
                    st.metric("Latest Count", f"{latest['article_count']:.0f}")
                    st.caption(f"Articles in {latest['yearmon']}")
                with col3:
                    st.metric("12M Mean", f"{latest['rolling_mean']:.1f}")
                    st.caption("12-month rolling average")
                with col4:
                    st.metric("Alert / Alarm", f"{latest['threshold_1sd']:.1f} / {latest['threshold_2sd']:.1f}")
                    st.caption("Thresholds: 12M Mean+1SD / +2SD")
