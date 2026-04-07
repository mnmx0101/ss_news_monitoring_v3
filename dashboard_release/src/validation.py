"""
validation.py
=============
Alert/anomaly detection and cross-source convergence visualization.

Constants
---------
- METRIC_CONFIG   : metric definitions (aggregation function, direction, display title)
- CMAP_SRC, NORM_SRC     : colormap for per-source heatmaps
- CMAP_CONV, NORM_CONV   : colormap for convergence heatmaps

Functions
---------
- compute_alert_level(series, direction)            : SD-based alert labeling
- _build_alert_matrix(panel, metric, agg, dir)     : build alert matrix for one source
- get_alert_matrices(panels, metric, agg, dir)     : build aligned matrices for all sources
- compute_convergence(matrices)                     : count sources at alert+ per cell
- plot_convergence_heatmaps(panels, ...)            : heatmap grid + convergence column
- plot_national_convergence(panels, ...)            : stacked bar + rolling mean (national)
- plot_convergence_by_adm1(panels, ...)             : per-ADM1 convergence subplots
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# ── Metric configuration ──────────────────────────────────────────────────────
METRIC_CONFIG = {
    'n_events_total':   {'agg': 'sum',  'direction': 'high', 'title': 'Total events'},
    'n_fatality_proxy': {'agg': 'sum',  'direction': 'high', 'title': 'Fatality proxy'},
    'avg_tone_mean':    {'agg': 'mean', 'direction': 'low',  'title': 'Avg tone'},
    'num_mentions_sum': {'agg': 'sum',  'direction': 'high', 'title': 'Media mentions'},
}

# ── Colormaps ─────────────────────────────────────────────────────────────────
# Per-source: 0=normal, 1=alert, 2=alarm, 3=no data
CMAP_SRC   = mcolors.ListedColormap(['#F1EFE8', '#FAC775', '#E24B4A', '#B4B2A9'])
BOUNDS_SRC = [0, 0.5, 1.5, 2.5, 3.5]
NORM_SRC   = mcolors.BoundaryNorm(BOUNDS_SRC, CMAP_SRC.N)

# Convergence: 0=none, 1–6=number of sources at alert+
CONV_COLORS = ['#F1EFE8', '#9FE1CB', '#FAC775', '#D85A30', '#E24B4A', '#7F77DD', '#483D8B']
CMAP_CONV   = mcolors.ListedColormap(CONV_COLORS)
BOUNDS_CONV = [-0.5, 0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5]
NORM_CONV   = mcolors.BoundaryNorm(BOUNDS_CONV, CMAP_CONV.N)


# ── Core alert computation ────────────────────────────────────────────────────

def compute_alert_level(series: pd.Series, direction: str) -> pd.Series:
    """
    Classify each observation as 0 (normal), 1 (alert ±1SD), 2 (alarm ±2SD),
    or 3 (no data) relative to the long-term mean of the series.
    """
    mu, sd = series.mean(), series.std()
    out    = pd.Series(np.nan, index=series.index)
    obs    = series.notna()
    out[obs] = 0
    if direction == 'high':
        out[obs & (series >= mu + sd)]   = 1
        out[obs & (series >= mu + 2*sd)] = 2
    else:
        out[obs & (series <= mu - sd)]   = 1
        out[obs & (series <= mu - 2*sd)] = 2
    return out.fillna(3)


def _build_alert_matrix(panel: pd.DataFrame, metric: str,
                        agg_func: str, direction: str) -> pd.DataFrame:
    """Aggregate panel to (year_month × ADM1) and classify into alert levels."""
    plot_panel = panel.copy()
    plot_panel.loc[plot_panel['is_observed'] == 0, metric] = np.nan
    matrix = (
        plot_panel
        .groupby(['year_month', 'ADM1_EN'])[metric]
        .agg(agg_func)
        .unstack('ADM1_EN')
    )
    return matrix.apply(lambda col: compute_alert_level(col, direction=direction))


def get_alert_matrices(panels: dict, metric: str,
                       agg_func: str, direction: str) -> dict:
    """
    Build alert matrices for each source panel, aligned to a common
    (month × ADM1) index. Missing coverage is filled with 3 (no data).
    """
    matrices = {
        src: _build_alert_matrix(panel, metric, agg_func, direction)
        for src, panel in panels.items()
    }
    all_months = sorted(set().union(*[m.index   for m in matrices.values()]))
    all_adm1   = sorted(set().union(*[m.columns for m in matrices.values()]))
    return {
        src: m.reindex(index=all_months, columns=all_adm1).fillna(3)
        for src, m in matrices.items()
    }


def compute_convergence(matrices: dict) -> pd.DataFrame:
    """
    For each (month, ADM1) cell, count how many sources are at alert (1) or
    alarm (2). Sources with no data (3) are excluded. Returns values 0–5.
    """
    src_list = list(matrices.keys())
    arr      = np.stack([matrices[s].values for s in src_list], axis=0)
    at_alert = (arr >= 1) & (arr != 3)
    n_sources_alert = at_alert.sum(axis=0)
    return pd.DataFrame(
        n_sources_alert,
        index   = list(matrices[src_list[0]].index),
        columns = list(matrices[src_list[0]].columns),
    )


# ── Plot helpers ──────────────────────────────────────────────────────────────

def _setup_time_ticks(ref_matrix, step=6):
    tick_pos  = list(range(0, len(ref_matrix.index), step))
    tick_labs = [ref_matrix.index[t] for t in tick_pos]
    return tick_pos, tick_labs


def _draw_source_heatmap(ax, matrix, src, tick_pos, tick_labs, adm1_labels, show_yticks):
    ax.imshow(matrix.T.values, aspect='auto', cmap=CMAP_SRC,
              norm=NORM_SRC, interpolation='nearest')
    ax.set_title(src, fontsize=9, fontweight='bold', pad=4)
    ax.set_xticks(tick_pos)
    ax.set_xticklabels(tick_labs, rotation=90, ha='right', fontsize=6)
    if show_yticks:
        ax.set_yticks(range(len(adm1_labels)))
        ax.set_yticklabels(adm1_labels, fontsize=8)
    else:
        ax.set_yticks([])


def _draw_incidence_bar(ax, matrix, tick_pos, tick_labs, src, show_legend):
    print(f"      Inside _draw_incidence_bar for {src}...")
    x           = range(len(matrix.index))
    alert_pm    = (matrix == 1).sum(axis=1)
    alarm_pm    = (matrix == 2).sum(axis=1)
    observed_pm = (matrix != 3).sum(axis=1)
    
    print(f"      - x length: {len(x)}, alerts: {len(alert_pm)}, alarms: {len(alarm_pm)}")
    
    ax.bar(list(x), alert_pm.values, color='#FAC775', width=1.0, label='alert')
    ax.bar(list(x), alarm_pm.values, color='#E24B4A', width=1.0,
           label='alarm', bottom=alert_pm.values)
    ax.plot(list(x), observed_pm.values, color='#B4B2A9',
            linewidth=0.8, linestyle='--', label='w/ data')
    ax.set_xticks(tick_pos)
    ax.set_xticklabels(tick_labs, rotation=90, ha='right', fontsize=6)
    ax.set_title(src, fontsize=8, pad=3)
    ax.spines[['top', 'right']].set_visible(False)
    ax.tick_params(axis='y', labelsize=7)
    if show_legend:
        ax.set_ylabel('# ADM1s', fontsize=8)
        ax.legend(fontsize=6, frameon=False, loc='upper left')


def _draw_convergence_bar(ax, conv_matrix, tick_pos, tick_labs):
    x       = range(len(conv_matrix))
    bottoms = np.zeros(len(conv_matrix))
    for n, color in zip(range(1, 6), CONV_COLORS[1:]):
        counts = (conv_matrix == n).sum(axis=1).values
        ax.bar(list(x), counts, bottom=bottoms,
               color=color, width=1.0, label=f'{n} src')
        bottoms += counts
    ax.set_xticks(tick_pos)
    ax.set_xticklabels(tick_labs, rotation=90, ha='right', fontsize=6)
    ax.set_title('convergence', fontsize=8, pad=3)
    ax.spines[['top', 'right']].set_visible(False)
    ax.tick_params(axis='y', labelsize=7)
    ax.legend(fontsize=6, frameon=False, loc='upper left')


# ── Main plot functions ───────────────────────────────────────────────────────

def plot_convergence_heatmaps(panels: dict, metric: str, agg_func: str,
                              direction: str, title: str):
    """
    Draw a heatmap grid — one column per source plus a convergence column.
    Each row = ADM1 region, each column-pixel = month.
    Bottom row shows stacked incidence bars.
    """
    matrices    = get_alert_matrices(panels, metric, agg_func, direction)
    conv_matrix = compute_convergence(matrices)

    src_list    = list(matrices.keys())
    ref_matrix  = matrices[src_list[0]]
    adm1_labels = list(ref_matrix.columns)
    tick_pos, tick_labs = _setup_time_ticks(ref_matrix)
    n_cols      = len(src_list) + 1

    fig, axes = plt.subplots(
        2, n_cols,
        figsize=(4.5 * n_cols, 9),
        gridspec_kw={'wspace': 0.05, 'hspace': 0.4, 'height_ratios': [2, 1]}
    )

    for i, src in enumerate(src_list):
        _draw_source_heatmap(axes[0, i], matrices[src], src,
                             tick_pos, tick_labs, adm1_labels, show_yticks=(i == 0))

    ax_conv = axes[0, -1]
    im_conv = ax_conv.imshow(conv_matrix.T.values, aspect='auto',
                              cmap=CMAP_CONV, norm=NORM_CONV, interpolation='nearest')
    ax_conv.set_title('convergence\n(# sources at alert+)', fontsize=9, fontweight='bold', pad=4)
    ax_conv.set_xticks(tick_pos)
    ax_conv.set_xticklabels(tick_labs, rotation=90, ha='right', fontsize=6)
    ax_conv.set_yticks([])

    fig.colorbar(
        plt.cm.ScalarMappable(norm=NORM_SRC, cmap=CMAP_SRC),
        ax=axes[0, :-1], ticks=[0, 1, 2, 3], shrink=0.6, pad=0.01, location='bottom'
    ).ax.set_xticklabels(['normal', 'alert', 'alarm', 'no data'], fontsize=7)

    fig.colorbar(
        im_conv, ax=ax_conv, ticks=list(range(len(src_list) + 1)),
        shrink=0.6, pad=0.01, location='bottom'
    ).ax.set_xticklabels(
        ['0'] + [f'{n} src' for n in range(1, len(src_list) + 1)], fontsize=7
    )

    for i, src in enumerate(src_list):
        _draw_incidence_bar(axes[1, i], matrices[src],
                            tick_pos, tick_labs, src, show_legend=(i == 0))
    _draw_convergence_bar(axes[1, -1], conv_matrix, tick_pos, tick_labs)

    fig.suptitle(f'{title} — source comparison & convergence',
                 fontsize=12, fontweight='bold', y=1.01)
    plt.savefig(f'convergence_{metric}.png', dpi=150, bbox_inches='tight')
    plt.show()


def plot_national_convergence(panels: dict, metric: str, agg_func: str,
                              direction: str, title: str,
                              roll_window: int = 12) -> pd.DataFrame:
    """
    Stacked bar chart of convergence over time at the national level,
    with a rolling-mean trend line and annotations for the top 5 peaks.

    Returns a dataframe of the top-5 peak months for the given metric.
    """
    matrices    = get_alert_matrices(panels, metric, agg_func, direction)
    conv_matrix = compute_convergence(matrices)
    ref_matrix  = matrices[list(matrices.keys())[0]]
    tick_pos    = list(range(0, len(ref_matrix.index), 6))
    tick_labs   = [ref_matrix.index[t] for t in tick_pos]
    x           = list(range(len(ref_matrix.index)))

    fig, ax = plt.subplots(figsize=(14, 4))
    bottoms = np.zeros(len(conv_matrix))
    total   = np.zeros(len(conv_matrix))

    for n, color in zip(range(1, 6), CONV_COLORS[1:]):
        counts  = (conv_matrix == n).sum(axis=1).values
        ax.bar(x, counts, bottom=bottoms, color=color, width=1.0,
               label=f'{n} src', alpha=0.85)
        bottoms += counts
        total   += counts

    rolling = pd.Series(total, index=ref_matrix.index).rolling(
        window=roll_window, center=True
    ).mean()
    ax.plot(x, rolling.values, color='#2C2C2A', linewidth=1.6,
            label=f'{roll_window}m rolling mean', zorder=5)

    top5 = rolling.dropna().nlargest(5).sort_index()
    for rank, (ym, val) in enumerate(top5.items(), start=1):
        xi = ref_matrix.index.get_loc(ym)
        ax.axvline(xi, color='#2C2C2A', linewidth=0.8, linestyle='--', alpha=0.5, zorder=4)
        y_offset = val + 0.3 + (rank % 2) * 0.8
        ax.annotate(
            f'{ym}\n(#{rank})', xy=(xi, val), xytext=(xi, y_offset),
            fontsize=7, ha='center', color='#2C2C2A',
            arrowprops=dict(arrowstyle='-', color='#888780', lw=0.8, shrinkA=0, shrinkB=2),
            bbox=dict(boxstyle='round,pad=0.3', fc='white', ec='#B4B2A9', lw=0.5, alpha=0.9),
            zorder=6,
        )

    ax.set_xticks(tick_pos)
    ax.set_xticklabels(tick_labs, rotation=45, ha='right', fontsize=8)
    ax.set_ylabel('# ADM1s', fontsize=9)
    ax.set_title(f'{title} — national convergence incidence (1+ sources)',
                 fontsize=11, fontweight='bold')
    ax.spines[['top', 'right']].set_visible(False)
    ax.tick_params(axis='y', labelsize=8)
    ax.legend(fontsize=8, frameon=False, ncol=2,
              loc='upper left', bbox_to_anchor=(1.01, 1), borderaxespad=0)
    plt.tight_layout()
    plt.savefig(f'national_convergence_{metric}.png', dpi=150, bbox_inches='tight')
    plt.show()

    return (
        top5
        .reset_index()
        .rename(columns={'index': 'year_month', 0: 'rolling_mean'})
        .assign(rank=range(1, 6), metric=metric)
        [['metric', 'rank', 'year_month', 'rolling_mean']]
    )


def plot_convergence_by_adm1(panels: dict, metric: str, agg_func: str,
                             direction: str, title: str,
                             roll_window: int = 6) -> dict:
    """
    Subplot grid — one panel per ADM1 state — showing convergence bars and
    rolling mean. Returns a dict {ADM1: {peak_1, peak_2}} of peak months.
    """
    matrices    = get_alert_matrices(panels, metric, agg_func, direction)
    conv_matrix = compute_convergence(matrices)
    ref_matrix  = matrices[list(matrices.keys())[0]]
    tick_pos    = list(range(0, len(ref_matrix.index), 6))
    tick_labs   = [ref_matrix.index[t] for t in tick_pos]
    x           = list(range(len(ref_matrix.index)))
    adm1_list   = list(conv_matrix.columns)

    n_cols = 3
    n_rows = -(-len(adm1_list) // n_cols)
    fig, axes = plt.subplots(
        n_rows, n_cols,
        figsize=(6 * n_cols, 3.5 * n_rows),
        sharex=False, sharey=False,
        gridspec_kw={'hspace': 0.5, 'wspace': 0.3}
    )
    axes = axes.flatten()
    peak_timing = {}

    for i, adm1 in enumerate(adm1_list):
        ax  = axes[i]
        col = conv_matrix[adm1].values

        bar_colors = [CONV_COLORS[int(v)] if int(v) < len(CONV_COLORS)
                      else CONV_COLORS[-1] for v in col]
        ax.bar(x, col, color=bar_colors, width=1.0, alpha=0.85)

        rolling = pd.Series(col, index=ref_matrix.index).rolling(
            window=roll_window, center=True
        ).mean()
        ax.plot(x, rolling.values, color='#2C2C2A', linewidth=1.2, zorder=5)

        top2 = rolling.dropna().nlargest(2)
        peak_timing[adm1] = {
            'peak_1': top2.index[0] if len(top2) > 0 else None,
            'peak_2': top2.index[1] if len(top2) > 1 else None,
        }

        for rank, (ym, val) in enumerate(top2.items(), start=1):
            xi = ref_matrix.index.get_loc(ym)
            ax.axvline(xi, color='#2C2C2A', linewidth=0.7, linestyle='--', alpha=0.5, zorder=4)
            ax.annotate(
                f'#{rank}\n{ym}', xy=(xi, val),
                xytext=(xi, val + 0.15 + (rank % 2) * 0.3),
                fontsize=5.5, ha='center', color='#2C2C2A',
                arrowprops=dict(arrowstyle='-', color='#888780', lw=0.6, shrinkA=0, shrinkB=2),
                bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='#B4B2A9', lw=0.4, alpha=0.9),
                zorder=6,
            )

        ax.set_title(adm1, fontsize=10, fontweight='bold', pad=4)
        ax.set_xticks(tick_pos)
        ax.set_xticklabels(tick_labs, rotation=45, ha='right', fontsize=6)
        ax.set_ylim(0, len(panels))
        ax.set_yticks(range(len(panels) + 1))
        ax.set_yticklabels([str(n) for n in range(len(panels) + 1)], fontsize=7)
        ax.set_ylabel('# src', fontsize=7)
        ax.spines[['top', 'right']].set_visible(False)

    for j in range(len(adm1_list), len(axes)):
        axes[j].set_visible(False)

    handles = [
        plt.Rectangle((0, 0), 1, 1, color=CONV_COLORS[n], alpha=0.85)
        for n in range(1, len(panels) + 1)
    ] + [plt.Line2D([0], [0], color='#2C2C2A', linewidth=1.2)]
    labels = [f'{n} src' for n in range(1, len(panels) + 1)] + [f'{roll_window}m mean']

    fig.legend(handles, labels, fontsize=8, frameon=False,
               ncol=len(panels) + 1, loc='lower center', bbox_to_anchor=(0.5, -0.02))
    fig.suptitle(f'{title} — convergence by ADM1 (# sources at alert+)',
                 fontsize=12, fontweight='bold')
    plt.tight_layout(rect=[0, 0.04, 1, 1])
    plt.savefig(f'convergence_adm1_{metric}.png', dpi=150, bbox_inches='tight')
    plt.show()

    return peak_timing
