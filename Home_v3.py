"""
News Analytics Platform - Home Page (V3)
Entry point with dashboard description and data coverage analysis.
"""

import streamlit as st
import pandas as pd
import altair as alt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils.data_loader import load_data

@st.cache_data(show_spinner="Computing coverage statistics...")
def compute_coverage():
    df = load_data()
    df = df[df["retrieve_source"] == "radiotamazuj"].copy()
    df_clean = df.drop_duplicates(subset=["adm2_name_final", "yearmon", "Label", "title"])

    all_yearmons = sorted(df_clean["yearmon"].dropna().unique())
    all_topics   = sorted([t for t in df_clean["Label"].dropna().unique() if t != "Uncategorized"])
    all_adm2     = sorted(df_clean["adm2_name_final"].dropna().unique())
    n_months = len(all_yearmons)

    # Articles per (topic, adm2, yearmon)
    observed = (
        df_clean.groupby(["Label", "adm2_name_final", "yearmon"])
        .size().reset_index(name="article_count")
    )

    # Months covered per (topic, adm2)
    pair_cov = (
        observed.groupby(["Label", "adm2_name_final"])
        .agg(observed_months=("yearmon", "nunique"))
        .reset_index()
    )
    pair_cov["total_months"] = n_months
    pair_cov["coverage_pct"] = (pair_cov["observed_months"] / n_months * 100).round(1)

    # Full grid to detect zero pairs
    full_idx = pd.MultiIndex.from_product([all_topics, all_adm2], names=["Label", "adm2_name_final"])
    pair_full = pd.DataFrame(index=full_idx).reset_index()
    pair_full = pair_full.merge(pair_cov, on=["Label", "adm2_name_final"], how="left")
    pair_full["observed_months"] = pair_full["observed_months"].fillna(0).astype(int)
    pair_full["coverage_pct"]    = pair_full["coverage_pct"].fillna(0.0)

    # ADM2 summary (avg across topics)
    adm2_summary = (
        pair_cov.groupby("adm2_name_final")
        .agg(avg_coverage=("coverage_pct", "mean"),
             min_coverage=("coverage_pct", "min"))
        .reset_index()
        .sort_values("avg_coverage")
    )

    # Topic summary
    topic_summary = (
        pair_cov.groupby("Label")
        .agg(avg_coverage=("coverage_pct", "mean"),
             n_adm2=("adm2_name_final", "nunique"))
        .reset_index()
        .sort_values("avg_coverage")
    )

    zero_count = int((pair_full["observed_months"] == 0).sum())
    total_pairs = len(pair_full)

    # Taxonomy table
    from utils.data_loader import get_taxonomy_table
    taxonomy_df = get_taxonomy_table()

    stats = {
        "total_articles": int(len(df)),
        "date_range": (df["yearmon"].min(), df["yearmon"].max()),
        "n_adm1": int(df["adm1_name_final"].nunique()),
        "n_adm2": int(len(all_adm2)),
        "n_topics": int(len(all_topics)),
        "n_months": int(n_months),
        "zero_count": zero_count,
        "total_pairs": total_pairs,
        "taxonomy": taxonomy_df
    }
    return stats, adm2_summary, topic_summary, pair_full


def home_page():
    # ── CUSTOM CSS FOR READABILITY ───────────────────────────────────────────
    st.markdown("""
        <style>
            /* Increase body font size for better readability */
            .main .block-container p, 
            .main .block-container li, 
            .main .block-container table {
                font-size: 1.15rem !important;
                line-height: 1.6 !important;
            }
            .main .block-container h1 {
                font-size: 2.5rem !important;
            }
            .main .block-container h2 {
                font-size: 2rem !important;
                margin-top: 2rem !important;
            }
            .main .block-container h3 {
                font-size: 1.5rem !important;
                margin-top: 1.5rem !important;
            }
        </style>
    """, unsafe_allow_html=True)

    st.title("South Sudan News Analytics Platform (V3)")

    st.markdown("""
Welcome to the **South Sudan News Analytics Platform (V3)**—a specialized decision-support tool designed for humanitarian and food security analysts. This platform provides real-time monitoring and historical analysis of news trends across South Sudan, utilizing data synthesized from [Radio Tamazuj](https://www.radiotamazuj.org/en/about-us).

---

### Analytical Capabilities

| Component | Analytical Objective |
|:---|:---|
| **National Overview** | Systematic monitoring of geographic risk distributions via comparative heatmaps. |
| **ADM1 Insights** | Longitudinal analysis of state-level article trends utilizing a multi-method consensus engine. |
| **ADM2 Insights** | Granular county-level monitoring to identify localized anomalies and reporting spikes. |
| **Validation Reference** | Evidence-based validation layer mapping historical IPC ground-truth events. |
| **RAG+LLM Summary** | Automated intelligence synthesis generating cited situation reports from source documentation. |

---

### Crisis Signaling and Threshold Methodology

The platform identifies anomalies by evaluating current article volume against multi-year historical baselines. Analysts can calibrate signals using three distinct statistical distributions:

| Methodology | Alert Threshold | Alarm Threshold |
|:---|:---|:---|
| **Percentile Rank** | Top 25% of historical observations (p75). | Top 10% of historical observations (p90). |
| **Tukey Outlier** | Values exceeding the Interquartile Range (IQR) per 1.5x multiplier. | Values exceeding the IQR per 3x multiplier. |
| **Z-Score (SD)** | Deviations exceeding 1 Standard Deviation from the mean. | Deviations exceeding 2 Standard Deviations from the mean. |

**Note**: Geographic regions with insufficient historical data (fewer than *N* months) are automatically evaluated using nationally-scaled proxies to maintain monitoring continuity.

---

### Keyword Taxonomy

Classification is performed using a keyword-based taxonomy derived from established food security research. This table serves as the reference for thematic labeling:
""")

    stats, adm2_df, topic_df, pair_full = compute_coverage()
    
    st.table(stats["taxonomy"])

    st.markdown("---")
    st.caption("*Independent analytical tool developed for strategic monitoring and early warning.*")


    # ── DATA COVERAGE SECTION ─────────────────────────────────────────────────
    st.markdown("---")
    st.header("Data Coverage and Limitations")
    st.markdown(
        "All signal analysis depends exclusively on **Radio Tamazuj** articles. "
        "Coverage is uneven across counties and topics — understanding these gaps is essential "
        "for correctly interpreting threshold alerts and silences."
    )

    stats, adm2_df, topic_df, pair_full = compute_coverage()

    # ── KPI ROW ───────────────────────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Articles", f"{stats['total_articles']:,}")
    c2.metric("Date Range", f"{stats['date_range'][0]} – {stats['date_range'][1]}")
    c3.metric("ADM2 Counties", stats["n_adm2"])
    c4.metric("Topics", stats["n_topics"])
    c5.metric("Zero-Coverage Pairs", f"{stats['zero_count']} / {stats['total_pairs']}")

    st.markdown("---")

    # ── CHART 1: Topic coverage bar ───────────────────────────────────────────
    st.subheader("Average Monthly Coverage by Topic (% of months with at least 1 article)")
    st.caption(
        "Topics shown in green meet the 30% adequacy threshold — at least 30% of months have at least one article. "
        "Topics shown in red are structurally under-reported and their anomaly signals should be treated with additional caution."
    )

    topic_bar = alt.Chart(topic_df).mark_bar().encode(
        x=alt.X("avg_coverage:Q", title="Average Coverage (% of months)", scale=alt.Scale(domain=[0, 100])),
        y=alt.Y("Label:N", sort=alt.SortField("avg_coverage", order="ascending"), title=None),
        color=alt.condition(
            alt.datum.avg_coverage >= 30,
            alt.value("#2e7d32"),   # green: adequately covered
            alt.value("#c62828")    # red: under-reported
        ),
        tooltip=[
            alt.Tooltip("Label:N", title="Topic"),
            alt.Tooltip("avg_coverage:Q", title="Avg Coverage %", format=".1f"),
            alt.Tooltip("n_adm2:Q", title="Counties with Any Data"),
        ]
    ).properties(height=320)

    # Reference line at 30% (adequate coverage threshold)
    ref_line = alt.Chart(pd.DataFrame({"x": [30]})).mark_rule(
        strokeDash=[6, 4], color="#555", strokeWidth=1.5
    ).encode(x="x:Q")

    ref_label = alt.Chart(pd.DataFrame({"x": [31], "y": ["Other"], "text": ["30% adequacy threshold"]})).mark_text(
        align="left", color="#555", fontSize=11
    ).encode(x="x:Q", y=alt.Y("y:N"), text="text:N")

    st.altair_chart(alt.layer(topic_bar, ref_line, ref_label).properties(height=320), use_container_width=True)

    st.markdown("---")

    # ── CHART 2: ADM2 avg coverage bar (bottom 20) ────────────────────────────
    st.subheader("Worst-Covered Counties — Average Coverage Across All Topics")
    st.caption(
        "Counties shown here average below 15% monthly coverage. "
        "Anomaly detection for these areas relies heavily on national fallback thresholds "
        "and may miss genuine crises due to a lack of reporting, not a lack of events."
    )

    bottom20 = adm2_df.head(20).copy()

    adm2_bar = alt.Chart(bottom20).mark_bar(color="#b71c1c").encode(
        x=alt.X("avg_coverage:Q", title="Avg Coverage % (across all topics)", scale=alt.Scale(domain=[0, 35])),
        y=alt.Y("adm2_name_final:N", sort=alt.SortField("avg_coverage", order="ascending"), title=None),
        color=alt.condition(
            alt.datum.avg_coverage < 10,
            alt.value("#b71c1c"),
            alt.value("#e57373")
        ),
        tooltip=[
            alt.Tooltip("adm2_name_final:N", title="County"),
            alt.Tooltip("avg_coverage:Q", title="Avg Coverage %", format=".1f"),
            alt.Tooltip("min_coverage:Q", title="Minimum Coverage %", format=".1f"),
        ]
    ).properties(height=400)

    st.altair_chart(adm2_bar, use_container_width=True)

    st.markdown("---")

    # ── CHART 3: Topic x ADM2 coverage heatmap (filtered to worst counties) ──
    st.subheader("Coverage Heatmap — Topic x County (Bottom 25 Counties)")
    st.caption(
        "Each cell shows the percentage of months that have at least one article for that topic/county pair. "
        "Gray (0%) means the platform has no data for that combination at all."
    )

    worst25_adm2 = adm2_df.head(25)["adm2_name_final"].tolist()
    hm_data = pair_full[pair_full["adm2_name_final"].isin(worst25_adm2)].copy()
    hm_data = hm_data[hm_data["Label"] != "Uncategorized"]

    heatmap = alt.Chart(hm_data).mark_rect(stroke="white", strokeWidth=0.5).encode(
        x=alt.X("Label:N", title="Topic", axis=alt.Axis(labelAngle=-40, labelOverlap=False)),
        y=alt.Y("adm2_name_final:N",
                sort=alt.SortField("adm2_name_final"),
                title=None,
                axis=alt.Axis(labelFontSize=11)),
        color=alt.Color("coverage_pct:Q",
                        title="Coverage %",
                        scale=alt.Scale(scheme="blues", domain=[0, 100])),
        tooltip=[
            alt.Tooltip("adm2_name_final:N", title="County"),
            alt.Tooltip("Label:N", title="Topic"),
            alt.Tooltip("coverage_pct:Q", title="Coverage %", format=".1f"),
            alt.Tooltip("observed_months:Q", title="Observed Months"),
        ]
    ).properties(height=550)

    st.altair_chart(heatmap, use_container_width=True)

    st.markdown("---")

    # ── LIMITATION SUMMARY ────────────────────────────────────────────────────
    st.subheader("Key Limitations")
    st.markdown("""
**1. Single-source bias** — All data comes from [Radio Tamazuj](https://www.radiotamazuj.org/en/about-us). Remote counties in Greater Equatoria, Abyei/Warrap border areas, and Upper Nile are systematically under-reported.

**2. Georeferencing uncertainty** — Geographic attribution is performed using a Named Entity Recognition (NER) algorithm that links place names in article text to administrative units. This process is inherently imperfect: false positives occur when a place is mentioned in context rather than as the event location, and false negatives occur when relevant localities are unnamed or referred to by informal names. County-level signals in particular should be treated as approximations subject to systematic NER error.

**3. Temporal gaps** — Even well-covered regions have gap months. The platform treats a missing month as "no data" (shown in gray in heatmaps), not as "Normal."

**4. Topic sparsity** — Topics below the 30% adequacy threshold (shown in red above) have insufficient temporal coverage for robust statistical inference in most counties. Treat their signals with heightened caution.

**5. Minimum history warning** — The platform flags any county with fewer than *N* months of history as using nationally-scaled fallback thresholds. The counties listed above are most likely to trigger this warning.

**6. Zero-coverage pairs** — """ + f"**{stats['zero_count']}** topic/county combinations have zero articles across the entire period. These are invisible to the threshold engine." + """

**Recommended caution counties**: Canal/Pigi, Ibba, Longochuk, Fashoda, Nagero, Baliet, Panyikang, Ezo, Pochalla, Budi, Kapoeta North, Gogrial East.
""")



home       = st.Page(home_page, title="Home", icon="🏠", default=True)
national   = st.Page("pages_v3/4_National_Overview.py", title="National Overview",   icon="🌍")
adm1       = st.Page("pages_v3/2_ADM1_Insights.py",     title="ADM1 Insights",       icon="🗺️")
adm2       = st.Page("pages_v3/3_ADM2_Insights.py",     title="ADM2 Insights",       icon="📍")
validation = st.Page("pages_v3/5_Validation_Reference.py", title="Validation Reference", icon="✅")
rag        = st.Page("pages_original/5_RAG_LLM_Summary.py",   title="RAG+LLM Summary",     icon="🤖")

st.set_page_config(
    page_title="News Analytics Platform (V3)",
    page_icon="📰",
    layout="wide"
)

pg = st.navigation({
    "Dashboard":  [home, national, adm1, adm2, validation, rag],
})

pg.run()
