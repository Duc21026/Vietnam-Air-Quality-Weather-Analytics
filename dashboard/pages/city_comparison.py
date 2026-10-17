"""City Comparison page: PM2.5 average for Hanoi vs Ho Chi Minh City."""

import streamlit as st
import plotly.express as px
import pandas as pd

from dashboard.utils.warehouse import get_city_pm25_comparison

st.title("City Comparison: PM2.5")
st.markdown(
    "Which city has the higher average PM2.5 during the selected period? "
    "Metric: **station-balanced daily average** — each station's daily mean is "
    "computed first, then averaged per city per day, then averaged over the "
    "selected days."
)

try:
    df = get_city_pm25_comparison()
except Exception as e:
    st.error(f"Cannot connect to warehouse: {e}")
    st.info("Make sure the pipeline has run at least once.")
    st.stop()

if df.empty:
    st.warning("No PM2.5 data available. Run the Airflow pipeline first.")
    st.stop()

df["date"] = pd.to_datetime(df["date"]).dt.date
min_date, max_date = df["date"].min(), df["date"].max()

st.sidebar.subheader("Filters")
start_date = st.sidebar.date_input("Start date", value=min_date, min_value=min_date, max_value=max_date)
end_date = st.sidebar.date_input("End date", value=max_date, min_value=min_date, max_value=max_date)

if start_date > end_date:
    st.error("Start date must be on or before end date.")
    st.stop()

mask = (df["date"] >= start_date) & (df["date"] <= end_date)
filtered = df[mask]

if filtered.empty:
    st.warning("No data in the selected date range.")
    st.stop()

summary = (
    filtered.groupby("city")
    .agg(
        avg_pm25=("avg_pm25", "mean"),
        days=("date", "nunique"),
        measurements=("measurement_count", "sum"),
        stations=("station_count", "max"),
    )
    .reset_index()
)

higher_city = summary.loc[summary["avg_pm25"].idxmax(), "city"]
higher_val = summary["avg_pm25"].max()

st.subheader("Summary")
cols = st.columns(len(summary) + 1)
for col, (_, row) in zip(cols, summary.iterrows()):
    col.metric(
        label=f"{row['city']} avg PM2.5",
        value=f"{row['avg_pm25']:.2f} µg/m³",
        help=f"{int(row['days'])} days, {int(row['stations'])} station(s), {int(row['measurements'])} measurements",
    )
cols[-1].metric("Higher PM2.5", higher_city, f"{higher_val:.2f} µg/m³")

st.caption(
    f"Selected period: {start_date} → {end_date} (same range applied to both cities)."
)

st.subheader("Average PM2.5 by City")
fig = px.bar(
    summary,
    x="city", y="avg_pm25",
    title="Average PM2.5 (selected period)",
    labels={"avg_pm25": "PM2.5 (µg/m³)", "city": "City"},
    text_auto=".2f",
)
st.plotly_chart(fig, use_container_width=True)

st.subheader("Daily Average PM2.5 Over Time")
fig2 = px.line(
    filtered.sort_values("date"),
    x="date", y="avg_pm25", color="city", markers=True,
    title="Daily Average PM2.5",
    labels={"avg_pm25": "PM2.5 (µg/m³)", "date": "Date", "city": "City"},
)
st.plotly_chart(fig2, use_container_width=True)

st.subheader("Coverage")
coverage = summary.rename(
    columns={
        "avg_pm25": "Avg PM2.5 (µg/m³)",
        "days": "Days with data",
        "stations": "Stations",
        "measurements": "Measurements",
    }
)
st.dataframe(coverage, use_container_width=True, hide_index=True)

st.caption(
    "Limitations: coverage is asymmetric — Hanoi has 2 monitoring stations while "
    "Ho Chi Minh City has only 1. Weekday/partial days at the edges of the range "
    "may have fewer measurements. Raw duplicate rows are de-duplicated upstream by dbt."
)
