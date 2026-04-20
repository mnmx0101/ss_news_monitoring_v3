---
title: South Sudan News Analytics Platform (V4)
colorFrom: blue
colorTo: green
sdk: streamlit
sdk_version: "1.40.1"
app_file: Home_v4.py
pinned: false
---

# South Sudan News Analytics Platform (V4)

A comprehensive dashboard for monitoring and analyzing news coverage in South Sudan, specifically tailored for humanitarian and food security analysts.

## Features

- **National Overview**: Statistical anomaloy detection and geographic heatmaps.
- **ADM1 & ADM2 Insights**: State-level and County-level anomaly detection with timeline markers.
- **Validation Reference**: Historical IPC event data for spatial triangulation.
- **RAG+LLM Summary**: AI-powered situation summaries generated dynamically from news archives.

## Data Requirement

This dashboard relies on Parquet reporting databases which are generated automatically or pulled from cloud datasets upon initialization.

## Environment Secrets

If deploying from this repository to Hugging Face Spaces or Streamlit Cloud, you must provide your OpenAI API key in your Cloud provider's Secrets configuration to power the RAG tab:

```toml
OPENAI_API_KEY = "sk-xxxxxxxx"
```
