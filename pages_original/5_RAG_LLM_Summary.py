"""
Page 5: RAG+LLM Situation Summary
Two-step process: (1) Estimate tokens and cost, (2) Generate summary.
Summary includes bullet points with article links and a complete narrative.
"""

import streamlit as st
import pandas as pd
import numpy as np
import re
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv("utils/.env")

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_loader import load_data
from utils.filters import (
    render_source_filter, render_date_filter, render_sentiment_filter,
    render_label_filter, render_adm1_filter, render_adm2_filter,
    apply_filters, render_summary_metrics
)


st.title("RAG+LLM Situation Summary")
st.markdown("Generate AI-powered situation summaries in two steps: **estimate cost**, then **generate summary**.")

# Pricing (per 1M tokens, USD)
MODEL_PRICING = {
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-4o":      {"input": 2.50, "output": 10.00},
    "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
}


def estimate_tokens(text):
    """Rough token estimation (~4 chars per token for English)."""
    return len(str(text)) // 4


def get_openai_client(user_api_key=None):
    """Initialize OpenAI client."""
    api_key = user_api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None, "Missing OpenAI API Key. Please provide one below or set it in your .env file."
    try:
        import openai
        openai.api_key = api_key
        return openai, None
    except Exception as e:
        return None, f"OpenAI init failed: {e}"


def keyword_score(text, query_terms):
    """Score text by keyword frequency."""
    t = (text or "").lower()
    return sum(t.count(q) for q in query_terms if q)


def retrieve_top_k(df, query, top_k=15):
    """Retrieve top-k relevant articles based on keyword matching."""
    if df.empty:
        return df
    query = (query or "").strip()
    if not query:
        return df.sort_values("date", ascending=False).head(top_k)
    q_terms = [t.lower() for t in re.findall(r"[A-Za-z0-9_]+", query) if len(t) >= 3]
    if not q_terms:
        return df.sort_values("date", ascending=False).head(top_k)
    scored = df.copy()
    scored["_score"] = scored.apply(
        lambda r: keyword_score(
            str(r.get("title", "")) + " " + str(r.get("paragraphs", "")),
            q_terms
        ),
        axis=1
    )
    return scored.sort_values(["_score", "date"], ascending=[False, False]).head(top_k)


def build_prompt(context_df, context_str, date_range, region_focus, topic_keyword):
    """Build the LLM prompt from retrieved articles with strict filtering."""
    docs = []
    for i, (_, r) in enumerate(context_df.iterrows()):
        url = r.get("url", "")
        url_str = f" | URL: {url}" if url and not pd.isna(url) else ""
        docs.append(
            f"[{i+1}] Date: {r['date'].strftime('%Y-%m-%d')} | "
            f"Region: {r['adm1_name_final']} | County: {r['adm2_name_final']} | "
            f"Label: {r['Label']} | "
            f"Title: {r['title']}{url_str}\n"
            f"Text: {str(r.get('paragraphs', ''))}"
        )
    docs_text = "\n\n".join(docs)

    # Build strict filtering instructions
    filter_requirements = []
    if region_focus and region_focus.strip():
        filter_requirements.append(f"Region/Location: **{region_focus.strip()}**")
    if topic_keyword and topic_keyword.strip():
        filter_requirements.append(f"Topic/Keyword: **{topic_keyword.strip()}**")
    
    strict_filter_instruction = ""
    if filter_requirements:
        filter_list = "\n".join([f"  - {req}" for req in filter_requirements])
        strict_filter_instruction = f"""
🚨 STRICT FILTERING REQUIREMENTS 🚨
You MUST ONLY include information that matches ALL of the following criteria:
{filter_list}
MATCHING RULES (FLEXIBLE):
- Use CASE-INSENSITIVE matching (e.g., "Juba" matches "juba", "JUBA", "Juba")
- Use PARTIAL matching (e.g., "Juba" matches "Juba County", "near Juba", "Juba area", "Juba region")
CRITICAL RULES:
1. If an article does NOT contain the specified region/location name (case-insensitive), DO NOT summarize it.
2. Only use FACTS explicitly stated in the articles - NO speculation, NO inference, NO assumptions.
"""
    else:
        strict_filter_instruction = """
CRITICAL RULES:
1. Only use FACTS explicitly stated in the articles - NO speculation, NO inference, NO assumptions.
"""

    prompt = f"""You are a humanitarian crisis analyst. Based ONLY on the following news reports from Radio Tamazuj,
provide a situation summary.
Focus Context: {context_str}
Time Period: {date_range[0]} to {date_range[1]}
{strict_filter_instruction}
REPORTS:
{docs_text}
INSTRUCTIONS:
1. Provide 5-10 bullet points from the articles, summarizing key findings or events.
2. For EACH bullet point, you MUST cite the source article number(s) inline in square brackets at the end of the sentence, e.g. [1] or [3, 5].
3. After the bullet points, provide a 2-3 sentence overall summary paragraph.
4. Cite specific dates and locations when mentioned.
5. Do NOT list excluded articles.
FORMAT:
* **Key Finding**: Description of the finding here. [1]
* ...
**Overall Summary**: ...
"""
    return prompt, docs_text


# Load data
df = load_data()
df = df[df["retrieve_source"] == "radiotamazuj"].copy()

# Sidebar filters
st.sidebar.header("Scoping Filters")
st.sidebar.info("These filters determine which articles the AI will analyze. Note: All data is from Radio Tamazuj.")

sentiments = render_sentiment_filter(df, "p5")
date_range = render_date_filter(df, "p5")
labels = render_label_filter(df, "p5")

st.sidebar.markdown("---")
st.sidebar.subheader("Geographic Scope")
adm1 = render_adm1_filter(df, "p5")
adm2 = render_adm2_filter(df, adm1_selection=adm1, key_prefix="p5")

# Apply filters
filtered_df = apply_filters(
    df, sources=["radiotamazuj"], date_range=date_range,
    sentiments=sentiments, labels=labels, adm1=adm1, adm2=adm2
)

# Summary metrics
render_summary_metrics(filtered_df)

st.markdown("---")

# Configuration
st.subheader("Summary Configuration")

col1, col2 = st.columns(2)
with col1:
    api_key = st.text_input(
        "OpenAI API Key (Leave blank to use system key)",
        type="password",
        key="p5_api_key"
    )
with col2:
    topic_keyword = st.text_input(
        "Focus Topic/Keyword",
        placeholder="e.g., food security, conflict, flooding",
        key="p5_topic"
    )

col3, col4, col5 = st.columns(3)
with col3:
    top_k = st.slider("Number of articles to analyze", 5, 50, 15, key="p5_topk")
with col4:
    model = st.selectbox(
        "Model",
        ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
        index=0,
        key="p5_model"
    )
with col5:
    region_focus = st.text_input(
        "Region/District Focus",
        placeholder="e.g., Juba, Bor South, Malakal",
        help="Focus the summary on this specific area.",
        key="p5_region_focus"
    )

st.markdown("---")

# Step 1: Estimate Tokens and Cost
st.subheader("Step 1: Estimate Tokens and Cost")

if st.button("Estimate Input Tokens and Cost", key="p5_estimate"):
    if filtered_df.empty:
        st.error("No articles match your filters.")
    else:
        context_df = retrieve_top_k(filtered_df, topic_keyword, top_k)

        if context_df.empty:
            st.warning("Not enough articles found.")
        else:
            context_parts = ["Source: Radio Tamazuj"]
            if labels:
                context_parts.append(f"Labels: {', '.join(labels[:3])}")
            if topic_keyword:
                context_parts.append(f"Topic: {topic_keyword}")
            context_str = "; ".join(context_parts) if context_parts else "General coverage"

            prompt, docs_text = build_prompt(context_df, context_str, date_range, region_focus, topic_keyword)

            input_tokens = estimate_tokens(prompt) + 200  # Increased buffer for full text
            output_tokens_est = 1500  # Increased for more comprehensive summaries

            pricing = MODEL_PRICING.get(model, {"input": 0, "output": 0})
            input_cost = (input_tokens / 1_000_000) * pricing["input"]
            output_cost = (output_tokens_est / 1_000_000) * pricing["output"]
            total_cost = input_cost + output_cost

            st.session_state["p5_context_df"] = context_df
            st.session_state["p5_prompt"] = prompt
            st.session_state["p5_context_str"] = context_str
            st.session_state["p5_estimated"] = True

            st.success(f"Estimation complete -- {len(context_df)} articles selected.")

            ecol1, ecol2, ecol3, ecol4 = st.columns(4)
            with ecol1:
                st.metric("Articles Selected", f"{len(context_df):,}")
            with ecol2:
                st.metric("Est. Input Tokens", f"~{input_tokens:,}")
            with ecol3:
                st.metric("Est. Output Tokens", f"~{output_tokens_est:,}")
            with ecol4:
                st.metric("Est. Cost", f"${total_cost:.4f}")

            st.info(f"**Model**: {model}  |  **Pricing**: ${pricing['input']}/1M input, ${pricing['output']}/1M output")

            with st.expander(f"Articles to be analyzed ({len(context_df)})", expanded=False):
                for i, (_, r) in enumerate(context_df.iterrows()):
                    url = r.get("url", "")
                    link = f" -- [link]({url})" if url and not pd.isna(url) else ""
                    st.markdown(
                        f"**[{i+1}]** {r['date'].strftime('%Y-%m-%d')} | "
                        f"{r['adm1_name_final']} > {r['adm2_name_final']} | "
                        f"{r['title'][:80]}{link}"
                    )

st.markdown("---")

# Step 2: Generate Summary
st.subheader("Step 2: Generate Summary")

if not st.session_state.get("p5_estimated"):
    st.info("Please run **Step 1** first to estimate tokens and cost before generating.")
else:
    if st.button("Generate Situation Summary", type="primary", key="p5_generate"):
        client, err = get_openai_client(api_key)

        if err:
            st.error(f"{err}")
        else:
            context_df = st.session_state.get("p5_context_df", pd.DataFrame())
            prompt = st.session_state.get("p5_prompt", "")
            context_str = st.session_state.get("p5_context_str", "")

            if context_df.empty or not prompt:
                st.error("No data available. Please re-run Step 1.")
            else:
                with st.spinner("Generating summary from selected articles..."):
                    try:
                        response = client.ChatCompletion.create(
                            model=model,
                            messages=[
                                {
                                    "role": "system",
                                    "content": "You are a careful crisis analyst. Provide factual, concise summaries based only on provided documents. When a specific region or district is provided as the focus, ensure all analysis centers on that location. Always cite article numbers in [brackets] for each bullet point."
                                },
                                {"role": "user", "content": prompt}
                            ],
                            max_tokens=1500,  # Increased for full article text
                            temperature=0.3
                        )

                        summary = response.choices[0].message.content

                        usage = response.get("usage", {})
                        if usage:
                            ucol1, ucol2, ucol3, ucol4 = st.columns(4)
                            actual_input = usage.get("prompt_tokens", 0)
                            actual_output = usage.get("completion_tokens", 0)
                            actual_total = usage.get("total_tokens", 0)
                            pricing = MODEL_PRICING.get(model, {"input": 0, "output": 0})
                            actual_cost = (actual_input / 1_000_000) * pricing["input"] + (actual_output / 1_000_000) * pricing["output"]

                            with ucol1:
                                st.metric("Prompt Tokens", f"{actual_input:,}")
                            with ucol2:
                                st.metric("Completion Tokens", f"{actual_output:,}")
                            with ucol3:
                                st.metric("Total Tokens", f"{actual_total:,}")
                            with ucol4:
                                st.metric("Actual Cost", f"${actual_cost:.4f}")

                        st.success("Summary generated successfully.")

                        st.markdown("### Situation Summary")
                        if region_focus:
                            st.markdown(f"*Focused on: **{region_focus.strip()}***")
                        st.markdown(summary)

                        st.markdown("### Key source article References")
                        
                        # Parse cited article indices from the summary text
                        cited_indices = set()
                        for m in re.finditer(r'\[([0-9\s,]+)\]', summary):
                            nums = [x.strip() for x in m.group(1).split(',')]
                            for n in nums:
                                if n.isdigit():
                                    cited_indices.add(int(n))

                        ref_data = []
                        for i, (_, r) in enumerate(context_df.iterrows()):
                            idx = i + 1
                            if idx in cited_indices:
                                url = r.get("url", "")
                                link = url if url and not pd.isna(url) else "N/A"
                                ref_data.append({
                                    "#": idx,
                                    "Date": r["date"].strftime("%Y-%m-%d"),
                                    "Region": r["adm1_name_final"],
                                    "County": r["adm2_name_final"],
                                    "Label": r["Label"],
                                    "Title": r["title"][:60],
                                    "URL": link
                                })
                        
                        if ref_data:
                            ref_df = pd.DataFrame(ref_data)
                            st.dataframe(ref_df, use_container_width=True, hide_index=True)
                        else:
                            st.info("No explicit source citations in the format `[1]` were found in the summary text.")

                    except Exception as e:
                        st.error(f"LLM Error: {e}")