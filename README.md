# IMF Capacity Development Dashboard

![IMF CD Dashboard](IMF%20CD%20Dashboard.png)

A Python script pulls economic indicators from the IMF and World Bank APIs for 25 member countries (2018-2024) and writes a single CSV. That CSV feeds a Power BI dashboard used to look at GDP growth, inflation, fiscal metrics, and related series across regions, including around the COVID-19 period.

**What the dashboard shows**
- GDP growth trends by country and region
- Regional patterns (Latin America, Africa, Asia, Europe, Middle East)
- COVID-19 impact on key indicators (2020-2021)
- Full span 2018 through 2024

**Technologies**
- Power BI (visualization)
- Python 3, pandas (data pipeline)
- IMF DataMapper API and World Bank API (no API keys)

**View dashboard**  
The report is exported as a PDF and included in this repo (`IMF_Capacity_Development_Dashboard.pdf`). Open it to view the visuals.

**Contents**
- `IMF CD Dashboard.png` – Screenshot of the dashboard
- `IMF_Capacity_Development_Dashboard.pdf` – Power BI export of the dashboard
- `fetch_economic_data.py` – Script that fetches from the APIs and outputs CSV
- `data/economic_data_master_20260127_231830.csv` – Dataset used in the dashboard
- `requirements.txt` – Python dependencies

**Run the script**
```bash
pip install -r requirements.txt
python3 fetch_economic_data.py
```
Output CSVs are written to a `data/` folder.

This was put together in January 2026 as part of my application to the IMF Institute for Capacity Development.
