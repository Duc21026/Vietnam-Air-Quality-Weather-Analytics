"""Vietnam Air Quality & Weather Analytics dashboard."""

import streamlit as st

st.set_page_config(
    page_title="Vietnam Air Quality & Weather",
    page_icon="🌫️",
    layout="wide",
)

st.title("Vietnam Air Quality & Weather Analytics")
st.markdown("Real-time air quality and weather data for Hanoi and Ho Chi Minh City")

st.sidebar.title("Navigation")
st.sidebar.markdown("Use the pages in the sidebar to explore the data.")

st.markdown("""
### Data Sources
- **Air Quality**: OpenAQ API (PM2.5, PM10)
- **Weather**: Open-Meteo API (temperature, humidity, precipitation, wind, pressure)

### Pipeline
APIs → Airflow → Data Lake (Parquet) → PostgreSQL → dbt → Dashboard
""")
