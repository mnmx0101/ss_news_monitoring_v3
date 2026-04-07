"""
llm.py
======
LLM-based conflict summarization using the OpenAI API.

Functions
---------
- inspect_articles(result_df)                        : print per-article text stats
- prepare_texts(result_df, max_chars, max_total)     : concatenate usable article texts
- summarize_conflict(result_df, adm1, ym, source, …) : generate structured JSON summary
"""

import json
import re
import os

import pandas as pd
from openai import OpenAI

MODEL              = "gpt-4o-mini"
JSON_FORMAT_MODELS = {"gpt-4o", "gpt-4o-mini", "gpt-4-turbo"}

SYSTEM_PROMPT = """You are a humanitarian analyst specializing in South Sudan conflict monitoring.
Analyze news articles and extract conflict-related information.
Focus on geographic specificity — identify which ADM1 states and ADM2 counties/towns are affected.
Output JSON only. No preamble. No markdown."""


def _get_client(api_key: str = None) -> OpenAI:
    """Return an OpenAI client, using provided key or loading from environment."""
    if not api_key:
        api_key = os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        raise EnvironmentError(
            "OPENAI_API_KEY not found. Please provide an API key."
        )
    return OpenAI(api_key=api_key)


def inspect_articles(result_df: pd.DataFrame) -> tuple:
    """
    Print per-article character and word counts before an LLM call.

    Returns
    -------
    (stats_df, total_chars)
    """
    usable = result_df[result_df['usable'] & result_df['text'].notna()].copy()
    rows = []
    for _, row in usable.iterrows():
        text = row['text'].strip()
        rows.append({
            'url':     row['SOURCEURL'],
            'n_chars': len(text),
            'n_words': len(text.split()),
        })

    stats_df    = pd.DataFrame(rows)
    total_chars = stats_df['n_chars'].sum()

    print(f"Usable articles  : {len(stats_df)}")
    print(f"Total chars      : {total_chars:,}")
    print(f"Total words      : {stats_df['n_words'].sum():,}")
    print(f"Avg chars/article: {stats_df['n_chars'].mean():,.0f}")
    print()
    print(stats_df[['url', 'n_chars', 'n_words']].to_string(index=False))

    return stats_df, total_chars


def prepare_texts(result_df: pd.DataFrame,
                  max_chars_per_article: int = None,
                  max_total_chars:       int = None) -> tuple:
    """
    Concatenate all usable article texts into one string.
    Optionally cap at max_chars_per_article and/or max_total_chars.

    Returns
    -------
    (aggregated_text, n_usable, n_included)
    """
    usable   = result_df[result_df['usable'] & result_df['text'].notna()].copy()
    chunks   = []
    total    = 0
    n_usable = len(usable)

    for _, row in usable.iterrows():
        text = row['text'].strip()
        if max_chars_per_article:
            text = text[:max_chars_per_article]
        chunk = f"--- Article: {row['SOURCEURL']} ---\n{text}"
        if max_total_chars and total + len(chunk) > max_total_chars:
            print(f"  [WARNING] max_total_chars={max_total_chars:,} reached -- stopping at {len(chunks)} articles")
            break
        chunks.append(chunk)
        total += len(chunk)

    n_included = len(chunks)
    print(f"Articles included: {n_included} / {n_usable} | Total chars: {total:,}")
    return "\n\n".join(chunks), n_usable, n_included


def summarize_conflict(result_df: pd.DataFrame,
                       adm1:       str,
                       year_month: str,
                       source:     str,
                       model:      str = MODEL,
                       max_tokens: int = 1500,
                       api_key:    str = None) -> dict | None:
    """
    Feed aggregated article text to OpenAI and return a structured JSON
    conflict summary for a given ADM1 × year_month × source slice.

    Returns None if there is no usable text to summarize.
    """
    client = _get_client(api_key=api_key)
    aggregated_text, n_usable, n_included = prepare_texts(result_df)

    if not aggregated_text:
        print("No usable text to summarize.")
        return None

    user_prompt = f"""Summarize conflict-related issues from these South Sudan news articles.

Context:
- ADM1 region  : {adm1}
- Period       : {year_month}
- Source       : {source}

Articles:
{aggregated_text}

Return JSON with exactly these fields:
{{
  "adm1_region"     : "{adm1}",
  "period"          : "{year_month}",
  "source"          : "{source}",
  "overall_summary" : "3-4 sentence summary of main conflict dynamics",
  "key_events"      : ["list of specific events with dates if available"],
  "adm2_affected"   : [
      {{
        "name"        : "county or town name",
        "description" : "what happened there"
      }}
  ],
  "actors"          : ["armed groups, government forces, militias mentioned"],
  "humanitarian"    : "displacement, casualties, food security impacts if mentioned",
  "severity"        : "one of: low, medium, high, critical"
}}"""

    kwargs = dict(
        model      = model,
        max_tokens = max_tokens,
        messages   = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_prompt},
        ],
    )
    if model in JSON_FORMAT_MODELS:
        kwargs["response_format"] = {"type": "json_object"}

    response = client.chat.completions.create(**kwargs)
    raw      = response.choices[0].message.content

    try:
        summary = json.loads(raw)
    except json.JSONDecodeError:
        match   = re.search(r'\{.*\}', raw, re.DOTALL)
        summary = json.loads(match.group()) if match else {"raw": raw}

    summary['n_articles_usable']   = n_usable
    summary['n_articles_included'] = n_included
    summary['source_urls']         = list(result_df['SOURCEURL'].unique())
    summary['generated_prompt']    = user_prompt

    usage = response.usage
    print(f"Model: {model} | Tokens -- prompt: {usage.prompt_tokens} | "
          f"completion: {usage.completion_tokens} | total: {usage.total_tokens}")

    return summary
