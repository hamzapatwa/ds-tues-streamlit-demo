# 🗽 New York State Crime Analytics Dashboard

A Streamlit-powered dashboard for exploring crime trends across New York State counties and agencies from **1990 to 2025**.  
It combines crime data with annual population estimates to calculate both raw counts and per-capita rates, displayed through interactive maps, trends, and rankings.

---

## 🚀 Features

- **Interactive Filters**
  - Year range selection  
  - Choose crime metrics (e.g., violent crime, property crime, larceny, etc.)  
  - Toggle between raw counts and per 100k population rates  

- **Visualizations**
  - **Choropleth Map:** County-level heatmap of crime intensity  
  - **Trends:** Historical statewide trends with selected year ranges highlighted  
  - **Rankings:** Top and bottom counties by chosen metric  
  - **KPIs:** Total crimes and percent change over time  

- **Agency-Level Data**
  - Raw table view by agency, county, and reporting months  

---

## 📂 Data Sources

- **Crime Data:** `Index_Crimes_by_County_and_Agency__Beginning_1990_20250906.csv`  
- **Population Data:** `Annual_Population_Estimates_for_New_York_State_and_Counties__Beginning_1970_20250907.csv`  
- **GeoJSON:** [Plotly US Counties](https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json)  

Both CSV files must be placed in the **same directory** as the Streamlit app.

---

## 🛠️ Tech Stack

- **Python 3.9+**
- [Streamlit](https://streamlit.io/) – UI framework  
- [Pandas](https://pandas.pydata.org/) – Data wrangling  
- [NumPy](https://numpy.org/) – Computation  
- [Plotly Express](https://plotly.com/python/plotly-express/) – Visualizations  
- [Requests](https://docs.python-requests.org/) – Fetching GeoJSON  

---

## ⚡ Quick Start

1. Clone this repo or copy the app file + CSVs into one directory.  
2. Install dependencies:
   ```bash
   pip install -r requirements.txt

Example requirements.txt:

streamlit
pandas
numpy
plotly
requests

	3.	Run the app:

streamlit run app.py


	4.	Open your browser at http://localhost:8501.

⸻

## 📊 Metrics Available
	•	index_total
	•	violent_total
	•	murder
	•	rape
	•	robbery
	•	aggravated_assault
	•	property_total
	•	burglary
	•	larceny
	•	motor_vehicle_theft

**Each metric can also be normalized to per 100k population.**

⸻

## 🔑 Notes
	•	Some county names are normalized (e.g., St Lawrence → St. Lawrence).
	•	Population data is required for per-capita calculations.
	•	If data files are missing, the app will error out with a helpful message.

⸻

## 📌 Roadmap / Possible Improvements
	•	Option to average per-capita rates across year ranges instead of summing.
	•	Expand filters to allow agency-level comparisons.
	•	Add download/export functionality for filtered datasets.
	•	Build time-lapse animations for maps.
