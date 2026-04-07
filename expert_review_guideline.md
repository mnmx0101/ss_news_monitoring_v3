# Expert Review Guideline: South Sudan News Analytics Platform (V3)

**Prepared for**: IPC Analysts and Food Security Practitioners  
**Platform**: South Sudan News Analytics Platform (V3)  
**Data Source**: [Radio Tamazuj](https://www.radiotamazuj.org/en/about-us)

---

## Purpose

This guideline supports systematic review of news-derived signals against known humanitarian ground truth. It is structured as a sequential analytical workflow with four distinct validation layers, progressing from national-level patterns to county-level incidents and source-level confirmation.

---

## Tool Overview: Tab-by-Tab Reference

### Home

**What it shows**: Dataset description, keyword taxonomy, data coverage visualizations, and key limitations.

**How to use it**:
1. Review the **Keyword Taxonomy** table to understand how topics are assigned. Misclassification at this stage propagates through all downstream signals.
2. Examine the **Topic Coverage Bar Chart**: topics in **green** meet the 30% adequacy threshold. Topics in **red** are structurally under-reported — treat their signals with extra caution baseline.
3. Review the **Worst-Covered Counties** bar chart to identify geographic blind spots before beginning analysis.
4. Read the **Key Limitations** section before interpreting any alert or alarm. Pay particular attention to the georeferencing caveat — county-level attribution is subject to NER false positives and negatives.

---

### National Overview

**What it shows**: ADM1 (state) and ADM2 (county) heatmaps of article volume anomaly status for a selected topic, metric, and time window.

**How to use it**:
1. Begin here to identify **which states or counties** are currently showing elevated signals.
2. Select a **Topic** of interest (e.g., Food Crisis, Conflict and Violence).
3. Switch between the **ADM1** and **ADM2** tabs to move from macro to micro spatial resolution.
4. Use the **Tone** and **Metric** filters to narrow to negative-sentiment articles or article volume.
5. States or counties showing sustained **orange (Alert)** or **red (Alarm)** patterns across multiple consecutive months are the highest-priority candidates for deeper investigation.

**Validation check at this stage**:
- Are the flagged states consistent with current IPC Phase classifications?
- Are alert patterns concentrated in known crisis-affected areas, or are they appearing in unexpected locations (which may indicate data artifacts)?

---

### ADM1 Insights (State Level)

**What it shows**: A longitudinal line chart of monthly article volume (or sentiment intensity) for a selected state and topic, with threshold bands overlaid. A method-level consensus heatmap is shown below the chart.

**How to use it**:
1. Select the **State** and **Topic** from the sidebar.
2. Enable **multiple threshold methods** (Percentile, Tukey Fence, Z-Score) simultaneously using the multiselect control.
3. Examine the **consensus engine output**: months where 2 or more methods simultaneously flag an Alert or Alarm represent the strongest anomaly signals.
4. Use the **Method × Month Breakdown Heatmap** below the chart to trace precisely which methods triggered in each month, and assess whether methods agree (all red) or diverge (mixed colors).
5. A divergence between methods may indicate borderline anomalies; convergence across all three methods constitutes a robust crisis signal.

**Recommended parameter settings for validation**:
- Alert percentile: **p75** (default)
- Alarm percentile: **p90** (default)
- Min History (N): **12 months** to ensure stable local baselines

**Validation check at this stage**:
- Do alarm months correspond to known events in your IPC records or situational reports?
- Are alarm patterns seasonal (cyclical flooding, harvest cycles) or event-driven?

---

### ADM2 Insights (County Level)

**What it shows**: Same structure as ADM1 Insights, but at county (ADM2) level. Includes the method × month breakdown heatmap.

**How to use it**:
1. Select the **County** and **Topic** from the sidebar.
2. Note the **Observed Months** metric — counties with very low counts are operating on national fallback thresholds (flagged with a warning).
3. Apply the same multi-method consensus approach as at ADM1 level.
4. Use this page **after** identifying priority states in the National Overview — do not begin analysis at ADM2 level without a prior ADM1 filter, as county-level statistical noise is higher.

**Validation check at this stage**:
- Does the county-level alarm pattern corroborate the state-level finding?
- Can it be linked to a specific documented event in the Validation Reference?

---

### Validation Reference

**What it shows**: An editable, searchable table of historical IPC-documented events at state and county level, organized by topic and time period. Sourced from published IPC reports.

**How to use it**:
1. Filter by **ADM1**, **ADM2**, **topic**, or **event type** to locate relevant ground-truth events.
2. Cross-reference the dates of documented IPC events against the alarm months identified in ADM1/ADM2 Insights.
3. If a documented event aligns temporally with an anomaly signal, this constitutes **positive validation**.
4. If an alarm has no matching ground-truth event, investigate further before treating it as a true positive — it may reflect a media reporting spike, NER misclassification, or a real crisis not yet documented.
5. Add new events to the table using the editable rows at the bottom. Click **Save Changes** to persist entries to the project CSV.

---

### RAG+LLM Summary

**What it shows**: An AI-generated situational intelligence summary based on the most relevant Radio Tamazuj articles for a selected topic, geographic focus, and time window.

**How to use it**:
1. Set the **Topic**, **Region/District Focus**, and **Date Range** to match the anomaly identified in ADM1/ADM2 Insights.
2. Generate the summary to retrieve a concise briefing with **inline citations** (e.g., [1], [3]).
3. Review the **Key Source Article References** table — only articles explicitly cited in the summary are shown. Follow source URLs to read original reporting for verification.
4. Use the generated summary to understand the **narrative driver** behind an anomaly: whether it reflects conflict events, displacement, weather shock, food price spikes, or is an artifact of reporting frequency.

**Validation check at this stage**:
- Does the LLM summary confirm the same events flagged by the threshold engine?
- Do the source articles cite specific geographic locations that corroborate ADM2 attribution?
- Are there contradictory signals across articles that suggest the anomaly may be ambiguous?

---

## Overall Validation Workflow

The complete analytical cycle proceeds through four sequential validation layers, moving from broad national surveillance to article-level confirmation.

```
Layer 1 — National Surveillance (National Overview)
    Identify elevated states/counties across all topics.
    Cross-reference with IPC national phase classifications.
             |
             v
Layer 2 — Anomaly Detection (ADM1 → ADM2 Insights)
    Apply multi-method consensus threshold engine.
    Assess convergence across Percentile, Tukey, and Z-Score methods.
    Use Method × Month Heatmap to identify agreement vs. divergence.
             |
             v
Layer 3 — Ground-Truth Validation (Validation Reference)
    Match identified alarm months to documented IPC events.
    Add new events to the reference as expert knowledge is applied.
    Assess true-positive vs. false-positive alarm rate for the region.
             |
             v
Layer 4 — Source-Level Confirmation (RAG+LLM Summary)
    Generate a cited situational brief for the flagged region and topic.
    Review source URLs for geographic and event-type corroboration.
    Assess whether the narrative supports or contradicts the statistical signal.
```

---

## Interpretation Standards

| Signal | Strength | Recommended Action |
|:---|:---|:---|
| Alarm confirmed by 3 methods + IPC event documented | **High confidence** | Flag for reporting. |
| Alarm confirmed by 2 methods, no IPC documentation | **Moderate confidence** | Investigate via RAG+LLM; seek additional context. |
| Alarm confirmed by 1 method only | **Low confidence** | Note for monitoring; not sufficient for reporting. |
| Alert without documented event | **Signal of interest** | Track over subsequent months. |
| Alarm in county with <12 months history | **Caution: fallback threshold** | Apply additional quantitative scrutiny. |
| Alarm in red-coverage topic (below 30% adequacy) | **Caution: sparse data** | Treat as indicative only. |
| County on recommended caution list | **Caution: geographic blind spot** | Cross-validate with field reports. |

---

## Common Failure Modes to Watch For

1. **NER false positives at ADM2 level**: A reporter mentions a county name in context (e.g., "food aid delivered to neighboring Baliet") and the article is attributed there, inflating that county's article count.

2. **Reporting spike vs. event spike**: A single large news event may generate many articles in one month, creating an apparent anomaly that reflects media attention rather than an underlying escalation.

3. **Seasonal patterns misread as anomalies**: Flooding (July–September) and harvest failure (October–November) are annual patterns. Alarms during these periods require seasonal interpretation, not just threshold comparison.

4. **Structurally sparse topic signals**: For red-highlighted topics (below 30% coverage adequacy), even a small increase in article count can trigger statistical alarms due to very low baselines.

5. **Silence is not safety**: If a county shows Normal status for an extended period, this may reflect lack of reporting rather than absence of crisis — particularly for counties on the recommended caution list.

---

*This guideline was prepared to support systematic evidence validation for IPC analysts monitoring South Sudan. For technical platform questions, refer to the project README.*
