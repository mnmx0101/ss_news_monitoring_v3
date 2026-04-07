"""
Page 4: Article Browser
Search and read individual articles with full metadata.
Default: radiotamazuj, Negative, full date range, Political Instability, Central Equatoria.
Shows cleaned text only.
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_loader import load_data
from utils.filters import (
    render_source_filter, render_date_filter, render_sentiment_filter,
    render_adm1_filter, render_adm2_filter,
    render_keyword_filter, apply_filters, render_summary_metrics
)

st.set_page_config(page_title="Article Browser", layout="wide")

st.title("Article Browser")
st.markdown("Search and read individual articles with full metadata.")

# Load data
df = load_data()

# Sidebar filters with defaults
st.sidebar.header("Filters")
sources = render_source_filter(df, "p4", default=["radiotamazuj"])
sentiments = render_sentiment_filter(df, "p4", default=["Negative"])
date_range = render_date_filter(df, "p4")

# Label filter -- default to Political Instability
all_labels = sorted([l for l in df["Label"].dropna().unique().tolist() if l != "Uncategorized"]) if "Label" in df.columns else []
default_labels = ["Political Instability"] if "Political Instability" in all_labels else all_labels
labels = st.sidebar.multiselect(
    "Article Labels",
    options=all_labels,
    default=default_labels,
    key="p4_labels"
)

st.sidebar.markdown("---")
st.sidebar.subheader("Geographic Scope")
adm1 = render_adm1_filter(df, "p4", default=["Central Equatoria"])
adm2 = render_adm2_filter(df, adm1_selection=adm1, key_prefix="p4")

keyword = render_keyword_filter("p4")

# Apply filters
filtered_df = apply_filters(
    df, sources=sources, date_range=date_range,
    sentiments=sentiments, labels=labels, adm1=adm1, adm2=adm2, keyword=keyword
)

# Summary metrics
render_summary_metrics(filtered_df)

st.markdown("---")

if filtered_df.empty:
    st.warning("No articles match the current filters. Try adjusting your filters.")
else:
    display_df = filtered_df.sort_values("date", ascending=False).reset_index(drop=True)

    display_df["display_title"] = (
        display_df["date"].dt.strftime("%Y-%m-%d") + " | " +
        display_df["adm1_name_final"].astype(str) + " | " +
        display_df["title"].astype(str).str[:60] + "..."
    )

    st.subheader("Select an Article")

    col1, col2 = st.columns([3, 1])
    with col1:
        selected_idx = st.selectbox(
            "Choose from filtered articles",
            range(len(display_df)),
            format_func=lambda x: display_df.iloc[x]["display_title"],
            key="p4_article_select"
        )
    with col2:
        st.metric("Matching Articles", f"{len(display_df):,}")

    art = display_df.iloc[selected_idx]

    st.markdown("---")
    st.subheader(f"{art['title']}")

    # Metadata
    mcol1, mcol2, mcol3, mcol4 = st.columns(4)
    with mcol1:
        st.markdown(f"**Date:** {art['date'].strftime('%Y-%m-%d')}")
    with mcol2:
        st.markdown(f"**Source:** {art.get('retrieve_source', 'N/A')}")
    with mcol3:
        st.markdown(f"**Region:** {art['adm1_name_final']}")
    with mcol4:
        st.markdown(f"**County:** {art['adm2_name_final']}")

    mcol5, mcol6, mcol7, mcol8 = st.columns(4)
    with mcol5:
        st.markdown(f"**Label:** {art['Label']}")
    with mcol6:
        st.markdown(f"**Sentiment:** {art['sentiment_label']}")
    with mcol7:
        st.markdown(f"**Score:** {art['sentiment_score']:.3f}")
    with mcol8:
        if art.get('url'):
            st.markdown(f"**[View Original]({art['url']})**")

    st.markdown("---")

    # Article text -- cleaned only
    st.subheader("Article Text (Cleaned)")
    clean_text = art.get('paragraphs_cleaned', 'No cleaned text available.')
    if pd.isna(clean_text):
        clean_text = 'No cleaned text available.'
    st.markdown(f"""
    <div style="background-color: #f0f7ff; padding: 20px; border-radius: 10px; max-height: 500px; overflow-y: auto; line-height: 1.6;">
        {clean_text}
    </div>
    """, unsafe_allow_html=True)
