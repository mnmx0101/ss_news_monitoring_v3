"""
IPC Phase 5 / critical escalation events for South Sudan.
Used to overlay validation events on the media monitoring line graphs.
"""

import pandas as pd

IPC_VALIDATION_EVENTS = [
    {
        "event_id": "JON_2020_FLOOD_FAMINE",
        "description": "Jonglei flooding, displacement & Phase 5 food crisis",
        "labels": ["Food Crisis", "Weather Conditions", "Forced Displacements"],
        "adm1_names": ["Jonglei"],
        "adm2_names": ["Akobo", "Duk", "Ayod"],
        "start_yearmonth": "2020-01",
        "end_yearmonth": "2020-07",
        "ipc_phase": 5,
        "source": "IPC_SouthSudan_AFI_AMN_2020Jan2020July.pdf",
    },
    {
        "event_id": "GPAA_2020_VIOLENCE",
        "description": "Greater Pibor coordinated attacks, mass displacement",
        "labels": ["Conflict and Violence", "Forced Displacements", "Humanitarian Aid"],
        "adm1_names": ["Jonglei"],
        "adm2_names": ["Pibor"],
        "start_yearmonth": "2020-02",
        "end_yearmonth": "2021-07",
        "ipc_phase": 5,
        "source": "IPC_South_Sudan_Famine_Review_2020Nov.pdf",
    },
    {
        "event_id": "UN_2025_NASIR_FAMINE_RISK",
        "description": "Upper Nile airstrikes, cholera, Risk of Famine",
        "labels": ["Conflict and Violence", "Food Crisis", "Environment Issues"],
        "adm1_names": ["Upper Nile"],
        "adm2_names": ["Longochuk", "Ulang"],
        "start_yearmonth": "2025-04",
        "end_yearmonth": "2026-07",
        "ipc_phase": 5,
        "source": "IPC_South_Sudan_Acute_Food_Insecurity_Malnutrition_April_July2025_Report.pdf",
    },
    {
        "event_id": "UNITY_2023_RUBKONA_FLOOD",
        "description": "Rubkona severe flooding, supply chain disruption",
        "labels": ["Weather Conditions", "Environment Issues", "Economic Issues"],
        "adm1_names": ["Unity"],
        "adm2_names": ["Rubkona"],
        "start_yearmonth": "2023-09",
        "end_yearmonth": "2025-07",
        "ipc_phase": 5,
        "source": "IPC_South_Sudan_Acute_Food_Insecurity_Malnutrition_Sep2023_July2024_report.pdf",
    },
    {
        "event_id": "UNITY_2022_LEER_MAYENDIT",
        "description": "Leer/Mayendit floods and armed clashes",
        "labels": ["Food Crisis", "Conflict and Violence", "Weather Conditions"],
        "adm1_names": ["Unity"],
        "adm2_names": ["Leer", "Mayendit"],
        "start_yearmonth": "2022-02",
        "end_yearmonth": "2022-07",
        "ipc_phase": 5,
        "source": "South_Sudan_IPC_Key_Messages_February-July-2022_Report.pdf",
    },
    {
        "event_id": "WEQ_2022_TAMBURA",
        "description": "Tambura inter-communal violence and trade disruption",
        "labels": ["Conflict and Violence", "Production Shortage", "Forced Displacements"],
        "adm1_names": ["Western Equatoria"],
        "adm2_names": ["Tambura"],
        "start_yearmonth": "2022-02",
        "end_yearmonth": "2025-07",
        "ipc_phase": 5,
        "source": "South_Sudan_IPC_Key_Messages_February-July-2022_Report.pdf",
    },
    {
        "event_id": "NBEG_2023_TRADE_CLOSURE",
        "description": "N. Bahr el Ghazal trade closure, dry spells, pests",
        "labels": ["Economic Issues", "Weather Conditions", "Pests and Diseases"],
        "adm1_names": ["Northern Bahr el Ghazal"],
        "adm2_names": ["Aweil North", "Aweil East", "Aweil South", "Aweil West"],
        "start_yearmonth": "2023-09",
        "end_yearmonth": "2025-11",
        "ipc_phase": 5,
        "source": "IPC_South_Sudan_Acute_Food_Insecurity_Malnutrition_Sep2023_July2024_report.pdf",
    },
    {
        "event_id": "LAKES_2022_FLOOD_CONFLICT",
        "description": "Lakes flooding and protracted conflict",
        "labels": ["Weather Conditions", "Conflict and Violence", "Food Crisis"],
        "adm1_names": ["Lakes"],
        "adm2_names": ["Cueibet", "Rumbek North"],
        "start_yearmonth": "2022-02",
        "end_yearmonth": "2022-07",
        "ipc_phase": 4,
        "source": "South_Sudan_IPC_Key_Messages_February-July-2022_Report.pdf",
    },
    {
        "event_id": "WARRAP_2022_CONFLICT",
        "description": "Warrap localized conflicts and cattle raiding",
        "labels": ["Conflict and Violence", "Production Shortage", "Economic Issues"],
        "adm1_names": ["Warrap"],
        "adm2_names": ["Twic", "Tonj East", "Tonj North"],
        "start_yearmonth": "2022-10",
        "end_yearmonth": "2023-07",
        "ipc_phase": 4,
        "source": "IPC_South_Sudan_Acute_Food_Insecurity_Malnutrition_22July_23July_report.pdf",
    },
    {
        "event_id": "EEQ_2022_DROUGHT",
        "description": "Eastern Equatoria drought and livestock migration",
        "labels": ["Weather Conditions", "Pests and Diseases", "Land-related issues"],
        "adm1_names": ["Eastern Equatoria"],
        "adm2_names": ["Kapoeta East", "Kapoeta North"],
        "start_yearmonth": "2022-02",
        "end_yearmonth": "2025-03",
        "ipc_phase": 4,
        "source": "South_Sudan_IPC_Key_Messages_February-July-2022_Report.pdf",
    },
    {
        "event_id": "SUDAN_2023_REFUGEE_INFLUX",
        "description": "Sudan war refugee/returnee influx to border counties",
        "labels": ["Political Instability", "Forced Displacements", "Humanitarian Aid"],
        "adm1_names": ["Upper Nile", "Unity", "Northern Bahr el Ghazal"],
        "adm2_names": ["Renk", "Maban", "Rubkona", "Aweil North", "Aweil East", "Aweil South", "Aweil West"],
        "start_yearmonth": "2023-09",
        "end_yearmonth": "2026-07",
        "ipc_phase": 4,
        "source": "IPC_South_Sudan_Acute_Food_Insecurity_Malnutrition_Sep2023_July2024_report.pdf",
    },
]


def expand_validation_events(events=None, adm_level="adm1"):
    """
    Expand event dictionary into a flat DataFrame.
    adm_level: 'adm1' to match on adm1 only, 'adm2' for adm2-level matching.
    """
    if events is None:
        events = IPC_VALIDATION_EVENTS

    rows = []
    for evt in events:
        months = pd.date_range(
            start=evt["start_yearmonth"],
            end=evt["end_yearmonth"],
            freq="MS",
        ).strftime("%Y-%m").tolist()

        if adm_level == "adm1":
            for adm1 in evt["adm1_names"]:
                for ym in months:
                    for label in evt["labels"]:
                        rows.append({
                            "event_id": evt["event_id"],
                            "adm_name": adm1,
                            "yearmonth": ym,
                            "label": label,
                            "ipc_phase": evt["ipc_phase"],
                            "description": evt["description"],
                            "source": evt["source"],
                        })
        else:
            for adm2 in evt["adm2_names"]:
                for ym in months:
                    for label in evt["labels"]:
                        rows.append({
                            "event_id": evt["event_id"],
                            "adm_name": adm2,
                            "yearmonth": ym,
                            "label": label,
                            "ipc_phase": evt["ipc_phase"],
                            "description": evt["description"],
                            "source": evt["source"],
                        })

    return pd.DataFrame(rows) if rows else pd.DataFrame()
