"""Air Quality page: PM2.5 and PM10 trends."""

import streamlit as st
import plotly.express as px

from dashboard.utils.warehouse import get_air_quality_hourly

st.title("Air Quality")

try:
    df = get_air_quality_hourly()
except Exception as e:
    st.error(f"Cannot connect to warehouse: {e}")
    st.stop()

if df.empty:
    st.warning("No air quality data available.")
    st.stop()

st.subheader("PM2.5 Over Time")
fig = px.line(
    df.sort_values("timestamp_utc"),
    x="timestamp_utc", y="pm25", color="city",
    title="PM2.5 Hourly",
    labels={"pm25": "PM2.5 (µg/m³)", "timestamp_utc": "Time"},
)
st.plotly_chart(fig, use_container_width=True)

if "pm10" in df.columns and df["pm10"].notna().any():
    st.subheader("PM10 Over Time")
    fig2 = px.line(
        df[df["pm10"].notna()].sort_values("timestamp_utc"),
        x="timestamp_utc", y="pm10", color="city",
        title="PM10 Hourly",
        labels={"pm10": "PM10 (µg/m³)", "timestamp_utc": "Time"},
    )
    st.plotly_chart(fig2, use_container_width=True)

st.subheader("City Comparison")
fig3 = px.box(
    df, x="city", y="pm25",
    title="PM2.5 Distribution by City",
    labels={"pm25": "PM2.5 (µg/m³)", "city": "City"},
)
st.plotly_chart(fig3, use_container_width=True)
