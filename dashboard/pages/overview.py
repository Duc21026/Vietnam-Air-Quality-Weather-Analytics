"""Overview page: summary stats and city comparison."""

import streamlit as st
import plotly.express as px

from dashboard.utils.warehouse import get_city_daily

st.title("Overview")

try:
    df = get_city_daily()
except Exception as e:
    st.error(f"Cannot connect to warehouse: {e}")
    st.info("Make sure the pipeline has run at least once.")
    st.stop()

if df.empty:
    st.warning("No data available. Run the Airflow pipeline first.")
    st.stop()

st.subheader("Latest Daily Averages")
st.dataframe(df.head(10))

st.subheader("Average PM2.5 by City")
fig = px.bar(
    df.groupby("city")["avg_pm25"].mean().reset_index(),
    x="city", y="avg_pm25",
    title="Average PM2.5 by City",
    labels={"avg_pm25": "PM2.5 (µg/m³)", "city": "City"},
)
st.plotly_chart(fig, use_container_width=True)

st.subheader("PM2.5 Over Time")
fig2 = px.line(
    df.sort_values("date"),
    x="date", y="avg_pm25", color="city",
    title="Daily Average PM2.5",
    labels={"avg_pm25": "PM2.5 (µg/m³)", "date": "Date", "city": "City"},
)
st.plotly_chart(fig2, use_container_width=True)
