"""
scraper.py
==========
URL accessibility auditing and article text extraction.

Functions
---------
- check_robots_txt(url, headers)         : check if path is disallowed by robots.txt
- check_url_accessibility(url, headers)  : full accessibility check (HTTP, paywall, bots)
- extract_article_text(url)              : extract main article body text
- is_usable(row)                         : strict usability check (blocks copyright too)
- is_usable_lenient(row)                 : lenient usability check (allows copyright signal)
- safe_extract(url, pre_check, delay)    : combined accessibility check + text extraction
- scrape_and_report(top_five_df, n, delay)      : batch-scrape and produce accessibility report
- scrape_peak_articles(peak_df, adm1, ym, src)  : scrape articles for a specific region/period
"""

import time
from urllib.parse import urlparse

import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

# ── Issue keyword lists ───────────────────────────────────────────────────────
PAYWALL_KEYWORDS = [
    "subscribe to read", "subscription required", "premium content",
    "sign in to read", "log in to read", "members only", "paid subscribers",
    "create an account", "unlock this article", "access this article",
]
BLOCK_KEYWORDS = [
    "access denied", "403 forbidden", "blocked", "captcha", "robot",
    "unusual traffic", "cloudflare", "enable javascript", "please verify you are human",
]
COPYRIGHT_KEYWORDS = [
    "reproduction prohibited", "all rights reserved", "do not reproduce",
    "no scraping", "automated access", "terms of use violation",
    "copyright notice", "republication prohibited",
]
HARD_BLOCKS = [
    "robots.txt disallows this path",
    "HTTP 403", "HTTP 401", "HTTP 429",
    "Request timed out", "Connection error",
]
HARD_BLOCKS_NO_COPYRIGHT = [
    "robots.txt disallows this path",
    "HTTP 403", "HTTP 401", "HTTP 429",
    "Request timed out", "Connection error",
]

# Cache for robots.txt disallow paths keyed by domain
ROBOTS_DISALLOW_PATHS: dict = {}


# ── Core helpers ──────────────────────────────────────────────────────────────

def check_robots_txt(url: str, headers: dict) -> bool:
    """Return True if robots.txt disallows the path for the given URL."""
    parsed = urlparse(url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    path = parsed.path or "/"
    domain = parsed.netloc

    if domain not in ROBOTS_DISALLOW_PATHS:
        try:
            r = requests.get(f"{base}/robots.txt", headers=headers, timeout=8)
            disallowed = [
                line.split(":", 1)[1].strip()
                for line in r.text.splitlines()
                if r.status_code == 200 and line.strip().lower().startswith("disallow:")
            ]
            ROBOTS_DISALLOW_PATHS[domain] = disallowed
        except Exception:
            ROBOTS_DISALLOW_PATHS[domain] = []

    return any(path.startswith(d) for d in ROBOTS_DISALLOW_PATHS[domain] if d)


def check_url_accessibility(url: str, headers: dict = None) -> dict:
    """
    Perform a comprehensive accessibility check on a URL.
    Returns a dict with keys: url, accessible, status_code, issues, html_snippet.
    """
    if headers is None:
        headers = {"User-Agent": "Mozilla/5.0"}

    result = {"url": url, "accessible": False, "status_code": None,
              "issues": [], "html_snippet": ""}

    try:
        if check_robots_txt(url, headers):
            result["issues"].append("robots.txt disallows this path")
    except Exception as e:
        result["issues"].append(f"robots.txt check failed: {e}")

    try:
        response = requests.get(url, headers=headers, timeout=12, allow_redirects=True)
        result["status_code"]  = response.status_code
        result["html_snippet"] = response.text[:2000]

        if response.status_code == 403:
            result["issues"].append("HTTP 403 — access forbidden")
        elif response.status_code == 401:
            result["issues"].append("HTTP 401 — authentication required")
        elif response.status_code == 429:
            result["issues"].append("HTTP 429 — rate limited")
        elif response.status_code >= 400:
            result["issues"].append(f"HTTP {response.status_code} error")

        soup      = BeautifulSoup(response.content, "html.parser")
        page_text = soup.get_text(separator=" ").lower()

        for kw in PAYWALL_KEYWORDS:
            if kw in page_text:
                result["issues"].append(f"Paywall signal: '{kw}'"); break
        for kw in BLOCK_KEYWORDS:
            if kw in page_text:
                result["issues"].append(f"Bot-block signal: '{kw}'"); break
        for kw in COPYRIGHT_KEYWORDS:
            if kw in page_text:
                result["issues"].append(f"Copyright signal: '{kw}'"); break

        total_text = " ".join(p.get_text(strip=True) for p in soup.find_all("p"))
        if len(total_text) < 200:
            result["issues"].append("Very little extractable text (<200 chars)")

    except requests.exceptions.Timeout:
        result["issues"].append("Request timed out")
    except requests.exceptions.ConnectionError:
        result["issues"].append("Connection error — site unreachable")
    except Exception as e:
        result["issues"].append(f"Unexpected error: {e}")

    result["accessible"] = len(result["issues"]) == 0
    return result


def extract_article_text(url: str) -> str:
    """Fetch and extract main article body text from a URL."""
    headers  = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, timeout=12)
    soup     = BeautifulSoup(response.content, "html.parser")

    for tag in ["field--name-body", "article-body", "field-body",
                "entry-content", "node__content"]:
        body = soup.find("div", class_=lambda c: c and tag in c)
        if body:
            return body.get_text(separator="\n", strip=True)

    return "\n".join(
        p.get_text(strip=True) for p in soup.find_all("p") if p.get_text(strip=True)
    )


def is_usable(row) -> bool:
    """Strict: block on any hard issue including copyright."""
    issues = row['issues'] if isinstance(row['issues'], list) else []
    has_hard_block = any(any(b in issue for b in HARD_BLOCKS) for issue in issues)
    return (row['status_code'] == 200) and not has_hard_block


def is_usable_lenient(row) -> bool:
    """Lenient: allow copyright signal — block only hard HTTP/robots issues."""
    issues = row['issues'] if isinstance(row['issues'], list) else []
    has_hard_block = any(
        any(b in issue for b in HARD_BLOCKS_NO_COPYRIGHT)
        for issue in issues
    )
    return (row['status_code'] == 200) and not has_hard_block


def safe_extract(url: str, pre_check: bool = True, delay: float = 1.0) -> dict:
    """
    Optionally run an accessibility pre-check, then extract article text.
    Returns dict with: url, text, accessible, issues, status_code.
    """
    time.sleep(delay)
    out = {"url": url, "text": None, "accessible": None, "issues": [], "status_code": None}

    if pre_check:
        check              = check_url_accessibility(url)
        out["issues"]      = check["issues"]
        out["status_code"] = check["status_code"]
        if any(any(b in issue for b in HARD_BLOCKS) for issue in check["issues"]):
            out["accessible"] = False
            out["text"]       = f"SKIPPED — {'; '.join(check['issues'])}"
            return out
    try:
        out["text"]       = extract_article_text(url)
        out["accessible"] = True
    except Exception as e:
        out["text"]       = f"ERROR: {e}"
        out["accessible"] = False
        out["issues"].append(str(e))

    return out


# ── Batch scraping ────────────────────────────────────────────────────────────

def scrape_and_report(top_five_df: pd.DataFrame, n: int = 10,
                      delay: float = 0.5) -> tuple:
    """
    Sample n most-recent articles per source, scrape, and return:
        sample_df      — full results with usable flag
        report         — per-source accessibility summary
        usable_sources — list of usable source_grouped values
    """
    # pandas 2.x: groupby().apply() can drop the group-key column from the
    # result even with group_keys=False. Use explicit concat to be safe.
    recent = (
        top_five_df
        .sort_values('SQLDATE', ascending=False)
        .groupby('source_grouped', group_keys=False)
        .head(100)
    )
    sample_df = pd.concat(
        [grp.sample(min(n, len(grp))) for _, grp in recent.groupby('source_grouped')],
        ignore_index=True,
    )
    print(f"Total articles to scrape: {len(sample_df)}")
    print(sample_df.groupby('source_grouped').size().rename('n_articles'))

    tqdm.pandas(desc="Scraping", unit="article")
    results   = sample_df['SOURCEURL'].progress_apply(
        lambda url: safe_extract(url, pre_check=True, delay=delay)
    )
    sample_df = pd.concat([sample_df, pd.DataFrame(results.tolist())], axis=1)

    def _source_report(grp):
        total      = len(grp)
        accessible = grp['accessible'].sum()
        all_issues = grp['issues'].explode().dropna()
        all_issues = all_issues[all_issues != '']
        top_issue  = all_issues.value_counts().idxmax() if len(all_issues) else "none"
        return pd.Series({
            'total':        total,
            'accessible':   int(accessible),
            'skipped':      int(total - accessible),
            'success_rate': f"{accessible / total * 100:.0f}%",
            'top_issue':    top_issue,
            'status_codes': grp['status_code'].value_counts().to_dict(),
        })

    report         = sample_df.groupby('source_grouped').apply(_source_report).reset_index()
    sample_df['usable'] = sample_df.apply(is_usable, axis=1)
    usable_sources = sample_df[sample_df['usable']]['source_grouped'].unique().tolist()

    print("\n── Scraping report ─────────────────────────────────────────────────")
    print(report.to_string(index=False))
    poor = report[report['accessible'] < report['total'] * 0.5]
    print(f"\n[WARNING] Sources with <50% success: {poor['source_grouped'].tolist()}" if len(poor)
          else "\n[OK] All sources above 50% accessibility")
    print(f"\nUsable articles : {sample_df['usable'].sum()} / {len(sample_df)}")
    print(f"Usable sources  : {usable_sources}")

    return sample_df, report, usable_sources


def scrape_peak_articles(peak_df: pd.DataFrame, adm1: str,
                         year_month: str, source: str,
                         delay: float = 0.5) -> pd.DataFrame:
    """Scrape full article text for a specific ADM1 × year_month × source slice."""
    urls = (
        peak_df[
            (peak_df['ADM1_EN']        == adm1) &
            (peak_df['year_month']     == year_month) &
            (peak_df['source_grouped'] == source)
        ][['SOURCEURL']]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    print(f"[{adm1} | {year_month} | {source}] {len(urls)} URLs")

    tqdm.pandas(desc=f"{adm1} {year_month}", unit="article")
    results   = urls['SOURCEURL'].progress_apply(
        lambda url: safe_extract(url, pre_check=True, delay=delay)
    )
    result_df = pd.concat([urls, pd.DataFrame(results.tolist())], axis=1)
    result_df['usable'] = result_df.apply(is_usable_lenient, axis=1)

    print(f"Usable: {result_df['usable'].sum()} / {len(result_df)}")
    return result_df
