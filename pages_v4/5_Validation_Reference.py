"""
IPC Validation Reference — Interactive lookup table of known IPC events.
"""
import streamlit as st
import pandas as pd
import io
import re
import os

CSV_PATH = "data/processed/user_ipc_events.csv"

st.title("✅ IPC Validation Reference")
st.markdown(
    "This table provides an exhaustive summary of key historical events across South Sudan by state and county. "
    "**You can add your own known events, edit existing ones, or delete rows.** Make sure to hit **Save Changes** when done! "
    "You can also use the search boxes below to rapidly filter the data."
)

# Raw Markdown table provided by User
RAW_MD = """
| adm1 (State/Region) | adm2 (County) | Event | Description | Period | Source of Report |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Jonglei (incl. Greater Pibor)** | Akobo, Duk, Ayod, Pibor, Twic East, Bor South | **Weather Conditions**, **Food Crisis**, **Conflict and Violence**, **Economic Issues** | Extensive flooding damaged homes, destroyed crops, and resulted in Catastrophe (IPC Phase 5) food insecurity for 40,000 people in Akobo, Duk, and Ayod. High food prices, cattle raiding, and intercommunal conflict disrupted livelihoods. | Jan 2020 – July 2020 | IPC_SouthSudan_AFI_AMN_2020Jan2020July.pdf |
| **Jonglei (incl. Greater Pibor)** | Gumuruk, Pibor, Lekuangole, Verteth, Kiziongora, Marow | **Conflict and Violence**, **Forced Displacements**, **Food Crisis**, **Environment Issues** | Unprecedented, coordinated sub-national attacks targeted civilians and infrastructure, displacing over 60,000 people and prompting Famine Likely conditions in western payams. Second waves of flooding further destroyed livelihoods and restricted game migration. | Oct 2020 – July 2021 | IPC_South_Sudan_Famine_Review_2020Nov.pdf |
| **Jonglei (incl. Greater Pibor)** | Fangak, Canal/Pigi, Ayod, Pibor, Uror | **Weather Conditions**, **Food Crisis**, **Environment Issues**, **Humanitarian Aid** | A third consecutive year of unprecedented flooding submerged settlements and pasturelands, leading to 67,000 people falling into Catastrophe (IPC Phase 5). Floods disrupted the delivery of humanitarian assistance and contaminated water sources. | Feb 2022 – July 2022 | South_Sudan_IPC_Key_Messages_February-July-2022_Report.pdf |
| **Jonglei (incl. Greater Pibor)** | Akobo, Canal/Pigi, Fangak, Pibor | **Conflict and Violence**, **Weather Conditions**, **Food Crisis** | Ongoing subnational conflict along the River Nile caused massive displacements and destruction of humanitarian facilities, placing 61,000 people in Catastrophe (IPC Phase 5). Heavy rains in the Ethiopian highlands compounded flooding. | Oct 2022 – July 2023 | IPC_South_Sudan_Acute_Food_Insecurity_Malnutrition_22July_23July_report.pdf |
| **Jonglei (incl. Greater Pibor)** | Duk, Nyirol, Akobo, Ayod, Pibor | **Pests and Diseases**, **Conflict and Violence**, **Food Crisis** | Sub-national violence and dry spells resulted in 35,000 people facing Catastrophe (IPC Phase 5). Crop damage from pests (fall armyworm, birds) and livestock diseases further reduced asset holdings. | Sept 2023 – July 2024 | IPC_South_Sudan_Acute_Food_Insecurity_Malnutrition_Sep2023_July2024_report.pdf |
| **Jonglei (incl. Greater Pibor)** | Fangak, Nyirol, Pibor, Uror, Twic East | **Weather Conditions**, **Conflict and Violence**, **Food Crisis** | Above-average rainfall and flooding displaced families, while intercommunal violence restricted market access. 22,000 people in Pibor and Uror faced Catastrophe (IPC Phase 5). | Sept 2024 – July 2025 | IPC_South_Sudan_Acute_Food_Insecurity_Malnutrition_Sep2024_July2025_Report.pdf |
| **Jonglei (incl. Greater Pibor)** | Pibor, Fangak, Twic East, Bor South | **Conflict and Violence**, **Weather Conditions**, **Food Crisis**, **Pests and Diseases** | Intercommunal violence, widespread flooding, and disease outbreaks reduced access to food, leading to 11,000 people in Fangak facing Catastrophe (IPC Phase 5). | Sept 2025 – July 2026 | IPC_South_Sudan_Acute_Food_Insecurity_Malnutrition_Sep2025_July2026_Report.pdf |
| **Upper Nile** | Maiwut, Longochuk, Ulang, Maban | **Weather Conditions**, **Conflict and Violence**, **Food Crisis** | Excessive flooding caused displacement, crop destruction, and market disruption, pushing counties into Emergency (IPC Phase 4). Sporadic insecurity drove food gaps in Maiwut. | Jan 2020 – July 2020 | IPC_SouthSudan_AFI_AMN_2020Jan2020July.pdf |
| **Upper Nile** | Baliet, Fashoda, Longochuk, Laukpiny/Nasir, Malakal | **Weather Conditions**, **Pests and Diseases**, **Economic Issues** | Severe floods destroyed crops and disrupted markets. Floods triggered increased livestock disease outbreaks and crop pests, while high food prices reduced purchasing power. | Feb 2022 – July 2022 | South_Sudan_IPC_Key_Messages_February-July-2022_Report.pdf |
| **Upper Nile** | Malakal, Nassir, Melut, Renk | **Weather Conditions**, **Conflict and Violence**, **Economic Issues** | Heavy rains in the Ethiopian Highlands re-started severe flooding in the Sobat basin. Ongoing conflict along the Upper Nile-Jonglei border caused large-scale displacement, pushing up the cost of the food basket. | Oct 2022 – July 2023 | IPC_South_Sudan_Acute_Food_Insecurity_Malnutrition_22July_23July_report.pdf |
| **Upper Nile** | Malakal, Panyikang, Renk, Fashoda | **Political Instability**, **Forced Displacements**, **Economic Issues** | The ongoing crisis in Sudan disrupted market functioning and trade, resulting in massive influxes of returnees and refugees. Market supplies from Sudan were entirely cut off. | Sept 2023 – July 2024 | IPC_South_Sudan_Acute_Food_Insecurity_Malnutrition_Sep2023_July2024_report.pdf |
| **Upper Nile** | Luakpiny/Nasir, Panyikang, Malakal | **Forced Displacements**, **Economic Issues**, **Food Crisis** | Trade disruptions from the Sudan crisis led to unusually high food prices. Returnees and refugees continued to strain local resources, putting 10,000 people in Malakal into Catastrophe (IPC Phase 5). | Sept 2024 – July 2025 | IPC_South_Sudan_Acute_Food_Insecurity_Malnutrition_Sep2024_July2025_Report.pdf |
| **Upper Nile** | Luakpiny/Nasir, Ulang, Malakal | **Conflict and Violence**, **Pests and Diseases**, **Food Crisis** | Armed violence and airstrikes displaced 20-25% of populations. A deadly cholera outbreak with high fatality rates severely worsened acute malnutrition, driving a Risk of Famine in Nasir and Ulang. | April 2025 – July 2025 | IPC_South_Sudan_Acute_Food_Insecurity_Malnutrition_April_July2025_Report.pdf |
| **Upper Nile** | Luakpiny/Nasir, Ulang, Longochuk, Panyikang | **Conflict and Violence**, **Food Crisis**, **Pests and Diseases** | Unprecedented violence, airstrikes, and a severe cholera outbreak sustained a Risk of Famine in Luakpiny/Nasir. 17,000 people faced Catastrophe (IPC Phase 5) due to destroyed supply routes. | Sept 2025 – July 2026 | IPC_South_Sudan_Acute_Food_Insecurity_Malnutrition_Sep2025_July2026_Report.pdf |
| **Unity (incl. Ruweng)** | Leer, Mayendit, Panyijiar, Guit, Rubkona | **Weather Conditions**, **Conflict and Violence**, **Food Crisis** | Floods caused significant loss of crops and livestock. Armed clashes, revenge killing, and cattle rustling placed 7,000 people in Leer and Mayendit in Catastrophe (IPC Phase 5). | Feb 2022 – July 2022 | South_Sudan_IPC_Key_Messages_February-July-2022_Report.pdf |
| **Unity (incl. Ruweng)** | Leer, Mayendit, Rubkona, Mayom | **Weather Conditions**, **Conflict and Violence**, **Food Crisis** | Drier-than-average conditions delayed planting, while central Unity was submerged by floods. Breached dykes in Rubkona destroyed trade flows, putting populations in Catastrophe (IPC Phase 5). | Oct 2022 – July 2023 | IPC_South_Sudan_Acute_Food_Insecurity_Malnutrition_22July_23July_report.pdf |
| **Unity (incl. Ruweng)** | Rubkona, Guit, Koch, Leer, Mayendit | **Weather Conditions**, **Forced Displacements**, **Food Crisis** | Catastrophe (IPC Phase 5) hit 15,000 people in Rubkona due to flooding, a lack of dry land, supply chain disruptions from Sudan, and the influx of returnees. | Sept 2023 – July 2024 | IPC_South_Sudan_Acute_Food_Insecurity_Malnutrition_Sep2023_July2024_report.pdf |
| **Unity (incl. Ruweng)** | Rubkona, Abiemnhom, Guit, Koch | **Weather Conditions**, **Economic Issues**, **Food Crisis** | Protracted flooding substantially reduced agricultural engagement. The macroeconomic crisis caused currency depreciation and unusually high food prices. | Sept 2024 – July 2025 | IPC_South_Sudan_Acute_Food_Insecurity_Malnutrition_Sep2024_July2025_Report.pdf |
| **Unity (incl. Ruweng)** | Rubkona, Guit, Leer, Mayendit, Panyijiar | **Economic Issues**, **Forced Displacements**, **Humanitarian Aid** | Increased market dependency amid high prices. A significant scale-up in Humanitarian Food Assistance (HFA) prevented further deterioration in Rubkona. | April 2025 – July 2025 | IPC_South_Sudan_Acute_Food_Insecurity_Malnutrition_April_July2025_Report.pdf |
| **Unity (incl. Ruweng)** | Rubkona, Leer, Koch, Mayendit | **Weather Conditions**, **Forced Displacements**, **Pests and Diseases** | Widespread flooding destroyed crops and displaced populations, leading to IPC AMN Phase 5 (Extremely Critical) acute malnutrition in Rubkona. | Sept 2025 – July 2026 | IPC_South_Sudan_Acute_Food_Insecurity_Malnutrition_Sep2025_July2026_Report.pdf |
| **Western Equatoria** | Nagero, Mundri East, Yambio | **Weather Conditions**, **Production Shortage**, **Forced Displacements** | Relative calm and above-average rainfall boosted crop production, though high food prices and refugee returnees kept some populations in Crisis (IPC Phase 3). | Jan 2020 – July 2020 | IPC_SouthSudan_AFI_AMN_2020Jan2020July.pdf |
| **Western Equatoria** | Tambura, Mundri East, Mvolo, Nagero | **Conflict and Violence**, **Economic Issues**, **Food Crisis** | Inter-communal violence and trade flow disruptions led to Catastrophe (IPC Phase 5) for 6,000 people in Tambura. | Feb 2022 – July 2022 | South_Sudan_IPC_Key_Messages_February-July-2022_Report.pdf |
| **Western Equatoria** | Mundri East, Mundri West, Mvolo, Nagero | **Weather Conditions**, **Production Shortage**, **Economic Issues** | Climate shocks (floods and dry spells), low crop production, and major trade flow disruptions drove high food insecurity. | Oct 2022 – July 2023 | IPC_South_Sudan_Acute_Food_Insecurity_Malnutrition_22July_23July_report.pdf |
| **Western Equatoria** | Mundri East, Mvolo, Nagero, Tambura | **Conflict and Violence**, **Weather Conditions**, **Pests and Diseases** | Insecurity, looting, dry spells, weed and pest infestations, and lack of tools negatively impacted crop production. | Sept 2023 – July 2024 | IPC_South_Sudan_Acute_Food_Insecurity_Malnutrition_Sep2023_July2024_report.pdf |
| **Western Equatoria** | Tambura, Mundri East, Mvolo, Nagero | **Conflict and Violence**, **Pests and Diseases**, **Economic Issues** | Localized insecurity (especially in Tambura), prolonged dry spells, crop pest outbreaks, and high staple food prices constrained agricultural production. | Sept 2024 – July 2025 | IPC_South_Sudan_Acute_Food_Insecurity_Malnutrition_Sep2024_July2025_Report.pdf |
| **Western Equatoria** | Nagero, Tambura | **Forced Displacements**, **Conflict and Violence** | An influx of IDPs from Tambura, along with ongoing insecurity restricting access to livelihoods, drove deterioration in Nagero. | April 2025 – July 2025 | IPC_South_Sudan_Acute_Food_Insecurity_Malnutrition_April_July2025_Report.pdf |
| **Western Equatoria** | Tambura, Mundri East, Mvolo, Nagero | **Conflict and Violence**, **Weather Conditions**, **Pests and Diseases** | Localised conflict, weed infestations, and crop pests reduced first-season harvests, while dry spells further constrained yields. | Sept 2025 – July 2026 | IPC_South_Sudan_Acute_Food_Insecurity_Malnutrition_Sep2025_July2026_Report.pdf |
| **Central Equatoria** | Juba, Terekeka, Kajo Keji, Yei | **Production Shortage**, **Conflict and Violence**, **Economic Issues** | Low crop production, insecurity between cattle keepers and farmers, and degraded road conditions drove high food prices. | Feb 2022 – July 2022 | South_Sudan_IPC_Key_Messages_February-July-2022_Report.pdf |
| **Central Equatoria** | Juba, Kajo Keji, Lainya, Morobo | **Conflict and Violence**, **Pests and Diseases**, **Land-related issues** | Inter-communal conflicts between cattle keepers and farmers restricted movement, while crop and livestock pests reduced yields. | Oct 2022 – July 2023 | IPC_South_Sudan_Acute_Food_Insecurity_Malnutrition_22July_23July_report.pdf |
| **Central Equatoria** | Juba, Kajo Keji, Lainya, Morobo | **Conflict and Violence**, **Weather Conditions**, **Pests and Diseases** | Conflict, raiding, violence, dry spells, and weed/pest infestations impacted negative on the first season harvest. | Sept 2023 – July 2024 | IPC_South_Sudan_Acute_Food_Insecurity_Malnutrition_Sep2023_July2024_report.pdf |
| **Central Equatoria** | Juba, Kajo Keji, Terekeka | **Economic Issues**, **Weather Conditions**, **Conflict and Violence** | Unusually high food prices, prolonged dry spells during the first season, and localized banditry constrained households. | Sept 2024 – July 2025 | IPC_South_Sudan_Acute_Food_Insecurity_Malnutrition_Sep2024_July2025_Report.pdf |
| **Central Equatoria** | Juba, Kajo Keji, Lainya, Morobo | **Economic Issues**, **Conflict and Violence**, **Weather Conditions** | Active conflict and unpredictable weather restricted population movement and trade flows, driving high food prices. | April 2025 – July 2025 | IPC_South_Sudan_Acute_Food_Insecurity_Malnutrition_April_July2025_Report.pdf |
| **Central Equatoria** | Juba, Lainya, Terekeka, Yei | **Production Shortage**, **Economic Issues**, **Forced Displacements** | A cereal deficit from the 2024 season and hyperinflation eroded purchasing power. The influx of IDPs and returnees strained limited resources. | Sept 2025 – July 2026 | IPC_South_Sudan_Acute_Food_Insecurity_Malnutrition_Sep2025_July2026_Report.pdf |
| **Eastern Equatoria** | Kapoeta North, Budi | **Environment Issues**, **Weather Conditions** | Normal to above-normal rainfall expected to bring seasonal availability of wild foods, fruit, and pasture for semi-arid areas. | Jan 2020 – July 2020 | IPC_SouthSudan_AFI_AMN_2020Jan2020July.pdf |
| **Eastern Equatoria** | Kapoeta East, Kapoeta North, Lafon, Torit | **Weather Conditions**, **Production Shortage**, **Conflict and Violence** | Drought conditions caused low crop production, compounded by insecurity and livestock diseases. | Feb 2022 – July 2022 | South_Sudan_IPC_Key_Messages_February-July-2022_Report.pdf |
| **Eastern Equatoria** | Kapoeta East, Budi, Ikotos, Lafon | **Weather Conditions**, **Land-related issues**, **Pests and Diseases** | Prolonged dry spells induced atypical long-distance livestock migrations and high levels of crop pests and diseases. | Oct 2022 – July 2023 | IPC_South_Sudan_Acute_Food_Insecurity_Malnutrition_22July_23July_report.pdf |
| **Eastern Equatoria** | Lafon, Budi, Ikotos, Kapoeta East | **Weather Conditions**, **Production Shortage**, **Pests and Diseases** | Dry spells, weed/pest infestations, and a lack of agricultural tools caused crop failure and poor pastures for livestock. | Sept 2023 – July 2024 | IPC_South_Sudan_Acute_Food_Insecurity_Malnutrition_Sep2023_July2024_report.pdf |
| **Eastern Equatoria** | Kapoeta East, Kapoeta North, Lafon | **Weather Conditions**, **Land-related issues**, **Conflict and Violence** | Significant cereal deficits from dry spells forced seasonal livestock migration, disrupting household access to food, compounded by cattle raids. | Sept 2024 – July 2025 | IPC_South_Sudan_Acute_Food_Insecurity_Malnutrition_Sep2024_July2025_Report.pdf |
| **Eastern Equatoria** | Kapoeta East, Lafon | **Economic Issues**, **Production Shortage**, **Conflict and Violence** | High food prices driven by low production, highway robberies, farmer-herder conflicts, and cattle raiding. | April 2025 – July 2025 | IPC_South_Sudan_Acute_Food_Insecurity_Malnutrition_April_July2025_Report.pdf |
| **Eastern Equatoria** | Lafon, Kapoeta East, Kapoeta North | **Weather Conditions**, **Forced Displacements**, **Conflict and Violence** | A prolonged dry spell and an influx of returnees from Uganda and Kenya strained resources, while cattle raiding disrupted trade. | Sept 2025 – July 2026 | IPC_South_Sudan_Acute_Food_Insecurity_Malnutrition_Sep2025_July2026_Report.pdf |
| **Northern Bahr el Ghazal** | Aweil North, Aweil West | **Weather Conditions**, **Production Shortage**, **Conflict and Violence** | Cereal production was 22% below 2018 levels due to flooding and inter-communal conflict disrupting access to markets. | Jan 2020 – July 2020 | IPC_SouthSudan_AFI_AMN_2020Jan2020July.pdf |
| **Northern Bahr el Ghazal** | Aweil East, Aweil North, Aweil West | **Conflict and Violence**, **Production Shortage**, **Pests and Diseases** | Conflicts along the Sudan border caused displacement, while floods, pests, and limited pastures reduced cereal and milk production. | Feb 2022 – July 2022 | South_Sudan_IPC_Key_Messages_February-July-2022_Report.pdf |
| **Northern Bahr el Ghazal** | Aweil East, Aweil South | **Political Instability**, **Economic Issues**, **Pests and Diseases** | Closure of the trade route between South Sudan and Sudan led to unusually high prices, compounded by flooding and livestock diseases. | Oct 2022 – July 2023 | IPC_South_Sudan_Acute_Food_Insecurity_Malnutrition_22July_23July_report.pdf |
| **Northern Bahr el Ghazal** | Aweil East, Aweil South, Aweil North | **Political Instability**, **Food Crisis**, **Forced Displacements** | Continued closure of Sudan trade routes and influx of returnees drove 40,000 people in Aweil East into Catastrophe (IPC Phase 5) by April 2024. | Sept 2023 – July 2024 | IPC_South_Sudan_Acute_Food_Insecurity_Malnutrition_Sep2023_July2024_report.pdf |
| **Northern Bahr el Ghazal** | Aweil North, Aweil East, Aweil South | **Economic Issues**, **Weather Conditions**, **Forced Displacements** | The economic crisis, irregular rainfall/floods/dry spells, high fuel transport prices, and Sudan returnees eroded household access to food. | Sept 2024 – July 2025 | IPC_South_Sudan_Acute_Food_Insecurity_Malnutrition_Sep2024_July2025_Report.pdf |
| **Northern Bahr el Ghazal** | Aweil Centre, Aweil North, Aweil East | **Economic Issues**, **Forced Displacements**, **Weather Conditions** | Currency devaluation, hyperinflation, and high numbers of returnees from Sudan severely impacted food stocks and access. | April 2025 – July 2025 | IPC_South_Sudan_Acute_Food_Insecurity_Malnutrition_April_July2025_Report.pdf |
| **Northern Bahr el Ghazal** | Aweil East, Aweil North, Aweil South | **Economic Issues**, **Weather Conditions**, **Pests and Diseases** | Persistently high food prices, irregular rainfall/floods, crop/livestock pest infestations, and the Sudan conflict spillover severely constrained production. | Sept 2025 – July 2026 | IPC_South_Sudan_Acute_Food_Insecurity_Malnutrition_Sep2025_July2026_Report.pdf |
| **Western Bahr el Ghazal** | Wau, Jur River | **Production Shortage** (Increase) | Cereal production reportedly increased by 29%, contributing to localized stability and slightly better food stocks than 2019. | Jan 2020 – July 2020 | IPC_SouthSudan_AFI_AMN_2020Jan2020July.pdf |
| **Western Bahr el Ghazal** | Wau, Jur River, Raga | **Economic Issues**, **Weather Conditions**, **Forced Displacements** | Macroeconomic shocks increased market prices, while prolonged dry spells, crop pests, and IDP/returnee arrivals strained resources. | Feb 2022 – July 2022 | South_Sudan_IPC_Key_Messages_February-July-2022_Report.pdf |
| **Western Bahr el Ghazal** | Wau, Jur River, Raja | **Forced Displacements**, **Economic Issues**, **Conflict and Violence** | IDP returnees placed pressure on resources, while currency depreciation and conflict between farmers and encroaching cattle keepers reduced food access. | Oct 2022 – July 2023 | IPC_South_Sudan_Acute_Food_Insecurity_Malnutrition_22July_23July_report.pdf |
| **Western Bahr el Ghazal** | Wau, Jur River, Raga | **Economic Issues**, **Pests and Diseases**, **Weather Conditions** | High food prices, crop/livestock pests, and irregular rainfall/dry spells severely affected agricultural activities and food flows. | Sept 2023 – July 2024 | IPC_South_Sudan_Acute_Food_Insecurity_Malnutrition_Sep2023_July2024_report.pdf |
| **Western Bahr el Ghazal** | Wau, Jur River, Raga | **Economic Issues**, **Weather Conditions**, **Conflict and Violence** | Loss of employment/reduced household income, irregular rainfall, and insecurity from cattle keepers encroaching into Jur River elevated prices. | Sept 2024 – July 2025 | IPC_South_Sudan_Acute_Food_Insecurity_Malnutrition_Sep2024_July2025_Report.pdf |
| **Western Bahr el Ghazal** | Wau, Jur River, Raga | **Economic Issues**, **Weather Conditions**, **Conflict and Violence** | High food prices, loss of jobs, dry spells, and conflicts between communities and cattle herders from Warrap State disrupted livelihoods. | Sept 2025 – July 2026 | IPC_South_Sudan_Acute_Food_Insecurity_Malnutrition_Sep2025_July2026_Report.pdf |
| **Lakes** | Rumbek North, Rumbek East, Cueibet | **Weather Conditions**, **Conflict and Violence** | Inter-communal violence disrupted livelihoods, keeping Rumbek North in Emergency (IPC Phase 4) alongside ongoing flood impacts. | Jan 2020 – July 2020 | IPC_SouthSudan_AFI_AMN_2020Jan2020July.pdf |
| **Lakes** | Cueibet, Rumbek North, Rumbek East | **Food Crisis**, **Weather Conditions**, **Conflict and Violence** | Devastating floods followed prolonged dry spells, and protracted violence from neighboring states placed 13,000 people into Catastrophe (IPC Phase 5). | Feb 2022 – July 2022 | South_Sudan_IPC_Key_Messages_February-July-2022_Report.pdf |
| **Lakes** | Cueibet, Rumbek Centre, Rumbek East | **Pests and Diseases**, **Weather Conditions**, **Economic Issues** | Crop pests and diseases, alongside floods and dry spells on agriculture, combined with reduced incomes and high food prices. | Oct 2022 – July 2023 | IPC_South_Sudan_Acute_Food_Insecurity_Malnutrition_22July_23July_report.pdf |
| **Lakes** | Cueibet, Rumbek Centre, Yirol West | **Economic Issues**, **Weather Conditions**, **Production Shortage** | High food prices, prolonged dry spells, depleted stocks from previous poor harvests, and low household incomes drove Crisis (IPC Phase 3) outcomes. | Sept 2023 – July 2024 | IPC_South_Sudan_Acute_Food_Insecurity_Malnutrition_Sep2023_July2024_report.pdf |
| **Lakes** | Awerial, Rumbek North, Yirol East | **Economic Issues**, **Weather Conditions**, **Conflict and Violence** | High food prices, dry spells, localized flooding, cattle raiding, and crop/livestock pests eroded household incomes and food sources. | Sept 2024 – July 2025 | IPC_South_Sudan_Acute_Food_Insecurity_Malnutrition_Sep2024_July2025_Report.pdf |
| **Lakes** | Rumbek North, Awerial, Cueibet | **Economic Issues**, **Environment Issues** | Depletion of food stocks, high market prices due to hyperinflation, and inaccessible roads due to the rainy season constrained supplies. | April 2025 – July 2025 | IPC_South_Sudan_Acute_Food_Insecurity_Malnutrition_April_July2025_Report.pdf |
| **Lakes** | Awerial, Rumbek North, Yirol East | **Weather Conditions**, **Conflict and Violence**, **Pests and Diseases** | Dry spells, localized flooding, insecurity, cattle raiding, and livestock diseases resulted in deterioration to Emergency (IPC Phase 4) during the lean season. | Sept 2025 – July 2026 | IPC_South_Sudan_Acute_Food_Insecurity_Malnutrition_Sep2025_July2026_Report.pdf |
| **Warrap (incl. Abyei)** | Tonj East, Tonj South | **Weather Conditions**, **Land-related issues**, **Conflict and Violence** | Flooding negatively affected crop production, while livestock migrated away from homesteads and ongoing insecurity restricted market/agricultural access. | Jan 2020 – July 2020 | IPC_SouthSudan_AFI_AMN_2020Jan2020July.pdf |
| **Warrap (incl. Abyei)** | Gogrial East, Tonj North, Twic | **Conflict and Violence**, **Weather Conditions** | Sub-national conflicts and cattle raiding disrupted agricultural activities, compounded by prolonged dry spells and floods limiting pasture. | Feb 2022 – July 2022 | South_Sudan_IPC_Key_Messages_February-July-2022_Report.pdf |
| **Warrap (incl. Abyei)** | Abyei, Twic, Gogrial East | **Conflict and Violence**, **Pests and Diseases**, **Weather Conditions** | Insecurity in the Amiet/Abyei region drove deterioration. Animal disease outbreaks, floods, and dry spells severely reduced household incomes. | Oct 2022 – July 2023 | IPC_South_Sudan_Acute_Food_Insecurity_Malnutrition_22July_23July_report.pdf |
| **Warrap (incl. Abyei)** | Twic, Gogrial East, Tonj East | **Economic Issues**, **Weather Conditions**, **Pests and Diseases** | Unusually high food prices, dry spells, human/animal illnesses, and an influx of returnees fleeing Sudan placed massive strain on the area. | Sept 2023 – July 2024 | IPC_South_Sudan_Acute_Food_Insecurity_Malnutrition_Sep2023_July2024_report.pdf |
| **Warrap (incl. Abyei)** | Twic, Gogrial East, Tonj East | **Economic Issues**, **Weather Conditions**, **Conflict and Violence** | Unpredictable weather (floods and prolonged dry spells), cattle raiding, and highly disrupted supply chains from Sudan eroded food security. | Sept 2024 – July 2025 | IPC_South_Sudan_Acute_Food_Insecurity_Malnutrition_Sep2024_July2025_Report.pdf |
| **Warrap (incl. Abyei)** | Tonj East, Tonj North, Twic | **Weather Conditions**, **Economic Issues**, **Forced Displacements** | Climatic shocks from widespread 2024 flooding, early stock depletion, and hyperinflation collided with massive influxes of people fleeing Sudan. | April 2025 – July 2025 | IPC_South_Sudan_Acute_Food_Insecurity_Malnutrition_April_July2025_Report.pdf |
| **Warrap (incl. Abyei)** | Tonj East, Tonj North, Twic, Abyei | **Weather Conditions**, **Conflict and Violence**, **Food Crisis** | Flooding, dry spells, and cattle raiding devastated markets. Acute malnutrition in Abyei slipped into IPC Phase 5 (Extremely Critical) due to conflict. | Sept 2025 – July 2026 | IPC_South_Sudan_Acute_Food_Insecurity_Malnutrition_Sep2025_July2026_Report.pdf |
| **Returnees (National)** | Sudan Border Areas, Transit Centers | **Forced Displacements**, **Food Crisis**, **Political Instability** | 280,000 returnees from the Sudan conflict lacked harvests or assets; 14,000 faced Catastrophe (IPC Phase 5) food insecurity. | Sept 2023 – July 2024 | IPC_South_Sudan_Acute_Food_Insecurity_Malnutrition_Sep2023_July2024_report.pdf |
| **Returnees (National)** | Sudan Border Areas, Transit Centers | **Forced Displacements**, **Food Crisis** | Over 629,000 returnees analysed, with an estimated 31,000 facing Catastrophe (IPC Phase 5) conditions as border communities were overwhelmed. | Sept 2024 – July 2025 | IPC_South_Sudan_Acute_Food_Insecurity_Malnutrition_Sep2024_July2025_Report.pdf |
| **Returnees (National)** | Sudan Border Areas, Transit Centers | **Forced Displacements**, **Food Crisis** | The number of people returning from Sudan continued to swell, placing 39,000 returnees in Catastrophe (IPC Phase 5) across the country. | April 2025 – July 2025 | IPC_South_Sudan_Acute_Food_Insecurity_Malnutrition_April_July2025_Report.pdf |
"""

@st.cache_data
def load_default_validation_data():
    lines = RAW_MD.strip().split("\n")
    data_lines = lines[2:]
    parsed = []
    for row in data_lines:
        cells = [c.strip() for c in row.split("|")[1:-1]]
        if len(cells) == 6:
            cells = [re.sub(r'[*_]', '', c) for c in cells]
            parsed.append(cells)
    df = pd.DataFrame(parsed, columns=[
        "State/Region (ADM1)", "County (ADM2)", "Events & Topics", 
        "Description", "Period", "Source Document"
    ])
    return df

def load_validation_data():
    if os.path.exists(CSV_PATH):
        return pd.read_csv(CSV_PATH)
    else:
        # Need to cast to string so edits work consistently
        df = load_default_validation_data()
        for col in df.columns:
            df[col] = df[col].astype(str)
        return df

if "ipc_df" not in st.session_state:
    st.session_state["ipc_df"] = load_validation_data()

st.markdown("### 📝 Edit Validation Events")
st.caption("Double-click any cell to edit. Scroll to the bottom and click + to add a row.")

edited_df = st.data_editor(
    st.session_state["ipc_df"],
    num_rows="dynamic",
    use_container_width=True,
    height=400,
    column_config={
        "State/Region (ADM1)": st.column_config.TextColumn(width="small"),
        "County (ADM2)": st.column_config.TextColumn(width="medium"),
        "Events & Topics": st.column_config.TextColumn(width="medium"),
        "Description": st.column_config.TextColumn(width="large"),
        "Period": st.column_config.TextColumn(width="small"),
        "Source Document": st.column_config.TextColumn(width="medium"),
    },
    hide_index=True,
    key="ipc_editor"
)

if st.button("💾 Save Changes", type="primary"):
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    edited_df.to_csv(CSV_PATH, index=False)
    st.session_state["ipc_df"] = edited_df.copy()
    st.success("Changes saved successfully to `data/processed/user_ipc_events.csv`!")

st.markdown("---")

# Build interactive filters
st.markdown("### 🔍 Search & Filter (Read-Only View)")
c1, c2, c3 = st.columns(3)

with c1:
    states = ["All"] + sorted(st.session_state["ipc_df"]["State/Region (ADM1)"].dropna().astype(str).unique().tolist())
    search_state = st.selectbox("Filter by State/Region", states)

with c2:
    search_county = st.text_input("Search by County", placeholder="e.g. Fangak").strip().lower()

with c3:
    search_event = st.text_input("Search by Topic/Event", placeholder="e.g. Food Crisis").strip().lower()

# Apply filters
filtered_df = st.session_state["ipc_df"].copy()
if search_state != "All":
    filtered_df = filtered_df[filtered_df["State/Region (ADM1)"].astype(str) == search_state]
if search_county:
    filtered_df = filtered_df[filtered_df["County (ADM2)"].astype(str).str.lower().str.contains(search_county, na=False)]
if search_event:
    filtered_df = filtered_df[filtered_df["Events & Topics"].astype(str).str.lower().str.contains(search_event, na=False)]

st.markdown(f"**Found: {len(filtered_df)} recorded validation instances matching your search.**")

st.dataframe(
    filtered_df,
    use_container_width=True,
    height=400,
    column_config={
        "State/Region (ADM1)": st.column_config.TextColumn(width="small"),
        "County (ADM2)": st.column_config.TextColumn(width="medium"),
        "Events & Topics": st.column_config.TextColumn(width="medium"),
        "Description": st.column_config.TextColumn(width="large"),
        "Period": st.column_config.TextColumn(width="small"),
        "Source Document": st.column_config.TextColumn(width="medium"),
    },
    hide_index=True
)
