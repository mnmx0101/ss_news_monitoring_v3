"""
sources.py
==========
Source categorization and filtering for GDELT data.

Functions
---------
- categorize_source(url)   : map a raw URL to a known source label
- prepare_df(df, year_min) : normalize, categorize, and filter the raw GDELT dataframe
"""

import pandas as pd

# ── Known source keyword → canonical label ────────────────────────────────────
KEYWORD_MAP = {
    'radiotamazuj': 'radiotamazuj',
    'eyeradio':     'eyeradio',
    'sudantribune': 'sudantribune',
    'reliefweb':    'reliefweb',
    'allafrica':    'allafrica',
    'bbc':          'bbc',
}


def categorize_source(url: str) -> str:
    """
    Map a raw SOURCEURL to one of the known source labels.
    Returns 'other' if no keyword matches.
    """
    if pd.isna(url):
        return 'other'
    url_lower = url.lower()
    for keyword, canonical in KEYWORD_MAP.items():
        if keyword in url_lower:
            return canonical
    return 'other'


def prepare_df(df: pd.DataFrame, year_min: int = 2014) -> pd.DataFrame:
    """
    Normalize source domain, categorize into known sources,
    and return filtered subset excluding 'other' and years before year_min.

    Parameters
    ----------
    df       : raw GDELT dataframe loaded from GCS
    year_min : minimum year to retain (inclusive)

    Returns
    -------
    Filtered and normalized dataframe with 'sourcewebsite' and
    'source_grouped' columns added.
    """
    df = df.copy()

    df['sourcewebsite'] = (
        df['SOURCEURL']
        .str.split('/').str[2]
        .str.lower()
        .str.strip()
        .str.replace(r'^(www\.|m\.|mobile\.)', '', regex=True)
    )

    df['source_grouped'] = df['SOURCEURL'].apply(categorize_source)

    return (
        df[
            (df['source_grouped'] != 'other') &
            (df['Year'] >= year_min)
        ]
        .reset_index(drop=True)
    )
