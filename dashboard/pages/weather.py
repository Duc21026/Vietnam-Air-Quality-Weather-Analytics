"""Weather page: temperature, humidity, wind, and pollution correlation."""

import streamlit as st
import plotly.express as px

from dashboard.utils.warehouse import get_pollution_weather

st.title("Weather & Pollution")

try:
    df = get_pollution_weather()
except Exception as e:
    st.error(f"Cannot connect to warehouse: {e}")
    st.stop()

if df.empty:
    st.warning("No data available.")
    st.stop()

st.subheader("Temperature Over Time")
fig = px.line(
    df.sort_values("timestamp_utc"),
    x="timestamp_utc", y="temperature", color="city",
    title="Temperature (°C)",
    labels={"temperature": "°C", "timestamp_utc": "Time"},
)
st.plotly_chart(fig, use_container_width=True)

st.subheader("Humidity vs PM2.5")
fig2 = px.scatter(
    df.dropna(subset=["pm25", "relative_humidity"]),
    x="relative_humidity", y="pm25", color="city",
    title="Humidity vs PM2.5",
    labels={"relative_humidity": "Humidity (%)", "pm25": "PM2.5 (µg/m³)"},
)
st.plotly_chart(fig2, use_container_width=True)

st.subheader("Wind Speed vs PM2.5")
fig3 = px.scatter(
    df.dropna(subset=["pm25", "wind_speed"]),
    x="wind_speed", y="pm25", color="city",
    title="Wind Speed vs PM2.5",
    labels={"wind_speed": "Wind (km/h)", "pm25": "PM2.5 (µg/m³)"},
)
st.plotly_chart(fig3, use_container_width=True)

st.subheader("Pollution Level Distribution")
if "pollution_level" in df.columns:
    fig4 = px.histogram(
        df, x="pollution_level", color="city",
        title="Pollution Level Distribution",
        labels={"pollution_level": "Level"},
    )
    st.plotly_chart(fig4, use_container_width=True)
