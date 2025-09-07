import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import requests

# --- Page Configuration ---
st.set_page_config(layout="wide")

# --- Constants & Configuration ---
CRIMES_PATH = "Index_Crimes_by_County_and_Agency__Beginning_1990_20250906.csv"
POPULATION_PATH = "Annual_Population_Estimates_for_New_York_State_and_Counties__Beginning_1970_20250907.csv"
GEOJSON_URL = "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"

COUNTY_NORMALIZATION = {
    "St Lawrence": "St. Lawrence",
    "Saint Lawrence": "St. Lawrence",
}

METRIC_COLUMNS = [
    'index_total', 'violent_total', 'murder', 'rape', 'robbery',
    'aggravated_assault', 'property_total', 'burglary', 'larceny',
    'motor_vehicle_theft'
]

# --- Helper Functions ---
def to_snake_case(name):
    """Converts a string to snake_case."""
    return name.lower().replace(' ', '_').replace('-', '_')

# --- Data Loading and Processing Functions ---
@st.cache_data
def load_crime_data():
    """Loads, cleans, and normalizes the crime data."""
    try:
        df = pd.read_csv(CRIMES_PATH, low_memory=False)
    except FileNotFoundError:
        st.error(f"Crime data file not found at '{CRIMES_PATH}'. Make sure it's in the same directory as the app.")
        return None
    df.columns = [to_snake_case(col) for col in df.columns]
    for col in METRIC_COLUMNS + ['year', 'months_reported']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df['county_norm'] = df['county'].str.strip().replace(COUNTY_NORMALIZATION)
    return df

@st.cache_data
def load_population_data():
    """Loads, cleans, and normalizes population data."""
    try:
        df = pd.read_csv(POPULATION_PATH, low_memory=False)
    except FileNotFoundError:
        st.error(f"Population data file not found at '{POPULATION_PATH}'. Make sure it's in the same directory as the app.")
        return None
    df.columns = [to_snake_case(col) for col in df.columns]
    pop_col = next((c for c in ['population', 'pop', 'est_population'] if c in df.columns), None)
    if not pop_col:
        st.error("Population column not found in population data.")
        return None
    df.rename(columns={pop_col: 'population', 'fips_code': 'fips'}, inplace=True)
    df['population'] = pd.to_numeric(df['population'], errors='coerce')
    df['year'] = pd.to_numeric(df['year'], errors='coerce')
    df['fips'] = df['fips'].astype(str).str.zfill(5)
    df['county_norm'] = df['geography'].str.replace(' County', '').str.strip().replace(COUNTY_NORMALIZATION)
    return df[['year', 'county_norm', 'population', 'fips']]

@st.cache_data
def join_and_compute_metrics(crime_df, pop_df):
    """Aggregates crime data, joins with population, and computes rates."""
    crime_agg = crime_df.groupby(['county_norm', 'year'])[METRIC_COLUMNS].sum().reset_index()
    df = pd.merge(crime_agg, pop_df, on=['county_norm', 'year'], how='left')
    for col in METRIC_COLUMNS:
        rate_col = f'{col}_per_100k'
        df[rate_col] = (df[col] / df['population']) * 100000
    return df

@st.cache_data
def get_geojson():
    """Fetches and caches GeoJSON data for NY counties."""
    try:
        r = requests.get(GEOJSON_URL)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        st.error(f"Failed to fetch GeoJSON: {e}")
        return None

# --- Main Application ---
st.title("🗽 New York State Crime Analytics Dashboard")

# --- Load Data ---
crime_df = load_crime_data()
pop_df = load_population_data()
geojson = get_geojson()

if crime_df is None or pop_df is None or geojson is None:
    st.warning("Could not load data. Please ensure the required CSV files are present.")
    st.stop()

full_df = join_and_compute_metrics(crime_df, pop_df)

# --- Sidebar Controls ---
st.sidebar.header("Dashboard Filters")

min_year, max_year = int(full_df['year'].min()), int(full_df['year'].max())
selected_years = st.sidebar.slider(
    "Select Year Range",
    min_year,
    max_year,
    (max_year - 5, max_year) # Default to last 5 years
)
start_year, end_year = selected_years

selected_metrics = st.sidebar.multiselect(
    "Select Crime Metrics",
    METRIC_COLUMNS,
    default=['index_total']
)

value_type = st.sidebar.radio("Value Type", ["Counts", "Per 100k"])

if not selected_metrics:
    st.warning("Please select at least one crime metric from the sidebar.")
    st.stop()

# --- Data Aggregation Based on Filters ---
# Filter data for the selected year range
range_df = full_df[full_df['year'].between(start_year, end_year)]

# Create a single metric by summing the selected metrics for map/rankings
range_df['combined_metric'] = range_df[selected_metrics].sum(axis=1)
for metric in selected_metrics:
    rate_col = f'{metric}_per_100k'
    range_df[rate_col] = (range_df[metric] / range_df['population']) * 100000

# Sum selected rate columns for a combined rate
rate_cols = [f'{m}_per_100k' for m in selected_metrics]
range_df['combined_rate'] = range_df[rate_cols].sum(axis=1)

# Aggregate over the year range for map and rankings
agg_df = range_df.groupby(['county_norm', 'fips']).agg({
    'combined_metric': 'sum',
    'combined_rate': 'sum', # You might want to average this instead
    'population': 'mean'
}).reset_index()

# --- KPI Section ---
st.header(f"Statewide Summary for {start_year} - {end_year}")
kpi_data = full_df[full_df['year'].between(start_year, end_year)]
total_crimes = kpi_data[selected_metrics].sum().sum()

# Calculate change over the selected period
start_year_total = full_df[full_df['year'] == start_year][selected_metrics].sum().sum()
end_year_total = full_df[full_df['year'] == end_year][selected_metrics].sum().sum()
period_change = ((end_year_total - start_year_total) / start_year_total * 100) if start_year_total else 0

col1, col2 = st.columns(2)
col1.metric(f"Total Selected Crimes ({start_year}-{end_year})", f"{total_crimes:,.0f}")
col2.metric(f"Change Over Period ({start_year} vs {end_year})", f"{period_change:.1f}%", delta=f"{period_change:.1f}%")

# --- Map View ---
st.header("County Crime Map")
color_col = 'combined_rate' if value_type == 'Per 100k' else 'combined_metric'
fig = px.choropleth_mapbox(
    agg_df,
    geojson=geojson,
    locations='fips',
    color=color_col,
    color_continuous_scale="Viridis",
    mapbox_style="carto-positron",
    zoom=6, center={"lat": 42.9, "lon": -75.5},
    opacity=0.6,
    hover_name='county_norm',
    hover_data={'fips': False, 'combined_metric': ':,', 'combined_rate': ':.2f'},
    labels={color_col: f"Total ({value_type})"}
)
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
st.plotly_chart(fig, use_container_width=True)

# --- Trend View ---
st.header("Historical Trend")
trend_df = full_df[full_df['year'].between(min_year, max_year)]
trend_metrics = [f"{m}_per_100k" for m in selected_metrics] if value_type == 'Per 100k' else selected_metrics
statewide_trend = trend_df.groupby('year')[trend_metrics].sum().reset_index()

trend_fig = px.line(
    statewide_trend,
    x='year',
    y=trend_metrics,
    title=f"Statewide Trend for Selected Metrics"
)
# Add a vertical shaded region for the selected year range
trend_fig.add_vrect(x0=start_year, x1=end_year, fillcolor="grey", opacity=0.2, line_width=0)
st.plotly_chart(trend_fig, use_container_width=True)


# --- Top/Bottom N View ---
st.header(f"County Rankings for {start_year} - {end_year}")
rank_metric = 'combined_rate' if value_type == 'Per 100k' else 'combined_metric'
ranked_data = agg_df.sort_values(rank_metric, ascending=False).dropna(subset=[rank_metric])

col1, col2 = st.columns(2)
with col1:
    top_fig = px.bar(ranked_data.head(10), x=rank_metric, y='county_norm', orientation='h', title="Top 10 Counties")
    top_fig.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(top_fig, use_container_width=True)
with col2:
    bottom_fig = px.bar(ranked_data.tail(10), x=rank_metric, y='county_norm', orientation='h', title="Bottom 10 Counties")
    bottom_fig.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(bottom_fig, use_container_width=True)

# --- Agency Table ---
st.header("Agency-Level Data")
agency_data = crime_df[crime_df['year'].between(start_year, end_year)]
st.dataframe(agency_data[['year', 'county_norm', 'agency', 'months_reported'] + selected_metrics])