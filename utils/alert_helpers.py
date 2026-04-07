"""
Alert/Alarm calculation helpers for anomaly detection.
Supports both static (full-span) and dynamic (12-month rolling) thresholds.
NaN values in the value column are treated as "No data" and excluded from
mean/SD calculations.
"""

import pandas as pd
import numpy as np
import altair as alt


def add_sd_flags_static(df_in, group_col, value_col):
    """
    STATIC threshold: Mean/SD computed over the entire time span per group.
    NaN rows are assigned status='No data' and excluded from mean/SD.
    Flags: Normal, Alert-high, Alarm-high, No data.
    """
    out = df_in.copy()
    no_data_mask = out[value_col].isna()

    # pandas transform skips NaN by default — mean/SD computed on observed values only
    mu = out.groupby(group_col)[value_col].transform("mean")
    sd = out.groupby(group_col)[value_col].transform(lambda s: s.std(ddof=0))

    out["mu"] = mu
    out["sd"] = sd

    sd_safe = out["sd"].replace(0, np.nan)
    out["z"] = (out[value_col] - out["mu"]) / sd_safe
    out["z"] = out["z"].fillna(0.0)

    is_alarm_high = (~no_data_mask) & (out["z"] >= 2)
    is_alert_high = (~no_data_mask) & (out["z"] >= 1) & (out["z"] < 2)

    out["status"] = "Normal"
    out.loc[is_alert_high, "status"] = "Alert-high"
    out.loc[is_alarm_high, "status"] = "Alarm-high"
    out.loc[no_data_mask,  "status"] = "No data"
    out.loc[no_data_mask,  "z"]      = np.nan

    return out


def add_sd_flags_dynamic(df_in, group_col, value_col, time_col="yearmon_date", window_months=12):
    """
    DYNAMIC threshold: Mean/SD computed over the trailing `window_months` months
    before each time point t, per group.
    NaN rows are assigned status='No data' and excluded from the trailing window.
    Flags: Normal, Alert-high, Alarm-high, No data.
    """
    out = df_in.copy()
    out = out.sort_values([group_col, time_col]).reset_index(drop=True)

    results = []
    for group_name, group_df in out.groupby(group_col):
        group_df = group_df.sort_values(time_col).copy()

        z_vals      = []
        mu_vals     = []
        sd_vals     = []
        status_vals = []

        for idx, row in group_df.iterrows():
            # No-data row — skip SD computation entirely
            if pd.isna(row[value_col]):
                z_vals.append(np.nan)
                mu_vals.append(np.nan)
                sd_vals.append(np.nan)
                status_vals.append("No data")
                continue

            current_date   = row[time_col]
            lookback_start = current_date - pd.DateOffset(months=window_months)

            # Trailing window: observed (non-NaN) rows only
            trailing = group_df[
                (group_df[time_col] >= lookback_start) &
                (group_df[time_col] <  current_date) &
                (group_df[value_col].notna())
            ]

            if len(trailing) < 3:
                z_vals.append(0.0)
                mu_vals.append(np.nan)
                sd_vals.append(np.nan)
                status_vals.append("Normal")
                continue

            mu = trailing[value_col].mean()
            sd = trailing[value_col].std(ddof=0)

            mu_vals.append(mu)
            sd_vals.append(sd)

            if sd == 0 or np.isnan(sd):
                z_vals.append(0.0)
                status_vals.append("Normal")
            else:
                z = (row[value_col] - mu) / sd
                z_vals.append(z)
                if z >= 2:
                    status_vals.append("Alarm-high")
                elif z >= 1:
                    status_vals.append("Alert-high")
                else:
                    status_vals.append("Normal")

        group_df["z"]      = z_vals
        group_df["mu"]     = mu_vals
        group_df["sd"]     = sd_vals
        group_df["status"] = status_vals
        results.append(group_df)

    return pd.concat(results, ignore_index=True)


def get_status_color_scale():
    """Return consistent color scale for status (including No data = black)."""
    return alt.Scale(
        domain=["Normal", "Alert-high", "Alarm-high", "No data"],
        range=["#4caf50", "#ff9800", "#f44336", "#1a1a1a"]
    )


def render_alert_legend():
    """Display color legend for alerts."""
    import streamlit as st

    st.markdown("""
    <div style="display: flex; gap: 24px; margin-bottom: 10px; font-size: 0.85em; flex-wrap: wrap;">
        <span><span style="display:inline-block;width:12px;height:12px;background:#4caf50;border:1px solid #388e3c;margin-right:4px;"></span> <b>Normal</b>: Within 1 SD</span>
        <span><span style="display:inline-block;width:12px;height:12px;background:#ff9800;border:1px solid #e68a00;margin-right:4px;"></span> <b>Alert-high</b>: 1–2 SD above mean</span>
        <span><span style="display:inline-block;width:12px;height:12px;background:#f44336;border:1px solid #d32f2f;margin-right:4px;"></span> <b>Alarm-high</b>: &gt;2 SD above mean</span>
        <span><span style="display:inline-block;width:12px;height:12px;background:#1a1a1a;border:1px solid #555;margin-right:4px;"></span> <b>No data</b>: Missing or below threshold</span>
    </div>
    """, unsafe_allow_html=True)


def make_heatmap_pair(ts_data, group_col, value_col, label_name, group_order, height=400):
    """
    Create a pair of heatmaps (static + dynamic) for a given label.
    Returns (static_chart, dynamic_chart).
    """
    ts_static  = add_sd_flags_static(ts_data,  group_col, value_col)
    ts_dynamic = add_sd_flags_dynamic(ts_data, group_col, value_col)

    tooltip_fields = [
        alt.Tooltip("yearmon_date:T",    title="Month",    format="%Y-%m"),
        alt.Tooltip(f"{group_col}:N",    title="Region"),
        alt.Tooltip(f"{value_col}:Q",    title="Articles", format=",d"),
        alt.Tooltip("status:N",          title="Status"),
        alt.Tooltip("z:Q",               title="Z-score",  format=".2f")
    ]

    static_chart = alt.Chart(ts_static).mark_rect().encode(
        x=alt.X("yearmon_date:T", title="Month"),
        y=alt.Y(f"{group_col}:N", title="", sort=group_order),
        color=alt.Color("status:N", title="Status", scale=get_status_color_scale()),
        tooltip=tooltip_fields
    ).properties(height=height, title="Static Threshold (Full-Span Mean/SD)")

    dynamic_chart = alt.Chart(ts_dynamic).mark_rect().encode(
        x=alt.X("yearmon_date:T", title="Month"),
        y=alt.Y(f"{group_col}:N", title="", sort=group_order),
        color=alt.Color("status:N", title="Status", scale=get_status_color_scale()),
        tooltip=tooltip_fields
    ).properties(height=height, title="Dynamic Threshold (12-Month Rolling Mean/SD)")

    return static_chart, dynamic_chart
