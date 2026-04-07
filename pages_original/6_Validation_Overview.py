"""
Page 6: Validation Overview
High-level summary of alert/alarm signal frequency for threshold validation.

Pipeline per render:
  1. Deduplicate by [geo_col, yearmon, retrieve_source, title]
  2. Aggregate article counts
  3. Build full panel: top-N regions × every month in date range
  4. Apply min-articles threshold (suppress noise from georef/label errors)
  5. Apply missing-month fill choice (0 or NaN/black)
  6. Compute static + dynamic SD flags

Three display sections:
  1. Signal Frequency Table  — alert/alarm counts per unit + national
  2. National Warning Timeline — stacked bar: units per status per month
  3. Unit-Level Warning History — region × month heatmap
"""

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_loader import load_data
from utils.filters import (
    render_source_filter, render_date_filter, render_sentiment_filter,
    apply_filters, render_summary_metrics
)
from utils.alert_helpers import (
    add_sd_flags_static, add_sd_flags_dynamic,
    get_status_color_scale, render_alert_legend
)

st.set_page_config(page_title="Validation Overview", layout="wide")

st.title("Validation Overview")
st.markdown(
    "Signal frequency and warning history for threshold validation. "
    "**Static** (full-span mean/SD) is the primary method; "
    "**Dynamic** (12-month rolling) is shown as a supplement. "
    "Articles are **deduplicated** before counting to prevent double-counting "
    "from multi-region tagging or scraper reruns."
)

# ── Load data ─────────────────────────────────────────────────────────────────
df = load_data()

# ── Sidebar: Filters ──────────────────────────────────────────────────────────
st.sidebar.header("Filters")
sources    = render_source_filter(df,    "p6", default=["radiotamazuj"])
sentiments = render_sentiment_filter(df, "p6", default=["Negative"])
date_range = render_date_filter(df, "p6")

st.sidebar.markdown("---")
all_labels = sorted([l for l in df["Label"].dropna().unique() if l != "Uncategorized"])
selected_labels = st.sidebar.multiselect(
    "Article Labels", options=all_labels, default=all_labels, key="p6_labels"
)

# ── Sidebar: Panel Options ────────────────────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.subheader("Panel Options")

geo_level = st.sidebar.radio(
    "Geographic level",
    ["ADM1 (State)", "ADM2 (County)"],
    key="p6_geo"
)
geo_col     = "adm1_name_final" if geo_level.startswith("ADM1") else "adm2_name_final"
level_label = "State" if geo_col == "adm1_name_final" else "County"

top_n = st.sidebar.slider("Top N regions to display", 5, 100, 15, key="p6_topn")

fill_missing = st.sidebar.radio(
    "Missing months (no articles found)",
    ["Fill as 0", "Leave as no data"],
    key="p6_fill",
    help=(
        "Fill as 0: missing region-months are treated as zero activity and "
        "included in the SD baseline (pulls mean down, widens SD). "
        "Leave as no data: excluded from SD — shown as black in heatmap."
    )
)

min_articles = st.sidebar.slider(
    "Min. articles/month threshold",
    min_value=0, max_value=20, value=1,
    key="p6_min",
    help="Periods with fewer articles than this may reflect georeferencing or labeling noise."
)
if min_articles > 0:
    below_treatment = st.sidebar.radio(
        "Periods below min. threshold",
        ["Set to no data", "Set to 0", "Keep as-is"],
        key="p6_below",
        help=(
            "Set to no data: excluded from SD baseline and shown as black. "
            "Set to 0: treated as inactive (Normal). "
            "Keep as-is: real count used — may generate anomalies for sparse regions."
        )
    )
else:
    below_treatment = "Keep as-is"

# ── Apply base filters ────────────────────────────────────────────────────────
filtered_df = apply_filters(df, sources=sources, date_range=date_range, sentiments=sentiments)
if selected_labels:
    filtered_df = filtered_df[filtered_df["Label"].isin(selected_labels)]
if geo_col == "adm2_name_final":
    filtered_df = filtered_df[filtered_df["adm2_name_final"] != "Unknown County"]

if filtered_df.empty:
    st.warning("No articles match the current filters.")
    st.stop()

# ── Step 1: Deduplicate ───────────────────────────────────────────────────────
# Remove same article appearing multiple times for same region-month-source
dedup_cols = [c for c in [geo_col, "yearmon", "retrieve_source", "title"]
              if c in filtered_df.columns]
deduped_df = filtered_df.drop_duplicates(subset=dedup_cols)
n_removed  = len(filtered_df) - len(deduped_df)

render_summary_metrics(deduped_df)
if n_removed > 0:
    st.caption(
        f"Removed **{n_removed:,}** duplicate article–region–month entries before counting "
        f"(dedup key: {', '.join(dedup_cols)})."
    )
st.markdown("---")
render_alert_legend()

# ── Steps 2–5: Build panelised time series ────────────────────────────────────

# All months spanning the selected date range
start_dt   = pd.Timestamp(date_range[0])
end_dt     = pd.Timestamp(date_range[1])
all_months = [str(p) for p in pd.period_range(start=start_dt, end=end_dt, freq="M")]

# Top-N regions by deduplicated article count
top_units = deduped_df[geo_col].value_counts().head(top_n).index.tolist()


def build_panel(deduped, group_col, units, months, fill_missing, min_articles, below_treatment):
    """
    Aggregate counts, create full Cartesian panel, apply threshold and fill rules.

    Fill logic:
      - Originally-missing cells (no articles at all) are controlled by fill_missing.
      - Below-threshold cells are controlled by below_treatment independently.
        'Set to no data' cells are NOT filled to 0 even when fill_missing='Fill as 0'.
    """
    # Raw counts (post-dedup)
    ts_raw = (
        deduped.groupby([group_col, "yearmon"])
        .size().reset_index(name="article_count")
    )
    ts_raw_top = ts_raw[ts_raw[group_col].isin(units)]

    # Full Cartesian panel
    panel = pd.DataFrame(
        [(r, m) for r in units for m in months],
        columns=[group_col, "yearmon"]
    )
    ts = panel.merge(ts_raw_top, on=[group_col, "yearmon"], how="left")
    ts["yearmon_date"] = pd.to_datetime(ts["yearmon"])

    # Track which cells were originally missing (vs present but low)
    originally_missing = ts["article_count"].isna().copy()

    # Apply min-articles threshold to present (non-missing) cells
    if min_articles > 1:
        below = (~originally_missing) & (ts["article_count"] < min_articles)
        if below_treatment == "Set to no data":
            ts.loc[below, "article_count"] = np.nan   # excluded from SD; shown black
        elif below_treatment == "Set to 0":
            ts.loc[below, "article_count"] = 0.0      # treated as inactive
        # "Keep as-is": real count retained

    # Apply fill choice only to originally-missing cells
    # (below-threshold cells that were set to NaN are intentionally kept as NaN)
    if fill_missing == "Fill as 0":
        ts.loc[originally_missing, "article_count"] = 0.0

    return ts


def build_national_panel(deduped, months, fill_missing, min_articles, below_treatment):
    """National-level panel (same rules as unit panel)."""
    ts_raw = deduped.groupby("yearmon").size().reset_index(name="article_count")
    panel  = pd.DataFrame({"yearmon": months, "level": "National"})
    ts     = panel.merge(ts_raw, on="yearmon", how="left")
    ts["yearmon_date"] = pd.to_datetime(ts["yearmon"])
    originally_missing = ts["article_count"].isna().copy()
    if min_articles > 1:
        below = (~originally_missing) & (ts["article_count"] < min_articles)
        if below_treatment == "Set to no data":
            ts.loc[below, "article_count"] = np.nan
        elif below_treatment == "Set to 0":
            ts.loc[below, "article_count"] = 0.0
    if fill_missing == "Fill as 0":
        ts.loc[originally_missing, "article_count"] = 0.0
    return ts


ts_panel = build_panel(
    deduped_df, geo_col, top_units, all_months,
    fill_missing, min_articles, below_treatment
)
ts_nat = build_national_panel(
    deduped_df, all_months, fill_missing, min_articles, below_treatment
)

# ── Step 6: SD flags ──────────────────────────────────────────────────────────
flagged_s     = add_sd_flags_static( ts_panel, geo_col,  "article_count")
flagged_d     = add_sd_flags_dynamic(ts_panel, geo_col,  "article_count")
flagged_nat_s = add_sd_flags_static( ts_nat,   "level",  "article_count")
flagged_nat_d = add_sd_flags_dynamic(ts_nat,   "level",  "article_count")

# ── Helper: frequency summary table ──────────────────────────────────────────

def build_frequency_table(flagged_df, group_col):
    """
    Count months per status per group.
    Alert%/Alarm% are out of months with actual data (No data excluded).
    """
    counts = (
        flagged_df.groupby([group_col, "status"])
        .size()
        .unstack(fill_value=0)
        .reindex(columns=["Normal", "Alert-high", "Alarm-high", "No data"], fill_value=0)
    )
    counts["Data Months"]  = counts["Normal"] + counts["Alert-high"] + counts["Alarm-high"]
    counts["Total Months"] = counts["Data Months"] + counts["No data"]
    denom = counts["Data Months"].replace(0, np.nan)
    counts["Alert %"] = (counts["Alert-high"] / denom * 100).round(1)
    counts["Alarm %"] = (counts["Alarm-high"] / denom * 100).round(1)
    return counts.sort_values("Alarm-high", ascending=False)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — Signal Frequency Table
# ══════════════════════════════════════════════════════════════════════════════
st.subheader("1. Signal Frequency")
st.caption(
    f"Months at each status per {level_label} (full panel: {len(all_months)} months × {len(top_units)} regions). "
    "Alert% and Alarm% are computed over months with data only."
)

tab_unit, tab_nat = st.tabs([geo_level, "National"])

with tab_unit:
    col_s, col_d = st.columns(2)
    with col_s:
        st.caption("**Static** (Full-Span Mean/SD)")
        st.dataframe(build_frequency_table(flagged_s, geo_col), use_container_width=True)
    with col_d:
        st.caption("**Dynamic** (12-Month Rolling Mean/SD)")
        st.dataframe(build_frequency_table(flagged_d, geo_col), use_container_width=True)

with tab_nat:
    col_s, col_d = st.columns(2)
    with col_s:
        st.caption("**Static** (Full-Span Mean/SD)")
        st.dataframe(build_frequency_table(flagged_nat_s, "level"), use_container_width=True)
    with col_d:
        st.caption("**Dynamic** (12-Month Rolling Mean/SD)")
        st.dataframe(build_frequency_table(flagged_nat_d, "level"), use_container_width=True)

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — National Warning Timeline (Stacked Bar)
# ══════════════════════════════════════════════════════════════════════════════
st.subheader("2. National Warning Timeline")
st.caption(
    f"Each bar = count of {level_label.lower()}s at each status in that month "
    f"(No data units excluded). Taller orange/red stacks indicate widespread alerting."
)

st.info(
    "Dynamic method: the first 12 months of each region's history have insufficient "
    "trailing data (< 3 observed months) and are marked Normal regardless of count. "
    "This is why alerts appear only after the warmup period."
)

# Numeric sort key: Alarm-high=0 (bottom), Alert-high=1, Normal=2 (top)
STACK_ORDER = {"Alarm-high": 0, "Alert-high": 1, "Normal": 2}


def unit_status_by_month(flagged_df, group_col):
    """Count units per status per month, excluding No data."""
    result = (
        flagged_df[flagged_df["status"] != "No data"]
        .groupby(["yearmon_date", "status"])[group_col]
        .nunique()
        .reset_index(name="unit_count")
    )
    result["sort_order"] = result["status"].map(STACK_ORDER)
    return result


status_order = ["Normal", "Alert-high", "Alarm-high"]


def make_timeline_chart(df, title):
    return (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("yearmon_date:T", title="Month"),
            y=alt.Y("unit_count:Q", title=f"# {level_label}s", stack="zero"),
            color=alt.Color(
                "status:N", title="Status",
                scale=get_status_color_scale(),
                sort=status_order
            ),
            order=alt.Order("sort_order:Q", sort="ascending"),
            tooltip=[
                alt.Tooltip("yearmon_date:T", title="Month",            format="%Y-%m"),
                alt.Tooltip("status:N",        title="Status"),
                alt.Tooltip("unit_count:Q",    title=f"{level_label}s", format=",d"),
            ]
        )
        .properties(height=260, title=title)
        .interactive()
    )


col_s, col_d = st.columns(2)
with col_s:
    timeline_s = unit_status_by_month(flagged_s, geo_col)
    st.altair_chart(
        make_timeline_chart(timeline_s, f"Static — {level_label} Status per Month"),
        use_container_width=True
    )
with col_d:
    timeline_d = unit_status_by_month(flagged_d, geo_col)
    st.altair_chart(
        make_timeline_chart(timeline_d, f"Dynamic — {level_label} Status per Month"),
        use_container_width=True
    )

# ── Unit-level heatmap as drill-down expander ─────────────────────────────────
nodata_note = " Black = no data or below threshold." if fill_missing == "Leave as no data" or min_articles > 1 else ""
heatmap_height = max(280, top_n * 22)

tooltip_fields = [
    alt.Tooltip("yearmon_date:T",  title="Month",    format="%Y-%m"),
    alt.Tooltip(f"{geo_col}:N",    title=level_label),
    alt.Tooltip("article_count:Q", title="Articles", format=",d"),
    alt.Tooltip("status:N",        title="Status"),
    alt.Tooltip("z:Q",             title="Z-score",  format=".2f"),
]


def make_heatmap(flagged_df, title):
    return (
        alt.Chart(flagged_df)
        .mark_rect()
        .encode(
            x=alt.X("yearmon_date:T", title="Month"),
            y=alt.Y(f"{geo_col}:N", title="", sort=top_units),
            color=alt.Color("status:N", title="Status", scale=get_status_color_scale()),
            tooltip=tooltip_fields
        )
        .properties(height=heatmap_height, title=title)
    )


with st.expander(
    f"Unit-level warning history — {geo_level} × month heatmap "
    f"({len(top_units)} regions × {len(all_months)} months){nodata_note}",
    expanded=False
):
    st.caption(
        "Each cell's colour is the same status counted in the bar chart above. "
        "Expanding this confirms which regions drive each month's alert/alarm count."
    )
    col_s, col_d = st.columns(2)
    with col_s:
        st.altair_chart(make_heatmap(flagged_s, "Static"), use_container_width=True)
    with col_d:
        st.altair_chart(make_heatmap(flagged_d, "Dynamic"), use_container_width=True)

# ── Sidebar download ──────────────────────────────────────────────────────────
st.sidebar.markdown("---")
csv = deduped_df.to_csv(index=False).encode("utf-8")
st.sidebar.download_button(
    "Download Deduplicated Data",
    csv,
    "validation_deduped_articles.csv",
    "text/csv",
    key="p6_download"
)
