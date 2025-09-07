
# NYS Index Crimes Streamlit Dashboard

## Quick start
1. Put your CSV next to `app.py` and name it:
   `Index_Crimes_by_County_and_Agency__Beginning_1990_20250906.csv`
   (or upload it via the sidebar when the app is running).

2. Install deps:
```bash
pip install -r requirements.txt
```

3. Launch:
```bash
streamlit run app.py
```

## Notes
- Year slider is auto-bounded by the data (1990–2024).
- Map uses a public NY counties GeoJSON; names are matched by county. If a county doesn't color, check the name in your CSV and add it to `alias_map` in `app.py`.
- Use the sidebar to change metric and filter counties.
