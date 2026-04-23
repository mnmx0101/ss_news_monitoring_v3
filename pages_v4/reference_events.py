"""
Reference events for expert review annotations.
Each event is annotated on timeline charts in National Overview and ADM1 Insights.

Topic types use the dashboard's Label column names:
  - "Conflict and Violence"
  - "Humanitarian Aid"
  - "Forced Displacements"
  - "Political Instability"
"""

import pandas as pd

REFERENCE_EVENTS = [
    # =========================================================================
    # CONFLICT AND VIOLENCE
    # =========================================================================
    # Type: CF = Armed conflict | ICV = Intercommunal | HR = Humanitarian access restriction
    # Intensity: H = High | M = Medium

    {"period": "2020-01/2020-03", "adm1": "Jonglei", "adm2": "Pieri",
     "topic": "Conflict and Violence", "label": "Pieri: ICV (H)",
     "description": "[ICV/H] Murle armed youth attack on Lou Nuer villages. ~287 killed."},

    {"period": "2020-01/2020-03", "adm1": "Jonglei", "adm2": "Pibor, Akobo, Nyirol",
     "topic": "Conflict and Violence", "label": "Pibor/Akobo: Lou Nuer-Murle ICV (H)",
     "description": "[ICV/H] Lou Nuer-Dinka-Murle cycle; ~8,000 displaced to UNMISS base in Pibor."},

    {"period": "2020-03", "adm1": "Lakes", "adm2": "Rumbek",
     "topic": "Conflict and Violence", "label": "Rumbek: Clan ICV (M)",
     "description": "[ICV/M] Inter-clan fighting triggered by killing of two elders. 41 killed, 60+ injured."},

    {"period": "2020-08", "adm1": "Warrap", "adm2": "Tonj",
     "topic": "Conflict and Violence", "label": "Tonj: Disarmament CF (H)",
     "description": "[CF/H] Clashes between soldiers and armed civilians following disarmament dispute. 127 killed (82 civilians)."},

    {"period": "2021-05", "adm1": "Jonglei", "adm2": "Pieri",
     "topic": "Conflict and Violence", "label": "Pieri: Repeat Murle ICV (H)",
     "description": "[ICV/H] Large-scale Murle attack on Lou Nuer villages (repeat cycle). ~287 killed."},

    {"period": "2022-02/2022-04", "adm1": "Unity", "adm2": "Leer",
     "topic": "Conflict and Violence", "label": "Leer: SSPDF Atrocities CF (H)",
     "description": "[CF/H] SSPDF + allied youth militia attack on SPLA-IO outpost; mass atrocities. Thousands displaced; war crimes documented."},

    {"period": "2022-04/2022-06", "adm1": "Warrap", "adm2": "Abyei AA",
     "topic": "Conflict and Violence", "label": "Abyei: Dinka ICV (H)",
     "description": "[ICV/H] Dinka Twic Mayardit vs. Dinka Ngok fighting; Warrap spillover. 117 civilians killed, 35 injured."},

    {"period": "2022-08/2022-12", "adm1": "Upper Nile", "adm2": "Greater Upper Nile",
     "topic": "Conflict and Violence", "label": "Kitgwang vs. Agwelek CF (H)",
     "description": "[CF/H] Kitgwang vs. Agwelek factional clashes within former SPLA-IO. 594 killed, 290 injured, 258 abducted, 75 SGBV."},

    {"period": "2022-10/2022-12", "adm1": "Upper Nile", "adm2": "Multiple",
     "topic": "Conflict and Violence", "label": "87% Harm Spike CF+ICV (H)",
     "description": "[CF+ICV/H] 87% spike in civilian harm vs. same period 2021; 464% rise in abductions."},

    {"period": "2022-10/2022-12", "adm1": "Warrap", "adm2": "Multiple",
     "topic": "Conflict and Violence", "label": "87% Harm Spike CF+ICV (H)",
     "description": "[CF+ICV/H] 87% spike in civilian harm vs. same period 2021; 464% rise in abductions."},

    {"period": "2022-10/2022-12", "adm1": "Jonglei", "adm2": "Multiple",
     "topic": "Conflict and Violence", "label": "87% Harm Spike CF+ICV (H)",
     "description": "[CF+ICV/H] 87% spike in civilian harm vs. same period 2021; 464% rise in abductions."},

    {"period": "2022-11", "adm1": "Warrap", "adm2": "S. Abyei, Warrap border",
     "topic": "Conflict and Violence", "label": "Abyei Border: Twic-Ngok ICV (M)",
     "description": "[ICV/M] Twic Dinka-Ngok Dinka retaliatory violence; SSPDF elements involved. 75 killed (Nov), 10 killed (Dec)."},

    {"period": "2023-01", "adm1": "Jonglei", "adm2": "Gumuruk, Lekyangole",
     "topic": "Conflict and Violence", "label": "Gumuruk: White Army ICV (H)",
     "description": "[ICV/H] White Army (Lou Nuer + Bor Dinka) attacks on Murle villages; child abductions. Mass displacement."},

    {"period": "2024", "adm1": "Unity", "adm2": "Multiple",
     "topic": "Conflict and Violence", "label": "Northern CF Surge 2024 (H)",
     "description": "[CF/H] UNMISS: 51% rise in civilian harm; 1,019 incidents. 1,561 killed, 1,299 injured, 551 abducted."},

    {"period": "2024", "adm1": "Upper Nile", "adm2": "Multiple",
     "topic": "Conflict and Violence", "label": "Northern CF Surge 2024 (H)",
     "description": "[CF/H] UNMISS: 51% rise in civilian harm; 1,019 incidents. 1,561 killed, 1,299 injured, 551 abducted."},

    {"period": "2024", "adm1": "Jonglei", "adm2": "Multiple",
     "topic": "Conflict and Violence", "label": "ICV Escalation 2024 (H)",
     "description": "[ICV/H] Escalating intercommunal violence; additional UNMISS peacekeepers deployed. 15% rise vs. 2023."},

    {"period": "2024", "adm1": "Lakes", "adm2": "Multiple",
     "topic": "Conflict and Violence", "label": "ICV Escalation 2024 (H)",
     "description": "[ICV/H] Escalating intercommunal violence; additional UNMISS peacekeepers deployed. 15% rise vs. 2023."},

    {"period": "2024", "adm1": "Eastern Equatoria", "adm2": "Multiple",
     "topic": "Conflict and Violence", "label": "ICV Escalation 2024 (H)",
     "description": "[ICV/H] Escalating intercommunal violence; additional UNMISS peacekeepers deployed. 15% rise vs. 2023."},

    {"period": "2025-02", "adm1": "Upper Nile", "adm2": "Nasir",
     "topic": "Conflict and Violence", "label": "Nasir: SPLA-IO Overrun CF (H)",
     "description": "[CF/H] SPLA-IO overrun of SSPDF base; 20+ civilians killed; Machar allies arrested. Thousands displaced; political crisis triggered."},

    {"period": "2025-02/2025-03", "adm1": "Upper Nile", "adm2": "Nasir, Ulang",
     "topic": "Conflict and Violence", "label": "Nasir/Ulang: Famine Driver CF (H)",
     "description": "[CF/H] SSPDF retaliatory offensive; evacuation orders; famine risk declared. ~110,000+ displaced."},

    {"period": "2025-03", "adm1": "Jonglei", "adm2": "Akobo",
     "topic": "Conflict and Violence", "label": "Akobo: Exodus CF (H)",
     "description": "[CF/H] SSPDF military operations; evacuation orders; Akobo largely deserted. ~110,000 fled to Ethiopia."},

    {"period": "2025-03", "adm1": "Jonglei", "adm2": "Fangak, Nyirol, Uror, Ayod",
     "topic": "Conflict and Violence", "label": "Fangak/Nyirol: Famine Cascade CF (H)",
     "description": "[CF/H] Escalating SSPDF/SPLM-IO clashes; famine risk across 8 counties. ~270,000 displaced."},

    {"period": "2025-03", "adm1": "Upper Nile", "adm2": "Fangak, Nyirol, Uror, Ayod",
     "topic": "Conflict and Violence", "label": "Fangak/Nyirol: Famine Cascade CF (H)",
     "description": "[CF/H] Escalating SSPDF/SPLM-IO clashes; famine risk across 8 counties. ~270,000 displaced."},

    {"period": "2025-03/2025-05", "adm1": "Jonglei", "adm2": "Fangak",
     "topic": "Conflict and Violence", "label": "Fangak: MSF Hospital Bombing CF/HR (H)",
     "description": "[CF/HR/H] SSPDF bombed MSF hospital in Fangak and old market (May 3). 7 killed, 20+ injured; aid access severed."},

    {"period": "2025-01/2025-09", "adm1": "Warrap", "adm2": "Multiple",
     "topic": "Conflict and Violence", "label": "Record ICV Year (H)",
     "description": "[ICV/H] OHCHR: worst ICV year on record. 1,854 killed, 1,693 injured, 423 abducted, 169 SGBV."},

    {"period": "2025-01/2025-09", "adm1": "Lakes", "adm2": "Multiple",
     "topic": "Conflict and Violence", "label": "Record ICV Year (H)",
     "description": "[ICV/H] OHCHR: worst ICV year on record. 1,854 killed, 1,693 injured, 423 abducted, 169 SGBV."},

    {"period": "2025-01/2025-09", "adm1": "Eastern Equatoria", "adm2": "Multiple",
     "topic": "Conflict and Violence", "label": "Record ICV Year (H)",
     "description": "[ICV/H] OHCHR: worst ICV year on record. 1,854 killed, 1,693 injured, 423 abducted, 169 SGBV."},

    {"period": "2025-03/2025-09", "adm1": "Western Equatoria", "adm2": "Multiple",
     "topic": "Conflict and Violence", "label": "W. Equatoria: Widespread CF (M)",
     "description": "[CF/M] UNMISS documented SSPDF, SPLA-IO, and NAS killings, abductions, sexual violence. Widespread."},
    # =========================================================================
    # HUMANITARIAN AID
    # =========================================================================
    {"period": "2021", "adm1": None, "adm2": None,
     "topic": "Humanitarian Aid",
     "label": "IPC: 8.3M in need (70%)",
     "description": "IPC reports 8.3 million people (70% of population) in need of humanitarian assistance"},
    {"period": "2022-11", "adm1": None, "adm2": None,
     "topic": "Humanitarian Aid",
     "label": "FAO-UNICEF-WFP: 7.76M food crisis",
     "description": "Joint report warns 7.76 million face crisis-level food insecurity, worst ever"},
    {"period": "2023", "adm1": None, "adm2": None,
     "topic": "Humanitarian Aid",
     "label": "22 aid workers killed",
     "description": "22 aid workers killed in South Sudan, one of most dangerous countries for humanitarians"},
    {"period": "2023-04/2023-12", "adm1": "Upper Nile", "adm2": "Renk",
     "topic": "Humanitarian Aid",
     "label": "Renk transit center overwhelmed",
     "description": "Sudan war spillover overwhelms Renk transit center (5K capacity, 16K+ occupants)"},
    {"period": "2023/2024", "adm1": "Upper Nile", "adm2": "Renk",
     "topic": "Humanitarian Aid",
     "label": "508K+ cross via Renk (cholera/measles)",
     "description": "508,000+ cross into South Sudan via Renk; overcrowding causes disease outbreaks"},
    {"period": "2024-06", "adm1": "Unity", "adm2": None,
     "topic": "Humanitarian Aid",
     "label": "FEWS NET: Famine risk (IPC 5)",
     "description": "FEWS NET projects risk of Famine (IPC Phase 5) in north-central Unity"},
    {"period": "2024", "adm1": None, "adm2": None,
     "topic": "Humanitarian Aid",
     "label": "HRP 57% funded ($1.8B)",
     "description": "$1.8 billion Humanitarian Response Plan only 57% funded"},
    {"period": "2025-05", "adm1": "Jonglei", "adm2": "Fangak",
     "topic": "Humanitarian Aid",
     "label": "MSF Fangak hospital bombed",
     "description": "Government forces bomb MSF hospital in Fangak killing 7"},
    {"period": "2024-10/2025-09", "adm1": None, "adm2": None,
     "topic": "Humanitarian Aid",
     "label": "Cholera: 17 states, 700+ dead",
     "description": "Cholera outbreak spreads across 17 of 18 states killing more than 700"},
    {"period": "2025", "adm1": "Upper Nile, Jonglei", "adm2": None,
     "topic": "Humanitarian Aid",
     "label": "WFP: 7.56M crisis hunger",
     "description": "WFP warns escalating violence risks cutting food assistance to hundreds of thousands"},

    # =========================================================================
    # FORCED DISPLACEMENTS
    # =========================================================================
    {"period": "2020", "adm1": "Jonglei", "adm2": "Pibor",
     "topic": "Forced Displacements",
     "label": "Pibor intercommunal displacement",
     "description": "Intercommunal violence forces thousands to flee; shelter at UNMISS Pibor base"},
    {"period": "2020/2021", "adm1": None, "adm2": None,
     "topic": "Forced Displacements",
     "label": "Record floods (65K ha, 800K livestock)",
     "description": "Record flooding destroys 65,000+ hectares and kills 800,000 livestock"},
    {"period": "2022", "adm1": None, "adm2": None,
     "topic": "Forced Displacements",
     "label": "Floods: 900K affected, 140K displaced",
     "description": "Consecutive flooding affects 900,000+ and displaces 140,000 across 29 counties"},
    {"period": "2023-04/2024-06", "adm1": "Upper Nile", "adm2": "Renk, Malakal",
     "topic": "Forced Displacements",
     "label": "Sudan war: 720K+ into S. Sudan",
     "description": "Sudan war drives 720,000+ into South Sudan via Renk; Malakal PoC swells"},
    {"period": "2023-06", "adm1": "Upper Nile", "adm2": "Malakal",
     "topic": "Forced Displacements",
     "label": "Malakal PoC violence (20+ killed)",
     "description": "Inter-ethnic violence in Malakal PoC site kills at least 20"},
    {"period": "2023-12", "adm1": None, "adm2": None,
     "topic": "Forced Displacements",
     "label": "IDPs: 2M internal, 2.27M refugees",
     "description": "IDP population reaches 2 million; 2.27 million South Sudanese refugees abroad"},
    {"period": "2024-05/2024-12", "adm1": None, "adm2": None,
     "topic": "Forced Displacements",
     "label": "Floods: 1.4M affected, 379K displaced",
     "description": "Extreme flooding affects 1.4 million across 44 counties"},
    {"period": "2025", "adm1": "Upper Nile", "adm2": "Renk",
     "topic": "Forced Displacements",
     "label": "Sudan arrivals surpass 1M",
     "description": "Total arrivals from Sudan since April 2023 surpass 1 million"},
    {"period": "2025-03/2025-09", "adm1": "Upper Nile", "adm2": "Nasir, Ulang, Longechuk",
     "topic": "Forced Displacements",
     "label": "Upper Nile airstrikes displacement",
     "description": "Government airstrikes cause mass displacement including cross-border flight to Ethiopia"},
    {"period": "2025", "adm1": None, "adm2": None,
     "topic": "Forced Displacements",
     "label": "2.3M refugees, 1.9M IDPs",
     "description": "South Sudanese refugee population abroad reaches 2.3 million"},

    # =========================================================================
    # POLITICAL INSTABILITY
    # =========================================================================
    {"period": "2020-01", "adm1": None, "adm2": None,
     "topic": "Political Instability",
     "label": "Rome peace declaration (SSOMA)",
     "description": "Sant'Egidio mediates Rome peace declaration between SSOMA and government"},
    {"period": "2020-02", "adm1": None, "adm2": None,
     "topic": "Political Instability",
     "label": "R-TGoNU formed (Kiir-Machar)",
     "description": "Kiir and Machar form Revitalized Transitional Government of National Unity"},
    {"period": "2021-08", "adm1": None, "adm2": None,
     "topic": "Political Instability",
     "label": "Kitgwang Declaration (SPLM-IO split)",
     "description": "Kitgwang Declaration by Gatwech Dual splits main opposition SPLM-IO"},
    {"period": "2022", "adm1": None, "adm2": None,
     "topic": "Political Instability",
     "label": "Election postponement",
     "description": "First election postponement as transitional government misses Feb 2023 deadline"},
    {"period": "2020/2024", "adm1": None, "adm2": None,
     "topic": "Political Instability",
     "label": "R-ARCSS provisions unimplemented",
     "description": "Key R-ARCSS provisions remain unimplemented: unified forces, constitution, census"},
    {"period": "2024-09", "adm1": None, "adm2": None,
     "topic": "Political Instability",
     "label": "Elections postponed to Dec 2026",
     "description": "Presidency postpones elections to December 2026, extends transitional period"},
    {"period": "2024-09", "adm1": None, "adm2": None,
     "topic": "Political Instability",
     "label": "R-TGoNU mandate expires",
     "description": "R-TGoNU constitutional mandate formally expires; signatories self-extend"},
    {"period": "2024", "adm1": None, "adm2": None,
     "topic": "Political Instability",
     "label": "Oil pipeline cut (2/3 revenue lost)",
     "description": "Sudan war ruptures oil export pipeline cutting two-thirds of state revenue"},
    {"period": "2025-03", "adm1": "Central Equatoria", "adm2": "Juba",
     "topic": "Political Instability",
     "label": "VP Machar detained, treason charges",
     "description": "Government places VP Machar under house arrest; treason charges filed"},
    {"period": "2025", "adm1": None, "adm2": None,
     "topic": "Political Instability",
     "label": "NSS: 114+ censorship/detention cases",
     "description": "NSS uses 2024 Act to detain activists and journalists without warrants"},
]


def parse_period_start(period_str):
    """Parse period string to a start date for chart annotation."""
    # Handle range periods like "2020-02/2020-05"
    start = period_str.split("/")[0]
    if len(start) == 4:  # year only
        return pd.Timestamp(f"{start}-07-01")  # mid-year
    elif len(start) == 7:  # YYYY-MM
        return pd.Timestamp(f"{start}-15")  # mid-month
    return pd.Timestamp(start)


def get_events_for_topic(topic):
    """Return a DataFrame of reference events for a given topic Label."""
    events = [e for e in REFERENCE_EVENTS if e["topic"] == topic]
    if not events:
        return pd.DataFrame()
    df = pd.DataFrame(events)
    df["date"] = df["period"].apply(parse_period_start)
    return df


def get_events_for_topic_and_adm1(topic, adm1_name):
    """Return events matching both topic and ADM1 (or national-level events)."""
    events = []
    for e in REFERENCE_EVENTS:
        if e["topic"] != topic:
            continue
        if e["adm1"] is None:
            # National-level event: show for all ADM1s
            events.append(e)
        elif adm1_name and adm1_name in str(e["adm1"]):
            events.append(e)
    if not events:
        return pd.DataFrame()
    df = pd.DataFrame(events)
    df["date"] = df["period"].apply(parse_period_start)
    return df
