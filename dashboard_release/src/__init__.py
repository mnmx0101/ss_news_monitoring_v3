"""
GDELT Processor — source package
=================================
Import the main public functions from each module for convenience.

Usage example
-------------
from src import prepare_df, build_panel, plot_convergence_heatmaps, summarize_conflict
"""

from .sources    import KEYWORD_MAP, categorize_source, prepare_df
from .scraper    import (safe_extract, scrape_and_report,
                         scrape_peak_articles, is_usable, is_usable_lenient)
from .validation import (METRIC_CONFIG, compute_alert_level, get_alert_matrices,
                         compute_convergence, plot_convergence_heatmaps,
                         plot_national_convergence, plot_convergence_by_adm1)
from .llm        import inspect_articles, prepare_texts, summarize_conflict

__all__ = [
    # sources
    "KEYWORD_MAP", "categorize_source", "prepare_df",
    # scraper
    "safe_extract", "scrape_and_report", "scrape_peak_articles",
    "is_usable", "is_usable_lenient",
    # validation
    "METRIC_CONFIG", "compute_alert_level", "get_alert_matrices",
    "compute_convergence", "plot_convergence_heatmaps",
    "plot_national_convergence", "plot_convergence_by_adm1",
    # llm
    "inspect_articles", "prepare_texts", "summarize_conflict",
]
