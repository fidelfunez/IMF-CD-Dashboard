# IMF Capacity Development Dashboard

![IMF CD Dashboard](IMF%20CD%20Dashboard.png)

This is a PowerBI dashboard created specifically for the IMF, as a project for me to showcase my Data Engineering and Data Analyst expertise. In order to do so, I first created a Python script that pulls economic indicators from the IMF and the World Bank APIs for 25 member countries, from the 2018-2024 period and creates a single CSV. That CSV then feeds the Power BI dashboard used to look at GDP growth, inflation, fiscal metrics, and other related series across regions, including around the COVID-19 period.

**What the dashboard shows**
- GDP growth trends by country and region
- Regional patterns (Latin America, Africa, Asia, Europe, Middle East)
- COVID-19 impact on key indicators (2020-2021)
- Full span 2018 through 2024

**Technologies**
- Power BI (for visualization)
- Python 3, pandas (for the data pipeline)
- IMF DataMapper API and World Bank API (no API keys required)

**View dashboard**  
The report is exported as a PDF and included in this repo (`IMF_Capacity_Development_Dashboard.pdf`). Please feel free to open it to view the visuals.

**Contents**
- `IMF CD Dashboard.png` – Screenshot of the dashboard
- `IMF_Capacity_Development_Dashboard.pdf` – Power BI export of the dashboard
- `fetch_economic_data.py` – The script that fetches from the APIs and outputs the CSV
- `data/economic_data_master_20260127_231830.csv` – The dataset used in the dashboard
- `requirements.txt` – The python dependencies I used

**Run the script**
```bash
pip install -r requirements.txt
python3 fetch_economic_data.py
```
Output CSVs are written to a `data/` folder.

This was proudly put together in January 2026, as part of my application to the IMF Institute for Capacity Development. - Fidel Fúnez C.
