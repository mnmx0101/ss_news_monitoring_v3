# Expert Review Template: Conflict & Violence

**Topic**: Conflict and Violence  
**Platform**: South Sudan News Analytics Platform (V4)  
**Source**: Radio Tamazuj  
**Keywords**: conflict, war, fighting, battle, violence, clash, attack, military, armed, rebel, soldier, security, bomb, shell, shooting, insurgent, terror, terrorism, casualty, hostage, airstrike

---

## 1. Projection Assumptions

### Expected indicator behaviour

- Conflict reporting is expected to **persist and escalate during the December-May dry season**, when military operations and intercommunal raiding are logistically easier.
- During the **lean season (May-August)**, cyclical violence driven by resource competition (cattle, water, grazing land) is expected to overlay ongoing armed conflict.
- Media coverage is foreseen to show **spikes during discrete escalation events** (attacks, territorial shifts, displacement waves, international evacuations) and an **elevated baseline during prolonged insecurity**.

### Link to AFI/AMN impact pathways

| Conflict mechanism | AFI/AMN pathway |
|:---|:---|
| Displacement | Loss of agricultural assets, disruption of planting/harvesting cycles |
| Market disruption | Price spikes, trade route closures, reduced food availability |
| Access disruption | Humanitarian corridors blocked, aid delivery suspended |
| Asset loss | Livestock raiding, granary destruction |
| Labour disruption | Recruitment, flight, and injury reduce household productivity |

**Summary pathway**: Conflict -> displacement + market disruption + reduced humanitarian access -> deterioration in Acute Food Insecurity (AFI) and Acute Malnutrition (AMN).

### Temporal & spatial variations

| Dimension | Expected pattern |
|:---|:---|
| **Temporal** | Peaks during dry-season offensives (Dec-Mar); secondary escalation around lean-season competition (Jun-Aug); relative lulls during heavy rains (Sep-Nov) |
| **Spatial hotspots** | Upper Nile (Malakal, Renk - Sudan spillover), Jonglei (Bor, Akobo - intercommunal), Unity (Bentiu - oil-area conflict), Lakes/Warrap (cattle raiding) |
| **Localised variation** | Strong county-level variation; the same state may have one county in active combat and an adjacent county in relative calm |

---

## 2. Data Sources & Limitations

### Coverage & reliability

- **Source**: [Radio Tamazuj](https://www.radiotamazuj.org/en/about-us) - an independent media outlet specialising in South Sudan and the broader region.
- **Strengths**: Strong narrative coverage of conflict events and dynamics, particularly in Upper Nile, Jonglei, and Unity. Good chronological depth (multi-year archive).
- **Format**: Deduplicated articles, each georeferenced to ADM1/ADM2 via Named Entity Recognition (NER), and labelled by topic using the keyword taxonomy.

### Data gaps / inconsistencies / breaks

| Gap type | Detail |
|:---|:---|
| **Geographic bias** | Coverage is skewed toward state capitals and accessible areas. Remote counties (Greater Equatoria borderlands, eastern Jonglei) are systematically underreported. |
| **Reporting intensity variation** | Media attention to conflict fluctuates with journalistic access, editorial priorities, and international attention cycles - not just with actual conflict levels. |
| **NER noise** | Georeferencing errors cause false attributions (e.g., a place mentioned in context rather than as event location). County-level signals are approximations. |
| **Single source** | No triangulation with other media outlets - all signals reflect Radio Tamazuj's editorial scope. |

### Implications for baseline validity

- The baseline reflects **media reporting activity**, not actual conflict levels. A "quiet month" may mean no reporting rather than no conflict.
- Thresholds should be interpreted as **relative anomalies in reporting** - unusual increases relative to this source's own historical pattern.
- Counties with fewer than **24 months** of reporting history (the default minimum) are flagged and **suppressed from Alert/Alarm** because their baseline is insufficient for reliable inference.

---

## 3. Proposed Measure

### Dimension captured

- **Article Count**: Measures the **change/deviation** in the volume of conflict-related reporting over time, relative to a historical baseline.
- Does **not** directly measure conflict intensity, severity, or casualties - only the quantity of media attention classified under the Conflict & Violence taxonomy.

### Fit-for-purpose

| Strength | Limitation |
|:---|:---|
| Captures emerging escalations and sudden reporting shocks effectively | Cannot distinguish between one major attack and many small incidents |
| Temporally responsive - coverage often precedes formal situation reports | Sensitive to editorial cycles and access constraints |
| Historically grounded - multi-year baseline enables anomaly detection | Does not measure severity (deaths, displacement scale) |

### Need for complementary measures

This measure should be complemented with:
- **ACLED / UCDP**: Event-level conflict data with severity coding
- **IPC / FEWS NET**: Formal food insecurity classification for outcome validation
- **OCHA / DTM**: Displacement flow data to validate displacement-linked signals
- **Sentiment Score** (available in the platform): Intensity of negative tone may proxy severity when article count is ambiguous

---

## 4. Proposed Method

### Interpretability & defensibility

| Method | Available in V4 | Interpretation |
|:---|:---|:---|
| **Percentile (default)** | Yes, p75 / p90 | "This month's reporting volume exceeds 75%/90% of all historical months" |
| **Tukey Fence (IQR)** | Yes, k=1.5 | "This month is a mild/strong statistical outlier" |
| **Z-Score (SD)** | Yes, SD 1/2 | "This month deviates by 1/2 standard deviations above the mean" |
| **Categorical (National Avg)** | Yes | "This region exceeds the national-average thresholds" - useful for spatial comparison |

**Primary framing**: "Unusual increase in conflict-related reporting relative to this region's own historical baseline."

### Suitability given data constraints

- Anomaly-based methods are appropriate for noisy, non-standardised media data where absolute values are not meaningful on their own.
- Percentile-based thresholds are robust to skewed distributions (common in article counts).
- The Categorical method enables cross-region comparison using a single national bar.

### Known limitations / biases

- **Media spike sensitivity**: A burst of reporting on a single major event can trigger Alarm even if the underlying conflict dynamic has not changed.
- **Silence != safety**: Low/no reporting does not confirm the absence of conflict - it may reflect access constraints or editorial choices.
- **Reporting bias**: Regions with higher baseline media access will appear "calmer" statistically because their elevated baseline absorbs more variation before hitting thresholds.
- **Keyword scope**: The taxonomy captures a broad range of conflict terms but may miss violence described in euphemistic or culturally specific language.

---

## 5. Reference Events

Use these documented conflict escalations to validate that signals behave as expected:

| Period | Event | Expected signal | ADM1 focus |
|:---|:---|:---|:---|
| **Dec 2013 - Apr 2014** | South Sudan civil war outbreak | Sustained Alarm across multiple states | Jonglei, Unity, Upper Nile |
| **Jul 2016** | Juba crisis / renewed fighting | Sharp spike followed by sustained elevation | Central Equatoria, Jonglei |
| **2020** | Jonglei intercommunal violence (Bor, Pibor) | Localised spikes in Jonglei counties | Jonglei |
| **Apr 2023** | Sudan conflict spillover (Renk, Upper Nile) | Strong signal in Upper Nile; displacement linked | Upper Nile |
| **2024-2025** | Escalation in Unity, Warrap; continued Sudan spillover | Elevated baseline + spikes across hotspot states | Upper Nile, Unity, Warrap |
| **Dec 2025 - Mar 2026** | Dry-season offensive cycle | Expected escalation pattern; test current signals | Multiple states |

### Anchor for signal behaviour

- **Clear spikes** expected during discrete escalation events (attacks, territorial changes).
- **Sustained elevated baseline** expected during prolonged insecurity phases.
- **Return to normal** expected after ceasefires, peace agreements, or rainy-season onset.

### Alignment with IPC deterioration phases

- Compare the timing of Alarm signals with IPC Phase transitions in the same states.
- Conflict-driven deterioration typically manifests in IPC projections **1-3 months after** escalation events - media signals may lead formal assessments.

---

## 6. Interpretation Note

### How to interpret signals

- Signals reflect **changes in reporting intensity**, not direct conflict magnitude.
- An **Alarm** means: "This region has an unusually high volume of conflict-related articles compared to its own history." It does not mean: "Conflict severity is at its worst."
- Focus on **timing** (when do signals emerge?), **persistence** (do they sustain over multiple months?), and **deviation from baseline** (how unusual is this?) - rather than absolute article counts.

### Key caveats

1. **Signals are exploratory, not confirmatory** - they suggest where to look further, not what is definitively happening.
2. **Silence is not evidence of absence** - no articles may mean no access, not no conflict.
3. **Regions with insufficient history** (< 24 months) have their signals suppressed to "No Concern" and should not be used for decision-making without additional sources.
4. **Cross-topic interaction** - a conflict escalation often co-triggers signals in Forced Displacements, Humanitarian Aid, Food Crisis, and Economic Issues. Consider the multi-topic pattern, not just Conflict in isolation.
5. **Interpret alongside contextual information** - location, type of event being reported, and alignment with other indicators (ACLED, IPC, DTM).
