"""
Threshold computation utilities for V4 ADM Insights.
Supports four methods:
  - percentile:   Alert at p1-th pct, Alarm at p2-th pct
  - tukey:        Outlier fence based on IQR; alert at Q3+k*IQR, alarm at Q3+2k*IQR
  - zscore:       Alert at mean+1*SD, Alarm at mean+2*SD (configurable multipliers)
  - categorical:  National-average P1/P2 applied uniformly to every region
"""

import numpy as np
import pandas as pd


def compute_thresholds(values: pd.Series, method: str, params: dict) -> tuple:
    """
    Compute (p1, p2) alert/alarm thresholds for a series of observed values.

    Parameters
    ----------
    values : pd.Series  - observed metric values (already filtered to observed months)
    method : str        - 'percentile' | 'tukey' | 'zscore' | 'categorical'
    params : dict       - method-specific parameters (see below)

    Returns
    -------
    (p1, p2) : tuple of floats
    """
    v = values.dropna()

    if len(v) == 0:
        return (0.0, 0.0)

    if method == "percentile":
        # params: {"p1": 75, "p2": 90}
        p1 = np.percentile(v, params.get("p1", 75))
        p2 = np.percentile(v, params.get("p2", 90))

    elif method == "tukey":
        # params: {"k": 1.5}  - alert at Q3+k*IQR, alarm at Q3+2k*IQR
        k = params.get("k", 1.5)
        q1 = np.percentile(v, 25)
        q3 = np.percentile(v, 75)
        iqr = q3 - q1
        p1 = q3 + k * iqr
        p2 = q3 + 2 * k * iqr

    elif method == "zscore":
        # params: {"sd1": 1.0, "sd2": 2.0}
        mu = v.mean()
        sd = v.std(ddof=1) if len(v) > 1 else 0.0
        p1 = mu + params.get("sd1", 1.0) * sd
        p2 = mu + params.get("sd2", 2.0) * sd

    elif method == "categorical":
        # Thresholds pre-computed nationally and passed via params
        p1 = params.get("p1", 0.0)
        p2 = params.get("p2", 0.0)

    else:
        raise ValueError(f"Unknown threshold method: {method}")

    # Ensure p2 >= p1
    if p2 < p1:
        p2 = p1

    return float(p1), float(p2)


def classify_region(group: pd.DataFrame, metric_col: str, method: str, params: dict,
                    country_p1: float, country_p2: float, country_median: float, N: int):
    """
    Classify each row in a region group as No Concern / Alert / Alarm.

    Regions with fewer than N observed months are flagged as fallback (with warning mark)
    and suppressed to 'No Concern' — they lack sufficient historical baseline to produce
    reliable signals. They are still shown in heatmaps with the warning mark.

    Returns the group with columns: status, p1, p2, display_name, fallback.
    """
    n_obs = len(group)
    is_fallback = n_obs < N

    if "adm2_name_final" in group.columns and not group["adm2_name_final"].isnull().all():
        base_name = group.iloc[0]["adm2_name_final"]
        state_name = group.iloc[0].get("adm1_name_final", "")
        region_name = f"{base_name} ({state_name})" if state_name else base_name
    elif "adm1_name_final" in group.columns:
        region_name = group.iloc[0]["adm1_name_final"]
    else:
        region_name = "?"

    if method == "categorical":
        # Use nationally pre-computed thresholds directly for all regions
        p1 = country_p1
        p2 = country_p2
        # Mute Central Equatoria and Juba alarms directly
        if "Central Equatoria" in region_name or "Juba" in region_name:
            p1 = None
            p2 = None
    elif not is_fallback:
        p1, p2 = compute_thresholds(group[metric_col], method, params)
    else:
        # Proportional scaling stored for display only
        reg_median = group[metric_col].median()
        scale = (reg_median / country_median) if country_median > 0 else 1.0
        p1 = country_p1 * scale
        p2 = country_p2 * scale

    group = group.copy()

    if is_fallback:
        # Suppress alert/alarm: insufficient history for reliable signal
        group["status"] = "No Concern"
    else:
        group["status"] = "No Concern"
        if p1 is not None:
            group.loc[group[metric_col] >= p1, "status"] = "Alert"
        if p2 is not None:
            group.loc[group[metric_col] >= p2, "status"] = "Alarm"

    group["p1"] = p1
    group["p2"] = p2
    group["fallback"] = is_fallback
    group["display_name"] = f"{region_name} ⚠️" if is_fallback else region_name
    return group


def compute_country_stats(topic_df: pd.DataFrame, metric_col: str, method: str, params: dict):
    """Compute country-wide thresholds.
    For 'categorical': uses percentile 75/90 to generate national baseline;
    actual categorical thresholds are averaged per-region in the calling code.
    """
    if method == "categorical":
        p1, p2 = compute_thresholds(topic_df[metric_col], "percentile", {"p1": 75, "p2": 90})
    else:
        p1, p2 = compute_thresholds(topic_df[metric_col], method, params)
    median = topic_df[metric_col].median()
    return p1, p2, median


THRESHOLD_DESCRIPTIONS = {
    "percentile": (
        "**Percentile method** - Ranks all monthly article counts for this region from "
        "lowest to highest. Alert fires when a month lands in the top 25% of historical "
        "counts (75th percentile by default); Alarm fires when it lands in the top 10% "
        "(90th percentile). Easy to understand: if you set p1 = 75, a month is flagged "
        "only if it has more articles than 75% of all past months."
    ),
    "tukey": (
        "**Tukey Fence method** - Uses the 'interquartile range' (IQR, the spread of the "
        "middle 50% of months) to define what counts as an outlier. Alert fires beyond "
        "Q3 + k x IQR; Alarm fires beyond Q3 + 2k x IQR. The default k = 1.5 is the "
        "standard statistical rule for detecting mild outliers - same logic used in box "
        "plots. Works well even when data is skewed."
    ),
    "zscore": (
        "**Z-Score (Standard Deviation) method** - Calculates the long-term average "
        "and standard deviation across observed months. Alert fires when a month is more "
        "than 1 standard deviation above average (default); Alarm fires at 2 standard "
        "deviations above. Intuition: SD-1 catches unusual months (roughly top 16%), "
        "SD-2 catches very unusual ones (roughly top 2.5%). Works best when article "
        "counts follow a roughly normal (bell-curve) distribution."
    ),
    "categorical": (
        "**Categorical (National Average) method** - Computes the Alert bound (P1) and "
        "Alarm bound (P2) for every region individually using the Percentile method "
        "(default 75th/90th), then takes the national average of those bounds. Every "
        "region is then judged against the same national bar. Removes the 'easy alarm' "
        "problem for high-volume regions and treats all counties on equal footing - "
        "useful for spatial comparison across districts."
    ),
}
