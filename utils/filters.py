"""
Shared filter components for consistent UI across all pages.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import re


def render_source_filter(df, key_prefix="", default=None):
    """Render source multi-select filter."""
    sources = sorted(df["retrieve_source"].dropna().unique().tolist()) if "retrieve_source" in df.columns else []
    if default is None:
        default = sources
    else:
        default = [s for s in default if s in sources]
    return st.sidebar.multiselect(
        "Sources",
        options=sources,
        default=default,
        key=f"{key_prefix}_sources"
    )


def render_date_filter(df, key_prefix=""):
    """Render date range filter."""
    min_date = df["date"].min().date() if not df.empty else datetime.today().date()
    max_date = df["date"].max().date() if not df.empty else datetime.today().date()
    return st.sidebar.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        key=f"{key_prefix}_dates"
    )


def render_sentiment_filter(df, key_prefix="", default=None):
    """Render sentiment type multi-select filter."""
    sentiments = sorted(df["sentiment_label"].dropna().unique().tolist()) if "sentiment_label" in df.columns else []
    if default is None:
        default = sentiments
    else:
        default = [s for s in default if s in sentiments]
    return st.sidebar.multiselect(
        "Sentiment Type",
        options=sentiments,
        default=default,
        key=f"{key_prefix}_sentiment"
    )


def render_label_filter(df, key_prefix=""):
    """Render article label multi-select filter."""
    labels = sorted([l for l in df["Label"].dropna().unique().tolist() if l != "Uncategorized"]) if "Label" in df.columns else []
    return st.sidebar.multiselect(
        "Article Labels",
        options=labels,
        default=labels,
        key=f"{key_prefix}_labels"
    )


def render_adm1_filter(df, key_prefix="", default=None):
    """Render ADM1 region multi-select filter."""
    regions = sorted(df["adm1_name_final"].dropna().unique().tolist()) if "adm1_name_final" in df.columns else []
    if default is None:
        default = regions
    else:
        default = [r for r in default if r in regions]
    return st.sidebar.multiselect(
        "ADM1 Regions",
        options=regions,
        default=default,
        key=f"{key_prefix}_adm1"
    )


def render_adm2_filter(df, adm1_selection=None, key_prefix=""):
    """Render ADM2 county multi-select filter, filtered by ADM1."""
    pool = df.copy()
    if adm1_selection:
        pool = pool[pool["adm1_name_final"].isin(adm1_selection)]
    counties = sorted(pool["adm2_name_final"].dropna().unique().tolist()) if "adm2_name_final" in pool.columns else []
    counties = [c for c in counties if c != "Unknown County"]
    return st.sidebar.multiselect(
        "ADM2 Counties",
        options=counties,
        default=counties,
        key=f"{key_prefix}_adm2"
    )


def render_keyword_filter(key_prefix=""):
    """Render keyword search input."""
    return st.sidebar.text_input(
        "Keyword Search",
        value="",
        key=f"{key_prefix}_keyword"
    )


def apply_filters(df, sources=None, date_range=None, sentiments=None, labels=None, adm1=None, adm2=None, keyword=None):
    """Apply all selected filters to dataframe."""
    filtered = df.copy()
    
    if sources:
        filtered = filtered[filtered["retrieve_source"].isin(sources)]
    
    if date_range and len(date_range) == 2:
        filtered = filtered[
            (filtered["date"].dt.date >= date_range[0]) &
            (filtered["date"].dt.date <= date_range[1])
        ]
    
    if sentiments:
        filtered = filtered[filtered["sentiment_label"].isin(sentiments)]
    
    if labels:
        filtered = filtered[filtered["Label"].isin(labels)]
    
    if adm1:
        filtered = filtered[filtered["adm1_name_final"].isin(adm1)]
    
    if adm2:
        filtered = filtered[filtered["adm2_name_final"].isin(adm2)]
    
    if keyword and keyword.strip():
        query = keyword.strip()
        parts = re.split(r"\s+OR\s+", query, flags=re.IGNORECASE)
        mask = False
        for term in parts:
            term = term.strip().strip('"').strip("'")
            if term:
                match = (
                    filtered["paragraphs"].astype(str).str.contains(term, case=False, na=False) |
                    filtered["title"].astype(str).str.contains(term, case=False, na=False)
                )
                mask = mask | match
        filtered = filtered[mask]
    
    return filtered


def render_summary_metrics(df):
    """Display summary metrics row."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Articles", f"{len(df):,}")
    
    with col2:
        if not df.empty:
            date_span = f"{df['date'].min().strftime('%Y-%m')} to {df['date'].max().strftime('%Y-%m')}"
        else:
            date_span = "N/A"
        st.metric("Date Span", date_span)
    
    with col3:
        if "retrieve_source" in df.columns and not df.empty:
            top_source = df["retrieve_source"].value_counts().idxmax()
        else:
            top_source = "N/A"
        st.metric("Top Source", top_source)
    
    with col4:
        if "Label" in df.columns and not df.empty:
            top_label = df["Label"].value_counts().idxmax()
        else:
            top_label = "N/A"
        st.metric("Top Label", top_label)
