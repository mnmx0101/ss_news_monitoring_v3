# South Sudan News Analytics Platform -- User Guide

**For IPC Analysts**

This guide walks you through the intended workflow for using the dashboard to contextualize your food security analysis. The platform is organized around a simple analytical logic: observe general trends, identify anomalies, drill into the articles that matter, and generate AI-assisted summaries with proper sourcing.

---

## Table of Contents

1. [Overview and Data Sources](#1-overview-and-data-sources)
2. [Recommended Workflow](#2-recommended-workflow)
3. [Page-by-Page Guide](#3-page-by-page-guide)
4. [Known Limitations](#4-known-limitations)
5. [Best Practices](#5-best-practices)

---

## 1. Overview and Data Sources

The platform aggregates news articles from three sources covering South Sudan:

| Source | Type | URL |
|--------|------|-----|
| AllAfrica.com | Aggregator | https://allafrica.com/ |
| Eye Radio | USAID-funded outlet | https://www.eyeradio.org/ |
| Radio Tamazuj | Independent outlet | https://www.radiotamazuj.org/en/news |

Each article has been georeferenced to Admin Level 1 (state) and Admin Level 2 (county) and labeled by topic using a keyword-based taxonomy derived from World Bank research outputs.

---

## 2. Recommended Workflow

The dashboard is designed to support a sequential analytical process:

**Step A: Understand what the data looks like (Dataset Overview)**
Start by examining general trends in article volume across topics. This gives you a baseline understanding of how much coverage each humanitarian theme is receiving and whether coverage is rising or falling.

**Step B: Identify periods and places with abnormal coverage (ADM1 and ADM2 Insights)**
Use the alert and alarm heatmaps to pinpoint specific regions and time periods where article volume is unusually high relative to historical norms. These anomalies often correspond to emerging crises, escalating situations, or significant events that warrant closer investigation.

**Step C: Read the actual articles (Article Browser)**
Once you have identified a region-time-topic combination of interest, filter down to the relevant articles. Read through them to understand what is driving the signal.

**Step D: Generate a structured summary (RAG+LLM Summary)**
For a given topic and geographic focus, use the AI-powered summary tool to produce a concise, source-cited situation brief. This is especially useful when there are too many articles to read individually, or when you need to quickly communicate findings to colleagues.

---

## 3. Page-by-Page Guide

### Page 1: Dataset Overview

**Purpose**: Get a high-level picture of article volume and topic distribution.

**What to look for**:
- The total article count trend shows whether media coverage of South Sudan is increasing or decreasing overall.
- The per-label subplots show the trend for each topic independently. Each subplot includes two reference lines:
  - The **full-span mean** (red dotted line) represents the average monthly article count across the entire dataset.
  - The **12-month rolling mean** (orange dashed line) captures recent momentum and is useful for spotting sustained shifts in coverage.
- The Label-by-Region heatmaps (ADM1 and ADM2) reveal which geographic areas receive the most coverage for each topic.

**Filters available**: Source, Date range.

---

### Page 2: ADM1 Insights (State Level)

**Purpose**: Identify states where article volume for a given topic is abnormally high.

**How alerts work**:
- For each state-month combination, the article count is compared against that state's historical distribution.
- **Normal**: The count is within 1 standard deviation of the mean.
- **Alert-high**: The count is 1 to 2 standard deviations above the mean.
- **Alarm-high**: The count exceeds 2 standard deviations above the mean.

**Two thresholds per label**:
The page shows side-by-side heatmaps for each topic label:
- **Static threshold**: Mean and standard deviation are computed over the full time span. This captures absolute deviations from the long-run norm.
- **Dynamic threshold**: Mean and standard deviation are computed over the trailing 12 months before each time point. This captures deviations relative to recent trends, which is more useful when overall article volume is growing.

**Default filters**: Radio Tamazuj source, Negative sentiment, full date range. These defaults reflect the most common analytical use case: tracking negative events reported by an independent source.

---

### Page 3: ADM2 Insights (County Level)

**Purpose**: Same logic as ADM1 but at the county level for more granular monitoring.

**Key differences from ADM1**:
- Includes an ADM1 geographic filter to narrow down which counties are shown (defaults to Central Equatoria).
- Counties labeled "Unknown County" are excluded.
- A summary table at the bottom ranks counties by the number of alarm-high months, which helps prioritize further investigation.

**Important note**: At the county level, article counts per month tend to be small, which makes the statistical thresholds less stable. The alert and alarm signals here are best treated as screening indicators rather than definitive flags. Use the RAG+LLM summary (Page 5) to extract deeper, region-specific insights.

---

### Page 4: Article Browser

**Purpose**: Search, filter, and read individual articles.

**How to use it**:
1. Set your filters in the sidebar. The defaults (Radio Tamazuj, Negative sentiment, Political Instability label, Central Equatoria) are a useful starting point, but adjust them based on what you found in the earlier pages.
2. Use the dropdown to select an article from the filtered set.
3. The article is displayed with full metadata: date, source, region, county, topic label, sentiment classification, and a link to the original source.
4. The cleaned text is shown by default. The original text is not displayed to respect copyright, but you can follow the link to read it on the source website.

**Tip**: Use the keyword search filter if you are looking for something specific, such as a place name or event type.

---

### Page 5: RAG+LLM Situation Summary

**Purpose**: Generate an AI-written situation brief based on a filtered set of articles.

**Two-step process**:

1. **Step 1 -- Estimate tokens and cost**: After setting your filters and configuration, click the "Estimate" button. This will show you how many articles will be analyzed, the estimated number of input and output tokens, and the approximate cost for the selected model. Review this before proceeding.

2. **Step 2 -- Generate summary**: Click the "Generate" button to produce the summary. The output includes:
   - Bullet points summarizing key findings, each citing article numbers in square brackets (e.g., [1], [3,5]).
   - An overall summary paragraph.
   - A reference table listing all source articles with dates, locations, labels, and links.

**Configuration options**:
- **Focus Topic/Keyword**: Narrows the article retrieval to those most relevant to your query.
- **Region/District Focus**: Instructs the AI to center its analysis on a specific geographic area.
- **Model selection**: gpt-4o-mini is the most cost-effective; gpt-4o produces higher-quality output at higher cost.

---

## 4. Known Limitations

Please keep the following limitations in mind when interpreting results from this platform:

### Article Labels Are Approximate
The topic labels (Conflict and Violence, Food Crisis, Political Instability, etc.) are assigned using a keyword-based taxonomy adapted from the following research:

> Ananth Balashankar et al., Predicting food crises using news streams. *Sci. Adv.* 9, eabm3449 (2023). DOI: 10.1126/sciadv.abm3449

The process works by georeferencing each article and then scanning the relevant text segments around each geolocation for topic keywords (lemmatized unigrams). This approach is practical and scalable, but it will produce some false positives (articles labeled with a topic they do not substantively cover) and false negatives (relevant articles missed because they use different vocabulary).

### Rising Baseline in Article Volume
The overall volume of articles in the dataset is increasing over time across most topics. This means that the static threshold (full-span mean) will tend to flag more recent periods as alerts or alarms simply because there are more articles being published. The dynamic threshold (12-month rolling mean) partially addresses this by comparing each period against only the recent past. In general, this tool is most useful for **forward-looking analysis**: identifying periods where coverage spikes beyond what recent history would predict.

### ADM2 Insights Require Supplementation
At the county level, the number of articles per month can be quite small, which makes statistical anomaly detection less reliable. The heatmaps on the ADM2 page should be treated as an initial screening tool. For substantive county-level insights, use the RAG+LLM summary page with a region/district focus to extract specific narrative context from the articles.

### Source Differences
The three news sources have different editorial orientations, geographic coverage, and publication volumes. Patterns that appear in one source may not appear in another, and vice versa. A spike in articles about a topic in Radio Tamazuj does not necessarily mean that Eye Radio or AllAfrica are reporting the same trend. See the Best Practices section below for guidance on cross-checking.

### LLM Cost
The RAG+LLM summary feature uses the OpenAI API, which incurs token-based costs. The default configuration uses a shared API key. Please use the cost estimation feature (Step 1) before generating summaries, and be mindful of how many articles you include in each query. The gpt-4o-mini model is recommended for routine use due to its lower cost.

---

## 5. Best Practices

1. **Start broad, then narrow down.** Begin with the Dataset Overview to understand the landscape, then use ADM1/ADM2 insights to find specific anomalies, and finally drill into articles and summaries for those specific areas.

2. **Explore by source, then cross-check.** Filter by one source at a time to understand each outlet's coverage pattern. If you see something noteworthy in Radio Tamazuj, check whether AllAfrica or Eye Radio are reporting similar trends. Convergence across sources strengthens the signal; divergence may indicate source bias or localized reporting.

3. **Use dynamic thresholds for recent periods.** When analyzing the most recent months, the dynamic (12-month rolling) threshold is more reliable than the static (full-span) threshold, especially given the rising baseline in article volume.

4. **Set a region focus for LLM summaries.** The Region/District Focus field in the RAG+LLM page significantly improves the relevance of generated summaries. Without it, the AI may produce a broad, unfocused overview. With it, the summary will specifically address events and conditions in the named area.

5. **Treat labels as screening categories.** Do not assume that all articles under a given label are equally relevant, or that the label system captures all relevant articles. When precision matters, use the Article Browser to read the actual texts.

6. **Keep token costs in mind.** Always run the cost estimation before generating a summary. For routine analysis, the gpt-4o-mini model with 15 articles is a good balance of quality and cost.

---

*This guide was prepared for IPC analysts working on South Sudan. For technical questions about the platform, refer to the README_SETUP.md file in the project directory.*
