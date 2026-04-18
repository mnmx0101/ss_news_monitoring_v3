# Media Monitoring: Key Specificities & Limitations

*South Sudan News Analytics Platform — Expert Briefing*

---

## 1. What Media Monitoring Actually Captures

**Core idea**: The platform tracks *reporting intensity*, rather than directly measuring event severity.

- The primary unit of analysis is the **article count per region per month** — acting as a proxy for media attention, which may not always scale directly with conflict, displacement, or hunger.
- An anomalous spike generally suggests: "*An event occurred that prompted increased media coverage*" — but it shouldn't be relied upon to quantify how many people were affected or the overall severity of a situation.
- Media signals can sometimes act as **early pointers**: coverage may precede formal assessments (like IPC or DTM), though the signal naturally contains some noise.
- The platform aims to flag **anomalies relative to a region's own historical baseline** — helping to spot what is "unusual for this place" rather than making absolute judgments.
- **Key framing**: Consider these as *exploratory signals* that can help guide further investigation, rather than serving as confirmatory evidence of a crisis on their own.

---

## 2. Keyword Taxonomy & Thematic Coverage

**Current labeling focus**: Conflict and Violence, Humanitarian Aid, Forced Displacements, and Political Instability. Note that **Conflict & Violence** and **Political Instability** signals can overlap significantly due to topic similarity and reporting patterns, even though their underlying keyword taxonomies are distinct.

**Core idea**: We rely on specific keywords, and coverage varies drastically by topic.

| Topic                           | Keywords                                                                                                                                                                               | Avg Coverage   |
| :------------------------------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------- |
| **Political Instability** | political, government, protest, demonstration, election, coup, instability, corruption, parliament, opposition, governance, policy, minister, president, cabinet, regime, referendum   | **~58%** |
| **Conflict and Violence** | conflict, war, fighting, battle, violence, clash, attack, military, armed, rebel, soldier, security, bomb, shell, shooting, insurgent, terror, terrorism, casualty, hostage, airstrike | **~58%** |
| **Humanitarian Aid**      | aid, relief, assistance, humanitarian, donor, funding, wfp, unhcr, unicef, ngo, distribution, support, msf, red cross, icrc                                                            | **~30%** |
| **Forced Displacements**  | displacement, displaced, refugee, refugees, idp, idps, migrant, migration, camp, camps, asylum, relocation, returnee, returnees                                                        | **~25%** |

- **Thematic considerations**: Topics below the **30% adequacy threshold** (e.g. Forced Displacements) tend to be structurally under-reported. Anomaly signals for these topics might best be treated with additional caution.
- **Attention distribution**: Major international events (like the Sudan spillover) can attract disproportionate coverage compared to more chronic, slow-onset situations.

---

## 3. Source Bias & Spatial Noise

**Core idea**: Relying on a single source offers a specific editorial perspective; any automated georeferencing process will contain inherent uncertainties.

- All data currently comes from **Radio Tamazuj** — a respected independent outlet with strong coverage of conflict and politics, though its footprint differs from a comprehensive national wire service.
- **Geographic distribution**: Coverage naturally tends to concentrate near state capitals and accessible areas; more remote counties (e.g., Canal/Pigi, Ibba, Pochalla, Gogrial East) may be more scarcely reported.
- **Georeferencing considerations**: The automated Named Entity Recognition (NER) algorithm attempts to match place names in text to administrative units.
  - **Potential false positives**: A county mentioned in passing during a political debate could be tagged even if the event didn't occur there.
  - **Potential false negatives**: Events described using highly informal or local names might occasionally be missed.
- **Interpreting silence**: An absence of reporting might reflect security risks or lack of access on the ground — not necessarily the absence of a crisis.

---

## 4. Threshold Methodology & Artificial Spikes

**Core idea**: Signal timing generally reflects *publication dates*, and anomaly detection is intended to help calibrate analyst attention.

| Methodology                         | Alert Threshold                              | Alarm Threshold                               |
| :---------------------------------- | :------------------------------------------- | :-------------------------------------------- |
| **Percentile Rank** (Default) | Top 25% of historical observations (p75).    | Top 10% of historical observations (p90).     |
| **Z-Score (SD)**              | Deviations > 1 Standard Deviation from mean. | Deviations > 2 Standard Deviations from mean. |

*Note*: The platform defaults to the Percentile Rank method. However, this can be complemented by the Z-Score method. Analysts can activate both methods simultaneously in the dashboard to see if the anomaly signals robustly align across different statistical approaches.

- **Temporal artifacts**: A single major event (e.g., Nasir airstrikes) might generate 10+ articles over several days, which can occasionally inflate the monthly count and trigger an artificial alert.
- **Predictable reporting cycles**: Seasonality in media attention (such as around UN General Assembly meetings or scheduled IPC releases) can create predictable reporting spikes that don't stem directly from new field conditions.
- **Minimum history threshold**: Regions with fewer than 24 months of data fall back to nationally-scaled thresholds to help limit inferences drawn from overly sparse baseline data.

---

## 5. Interpretation Guardrails

**Core idea**: Suggested approaches for interpreting and validating signals.

| ✅ Signals Can Help                      | ❌ Signals Typically Cannot                             |
| :--------------------------------------- | :------------------------------------------------------ |
| Highlight unusual increases in reporting | Directly measure severity (e.g., exact deaths or scale) |
| Suggest the timing of emerging events    | Confirm that an area is completely safe without crisis  |
| Show where media attention is clustering | Replace rigorous formal assessments (IPC, SMART)        |
| Spot potential cross-topic patterns      | Fully account for events in unreported regions          |
| Provide early leads for investigation    | Definitively distinguish root causes from correlations  |

**Suggested practices**:

- Where possible, triangulate signals with at least one **independent data source** (such as ACLED, IPC, or DTM).
- The best practice is to complement and validate the signals using contextual knowledge. A more direct approach is to try using the **RAG+LLM Summary function** to read detailed, cited intelligence about an event.
- This LLM Summary function might also prove helpful for contextualizing and explaining anomalous signals that originate from other conventional indicators.
- Try to look at **timing, persistence, and deviation** rather than getting overly focused on absolute article counts.
- Due to sparse coverage, it's generally best to **rely less on ADM2 (county-level) signals** and treat them more as **hypotheses to investigate**, rather than definitive findings.
- The **reference event overlay** can be a useful tool to help validate whether current signals align with known crises.
