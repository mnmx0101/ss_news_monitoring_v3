# Expert Review Templates — South Sudan News Analytics Platform (V4)

**Source**: Radio Tamazuj | **Minimum history**: 24 months | **Thresholds**: Percentile, Tukey, Z-Score, Categorical

---

# 1. Conflict and Violence

**Keywords**: conflict, war, fighting, battle, violence, clash, attack, military, armed, rebel, soldier, security, bomb, shell, shooting, insurgent, terror, terrorism, casualty, hostage, airstrike  
**Coverage**: ~16,300 articles | 77 counties | ~30% avg county-month coverage

## 1.1 Projection Assumptions
- Escalation expected during dry season (Dec-May); cyclical intercommunal violence during lean season (Jun-Aug)
- Media spikes expected during discrete attacks, displacement waves, and humanitarian evacuations
- Impact pathway: conflict -> displacement + market disruption + access constraints -> AFI/AMN deterioration
- Hotspots: Upper Nile (Sudan spillover), Jonglei (intercommunal), Unity (oil-corridor), Lakes/Warrap (cattle raiding)
- Strong county-level variation; adjacent counties can have very different conflict dynamics

## 1.2 Data Sources & Limitations
- Radio Tamazuj provides strong narrative coverage, especially in conflict hotspots (Upper Nile, Jonglei, Unity)
- Coverage biased toward accessible areas and state capitals; remote counties systematically underreported
- Reporting intensity varies with journalistic access and international attention, not just actual conflict
- NER georeferencing introduces noise at county level (false positives from contextual mentions)
- Baseline reflects media activity, not conflict levels; silence does not mean safety

## 1.3 Proposed Measure
- Article count measures change/deviation in conflict-related reporting volume vs historical baseline
- Does not measure conflict severity, casualties, or area of control directly
- Captures emerging escalations and sudden reporting shocks effectively
- Sensitive to editorial cycles; a single major event can dominate a month's count
- Complement with: ACLED (event severity), IPC (food security outcomes), DTM (displacement flows)

## 1.4 Proposed Method
- Anomaly-based thresholds: "unusual increase in conflict reporting relative to this region's own history"
- Percentile (default p75/p90) robust to skewed article count distributions
- Categorical method useful for cross-region comparison using a single national bar
- Cannot distinguish severity; sensitive to media spikes; does not account for reporting bias
- Regions with < 24 months suppressed (insufficient baseline for reliable inference)

## 1.5 Reference Events
- **2020-02 to 2020-05** (Jonglei/Pibor): Lou Nuer-Murle clashes kill 287+ with mass abductions
- **2021-08** (Upper Nile): Kitgwang Declaration triggers SPLM-IO factional clashes
- **2022-02 to 2022-05** (Unity/Leer, Koch, Mayendit): Government forces attack civilian villages
- **2022** (Upper Nile): White Army raids raze Shilluk villages; helicopter gunship intervention
- **2023-01** (Jonglei/Pibor): Lou Nuer-Murle revenge killings — 308 killed, 299 abducted
- **2024-01** (Abyei): Attack kills 52 people including women and children
- **2024** (National): UNMISS documents 1,019 violent incidents (+51% over 2023)
- **2025-01** (Western Equatoria): SSPDF-SPLA/IO armed clashes
- **2025-02 to 2025-03** (Upper Nile/Nasir): White Army overruns base; retaliatory airstrikes
- **2025-03** (Upper Nile/Nasir, Longechuk, Ulang): SSPDF aerial bombardments kill 58+

## 1.6 Interpretation Note
- Signals = changes in reporting intensity, not conflict magnitude
- Focus on timing, persistence, and deviation from baseline, not absolute counts
- Silence is not evidence of absence; may reflect access constraints
- Conflict escalations often co-trigger Displacement, Humanitarian Aid, and Food Crisis signals
- Signals are exploratory, not confirmatory: they suggest where to look further

---

# 2. Humanitarian Aid

**Keywords**: aid, relief, assistance, humanitarian, donor, funding, wfp, unhcr, unicef, ngo, distribution, support, msf, red cross, icrc  
**Coverage**: ~11,700 articles | 77 counties | ~30% avg county-month coverage

## 2.1 Projection Assumptions
- Aid reporting expected to spike during and after acute crises (conflict, flooding, displacement surges)
- Lean season (May-Aug) typically sees increased food assistance operations and reporting
- Impact pathway: aid presence/absence signals access capacity; aid disruptions may precede food security deterioration
- Hotspots overlap with conflict and displacement areas: Upper Nile, Jonglei, Unity, Warrap
- Aid reporting may surge with donor pledging cycles and UN appeals (Feb/Mar, Sep/Oct)

## 2.2 Data Sources & Limitations
- Good coverage of humanitarian operations and agency activities in major crisis locations
- Bias toward large-scale operations by major agencies (WFP, UNHCR, UNICEF); smaller NGO activities underreported
- Reporting reflects media interest in aid, not the actual volume or effectiveness of assistance
- Spikes may reflect press releases and public communications rather than operational changes
- Aid keywords overlap with political discourse (e.g. "donor" in diplomatic context)

## 2.3 Proposed Measure
- Article count captures change/deviation in volume of aid-related reporting vs baseline
- Proxies for humanitarian operational tempo and crisis response intensity
- A spike may signal either increased need (crisis response) or increased access (reopened corridors)
- Does not measure aid volume, beneficiary reach, or program effectiveness
- Complement with: OCHA 3W data (who/what/where aid delivery), WFP distribution records

## 2.4 Proposed Method
- Anomaly thresholds flag unusual increases in aid reporting relative to region's own history
- Percentile method works well given aid reporting's seasonal patterns
- Categorical method enables comparison of aid attention across regions (which areas are "neglected")
- Cannot distinguish positive spikes (more aid arriving) from negative spikes (aid disruption reporting)
- Regions with < 24 months suppressed to avoid false signals from sporadic coverage

## 2.5 Reference Events
- **2021** (National): IPC reports 8.3M (70% of population) in need of humanitarian assistance
- **2022-11** (National): FAO-UNICEF-WFP warns 7.76M face crisis-level food insecurity
- **2023** (National): 22 aid workers killed; one of most dangerous countries for humanitarians
- **2023-04 to 2023-12** (Upper Nile/Renk): Renk transit center overwhelmed (5K capacity, 16K+ occupants)
- **2023/2024** (Upper Nile/Renk): 508K+ cross via Renk; cholera and measles outbreaks
- **2024-06** (Unity): FEWS NET projects Famine risk (IPC Phase 5) in north-central Unity
- **2024** (National): $1.8B Humanitarian Response Plan only 57% funded
- **2025-05** (Jonglei/Fangak): Government bombs MSF hospital, killing 7
- **2024-10 to 2025-09** (National): Cholera spreads across 17 states, 700+ dead
- **2025** (Upper Nile, Jonglei): WFP warns violence risks cutting aid; 7.56M face crisis hunger

## 2.6 Interpretation Note
- Aid reporting spikes are ambiguous: they can signal either crisis escalation or response mobilisation
- Declining signals may indicate improving conditions, aid fatigue, or loss of access
- Cross-reference with Conflict and Displacement signals to determine whether aid spikes are reactive or proactive
- Sustained aid signals with declining conflict signals may indicate recovery/stabilisation phase
- Signals are exploratory; operational details require 3W and agency report triangulation

---

# 3. Forced Displacements

**Keywords**: displacement, displaced, refugee, refugees, idp, idps, migrant, migration, camp, camps, asylum, relocation, returnee, returnees  
**Coverage**: ~7,600 articles | 77 counties | ~25% avg county-month coverage

## 3.1 Projection Assumptions
- Displacement reporting expected to spike with conflict escalation, flooding, and lean-season shocks
- Secondary peaks during return movements (following ceasefires, dry-season access improvements)
- Impact pathway: displacement -> loss of livelihoods, overcrowding in camps, increased vulnerability to AMN
- Hotspots: Upper Nile (Sudan refugee influx), Jonglei (intercommunal displacement), Unity (Bentiu IDP camp)
- Displacement is seasonally layered: conflict-driven (dry season) + flood-driven (Jul-Nov)

## 3.2 Data Sources & Limitations
- Good coverage of large-scale displacement events, especially those involving IDP camps and UN involvement
- Chronic/protracted displacement receives less reporting than acute new displacement
- "Returnee" keyword captures both positive (voluntary return) and negative (forced return) dynamics
- Camp-based displacement overrepresented; spontaneous settlement and host-community absorption underreported
- Coverage lower (~25%) than Conflict (~30%); many displacement events go unreported in remote areas

## 3.3 Proposed Measure
- Article count tracks change/deviation in displacement-related reporting volume
- Captures sudden displacement events and major population movements effectively
- Does not capture displacement scale (numbers displaced), duration, or conditions
- Ongoing protracted displacement may not generate media signals (normalisation effect)
- Complement with: DTM/IOM flow monitoring, UNHCR registration data, camp population records

## 3.4 Proposed Method
- Anomaly thresholds detect unusual increases in displacement reporting vs historical baseline
- Useful for identifying timing of new displacement events before formal DTM reporting cycles
- Categorical method reveals which regions receive disproportionate vs insufficient displacement coverage
- Sensitive to single events covered in multiple articles (camp opening, border influx)
- Regions with < 24 months suppressed; especially important here given ~25% coverage

## 3.5 Reference Events
- **2020** (Jonglei/Pibor): Intercommunal violence forces thousands to flee to UNMISS base
- **2020/2021** (National): Record floods destroy 65K+ ha farmland, kill 800K livestock
- **2022** (National): Floods affect 900K+, displace 140K across 29 counties
- **2023-04 to 2024-06** (Upper Nile/Renk, Malakal): Sudan war drives 720K+ into South Sudan
- **2023-06** (Upper Nile/Malakal): Inter-ethnic violence in Malakal PoC kills 20+
- **2023-12** (National): IDP population reaches 2M internal; 2.27M refugees abroad
- **2024-05 to 2024-12** (National): Extreme flooding affects 1.4M, displaces 379K+
- **2025** (Upper Nile/Renk): Total arrivals from Sudan surpass 1M since Apr 2023
- **2025-03 to 2025-09** (Upper Nile/Nasir, Ulang, Longechuk): Airstrikes cause mass displacement to Ethiopia
- **2025** (National): 2.3M refugees abroad, 1.9M internally displaced

## 3.6 Interpretation Note
- Spike = sudden displacement event or major population movement being reported on
- Sustained elevated signal = protracted displacement situation receiving ongoing coverage
- Declining signal may mean situation stabilised, or media attention moved elsewhere
- Displacement signals often lag conflict signals by days-to-weeks; cross-reference with Conflict timeline
- Signals are exploratory; displacement scale and direction require DTM triangulation

---

# 4. Food Crisis

**Keywords**: food, famine, hunger, nutrition, malnutrition, insecurity, ipc, starvation, hungry  
**Coverage**: ~4,800 articles | 77 counties | ~18% avg county-month coverage

## 4.1 Projection Assumptions
- Food crisis reporting expected to peak during and around lean season (May-Aug) and post-harvest shortfall periods
- Spikes expected during IPC report releases, famine declarations, and major WFP/FEWS NET communications
- Impact pathway: direct indicator of AFI/AMN outcomes; media reflects both food insecurity conditions and institutional assessments
- Hotspots: Jonglei (chronic food insecurity), Unity (displacement-linked), Northern Bahr el Ghazal (lean-season epicentre)
- Lowest coverage of the 4 topics (~18% avg) — signals may be sparse and require careful interpretation

## 4.2 Data Sources & Limitations
- Coverage adequate for IPC-linked events and famine reporting but sparse for routine food security
- Keywords include "ipc" and "famine" — signals often reflect publication of formal assessments rather than field-level conditions
- Low county-month coverage (~18%) means many counties have no food crisis reporting for most months
- Under-covered topics: chronic malnutrition, market-level food access, household coping strategies
- Reporting may concentrate around UN calendar (IPC cycles, lean-season appeals) rather than actual onset

## 4.3 Proposed Measure
- Article count tracks change/deviation in food crisis reporting volume
- Effectively captures high-profile food crises, famine alerts, and institutional alarm signals
- Less effective at detecting slow-onset food insecurity in underreported areas
- Does not measure food prices, caloric intake, or nutritional status directly
- Complement with: IPC/CH data (formal classification), FEWS NET price monitoring, SMART surveys (AMN)

## 4.4 Proposed Method
- Anomaly thresholds flag unusual increases in food crisis reporting
- Due to low coverage (18%), many regions will have sparse baselines; N=24 filter critical here
- Categorical method may not perform well — few regions have enough data for stable per-region P1/P2
- Consider using Percentile with lower p1 (e.g. 60th percentile) given sparser data
- Regions with < 24 months suppressed — expect a high proportion of counties flagged here

## 4.5 Reference Events

> [!NOTE]
> Food Crisis does not have dedicated reference events in `reference_events.py`. The events below are drawn from the Humanitarian Aid category where they directly relate to food security outcomes.

- **2021** (National): IPC reports 8.3M in need — peak humanitarian caseload
- **2022-11** (National): FAO-UNICEF-WFP warns 7.76M face crisis-level food insecurity
- **2024-06** (Unity): FEWS NET projects Famine risk (IPC Phase 5) in north-central Unity
- **2024** (National): HRP 57% funded — millions without adequate food assistance
- **2025** (Upper Nile, Jonglei): WFP warns 7.56M face crisis-level hunger

## 4.6 Interpretation Note
- Spikes often reflect institutional communications (IPC releases, WFP alerts) rather than field-level change
- Absence of food crisis reporting should NOT be interpreted as food security — it reflects coverage gaps
- Due to lowest coverage among the 4 topics, treat food crisis signals with heightened caution
- Cross-reference with Economic Issues and Production Shortage signals for upstream drivers
- Signals are exploratory; food security severity requires IPC/FEWS NET validation

---

# 5. Political Instability

**Keywords**: political, government, protest, demonstration, election, coup, instability, corruption, parliament, opposition, governance, policy, minister, president, cabinet, regime, referendum  
**Coverage**: ~16,000 articles | 77 counties | ~58% avg county-month coverage (highest of all topics)

## 5.1 Projection Assumptions
- Political reporting expected to spike around election deadlines, peace agreement milestones, and constitutional crises
- Spikes during leadership disputes, factional splits, and military-political confrontations
- Impact pathway: political instability -> security vacuum + institutional paralysis -> reduced service delivery + aid disruption -> AFI/AMN deterioration
- Hotspots: Juba (national politics), Upper Nile/Jonglei (factional dynamics), all states during election cycles
- Highest coverage topic (~58%); signals are relatively robust compared to other categories

## 5.2 Data Sources & Limitations
- Strongest coverage of any topic due to political keywords appearing in broad governance and diplomatic reporting
- Keywords like "government," "president," "minister" capture routine governance reporting, not just crises
- High baseline means anomaly thresholds must distinguish genuine instability from normal political discourse
- Juba-centric bias: national political events dominate; subnational governance dynamics underreported
- Overlap with Conflict & Violence when political disputes escalate to armed confrontation

## 5.3 Proposed Measure
- Article count tracks change/deviation in political instability reporting volume
- Effectively captures discrete political shocks (coups, detentions, factional splits, election crises)
- Elevated baseline from routine governance reporting may dilute anomaly sensitivity
- Does not distinguish between positive political developments (peace deals) and negative ones (crises)
- Complement with: political event databases, peace process trackers, election monitoring reports

## 5.4 Proposed Method
- Anomaly thresholds flag unusual increases vs this topic's elevated baseline
- Percentile method works well given the high volume and relatively stable baseline
- Categorical method effective here due to strong coverage enabling stable per-region thresholds
- High coverage (58%) means fewer regions will trigger the N=24 month fallback
- Watch for false spikes from routine political coverage cycles (budget season, UN GA, IGAD summits)

## 5.5 Reference Events
- **2020-01** (National): Sant'Egidio Rome peace declaration between SSOMA and government
- **2020-02** (National): Kiir-Machar form R-TGoNU under R-ARCSS peace agreement
- **2021-08** (National): Kitgwang Declaration splits SPLM-IO, threatening peace process
- **2022** (National): First election postponement; transitional government misses Feb 2023 deadline
- **2020/2024** (National): Key R-ARCSS provisions unimplemented (unified forces, constitution, census)
- **2024-09** (National): Elections postponed to Dec 2026; transitional period extended to Feb 2027
- **2024-09** (National): R-TGoNU constitutional mandate formally expires; self-extended
- **2024** (National): Sudan war ruptures oil pipeline cutting two-thirds of state revenue
- **2025-03** (Central Equatoria/Juba): VP Machar detained under house arrest; treason charges filed
- **2025** (National): NSS detains activists/journalists; 114+ censorship and arrest cases documented

## 5.6 Interpretation Note
- Political signals have the highest baseline of all topics; focus on deviations, not absolute levels
- Spikes may reflect positive developments (peace agreements, elections announced) or crises (detentions, splits)
- Cross-reference with Conflict signals to identify when political disputes escalate to armed confrontation
- Sustained elevation may indicate protracted political crisis; sudden drops may indicate media suppression
- Signals are exploratory; political dynamics require contextual interpretation from governance analysts
