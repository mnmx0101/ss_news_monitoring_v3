---

# South Sudan Media Analytics Platform
### News-Derived Signal Intelligence for Humanitarian Analysis

---

## What Is This Platform?

**A dual-tool platform that converts media coverage into actionable early-warning signals.**

| | Radio Tamazuj Tool | GDELT Dashboard |
|---|---|---|
| **Focus** | Deep local intelligence | Broad multi-source monitoring |
| **Scope** | Hyper-local South Sudan | Regional + global GDELT events |
| **Data Period** | 2020 – present | 2020 – present |
| **Strength** | Flexible topic labeling + full-text AI | Cross-source convergence analysis |
| **Data volume** | ~80,000 curated articles | Automated GDELT event feeds |

> These tools are complementary — one for narrative depth, one for cross-source breadth.

---

## How They Compare

| | Radio Tamazuj | GDELT |
|---|---|---|
| **Data Period** | 2020 – present | 2020 – present |
| **Data Ingestion** | Manual scraping pipeline | Automated standardised pipeline |
| **Georeferencing (ADM1)** | Reliable at state level | Reliable at state level |
| **Georeferencing (ADM2)** | NLP-based, limited rural coverage | Standardised, limited rural coverage |
| **Labeling** | Flexible custom taxonomy (any topic) | Primarily conflict-focused; expandable to humanitarian aid |
| **Sources** | Single source (Radio Tamazuj) | 5+ sources (Eye Radio, Sudan Tribune, ReliefWeb…) |
| **Full-Text AI** | ✅ RAG + LLM summariser | ✅ Available for peak events |
| **Cross-Source Validation** | ❌ Single-source only | ✅ Convergence scoring across sources |

> **Shared limitation:** Rural and remote regions are structurally under-reported in media, regardless of tool.

---

## How to Position This Tool

**A complementary signal layer — not a replacement for formal humanitarian data.**

### Potential use case: Exploring consistency with formal sources

- When IPC reports flag elevated Phase 3–4 populations → *Is media coverage consistent with this, and where?*
- When economic indicators suggest a food price shock → *Are journalists reporting related dynamics?*
- When DTM data shows displacement → *Do news narratives reference similar events in the same period?*

> These are exploratory questions — media signals are **not confirmatory evidence**, but may help prioritize where to look further.

### What media monitoring may add

- **Timeliness** — Media sometimes picks up events before formal reporting cycles close, though not always
- **Contextual texture** — Provides narrative detail that quantitative indicators cannot capture
- **Geographic signal** — Can suggest which states or counties are generating coverage, subject to georeferencing limitations
- **An additional lens** — One more data point to triangulate alongside, not instead of, formal humanitarian assessments

---

## Dashboard Walkthrough

### 🏠 Home
Dataset overview · keyword taxonomy · geographic coverage · key limitations

### 🗺️ National Overview
Country-wide heatmaps — which states and counties are at **Alert** or **Alarm** this month?

### 📊 ADM1 / ADM2 Insights
Drill into a specific state or county · trend chart · 3-method statistical consensus engine

### 📋 Validation Reference
Key events recorded in IPC reports for South Sudan (2020 onwards) — cross-reference against detected signals

### 🤖 RAG + LLM Summary
Select a flagged region + time window → AI generates a cited situational brief from primary articles

### 🌐 External Analysis (GDELT)
Multi-source convergence analysis — does the broader media landscape agree with local reporting?

---

## How to Validate the Tool

### The 4-Layer Verification Funnel

```
1. DETECT       →  National Overview heatmap
                   Which states/counties show elevated signals?

2. CONFIRM      →  ADM1 / ADM2 Insights (consensus engine)
                   Do all 3 methods agree? (Percentile + Tukey + Z-Score)

3. BENCHMARK    →  Validation Reference
                   Does an IPC-recorded key event align with the flagged period?

4. INVESTIGATE  →  RAG + LLM Summary
                   What were journalists reporting? Verify via source articles.
```

**Multi-layered gate passed:** Signal confirmed by ≥2 statistical methods + IPC-recorded key event + corroborating narrative

---

## Limitations & Your Feedback Matters

### Known Limitations

- **Rural under-reporting** — Both tools reflect media reach, not field reality; remote areas are structurally under-covered
- **Georeferencing at ADM2** — County-level attribution can be noisy; articles may be misassigned based on incidental name mentions
- **Reporting ≠ Reality** — A media spike may reflect retrospective coverage or editorial focus, not active escalation
- **Silence is not safety** — A county showing Normal status may indicate absence of reporting, not absence of crisis
- **Label sparsity** — Low-coverage topics can trigger statistical alarms from small absolute changes

### We Need Your Expert Input

✅ Which signals match well with known events at **national and regional level**?  
✅ Which **(topic × region)** combinations show false positives or missed signals?  
✅ Which regions or topics feel most unreliable to you?  
✅ How can we update the **keyword taxonomy** to better capture South Sudan-specific terminology?

> **Expert feedback directly informs threshold calibration and future model refinement.**

---
*South Sudan News Analytics Platform V3 · Johns Hopkins · 2026*
