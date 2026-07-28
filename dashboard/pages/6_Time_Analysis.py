import os
import sys

sys.path.append(
    os.path.dirname(os.path.dirname(__file__))
)

import streamlit as st

from src.helpers import (
    load_data,
    recovery_delay_kpis
)

from src.charts import (
    time_claims_trend_chart,
    time_recovery_trend_chart,
    time_collection_rate_chart,
    recovery_delay_histogram
)

st.set_page_config(
    page_title="Time Analysis",
    page_icon="📅",
    layout="wide"
)

df = load_data()

# -------------------------------------------------------
# SIDEBAR
# -------------------------------------------------------

st.sidebar.header("🎛 Filters")

years = sorted(
    df["Accident Date"].dt.year.dropna().unique(),
    reverse=True
)

selected_years = st.sidebar.multiselect(
    "Year", years, default=years
)

filtered_df = df[df["Accident Date"].dt.year.isin(selected_years)]

if filtered_df.empty:
    st.warning("No records found for the selected filters.")
    st.stop()

# -------------------------------------------------------
# TITLE
# -------------------------------------------------------

st.title("📅 Time Analysis")
st.caption(
    "Claim activity and recovery performance over time - trends, "
    "seasonality, and operational delays."
)
st.markdown("---")

# -------------------------------------------------------
# KPIs
# -------------------------------------------------------

delay_kpis = recovery_delay_kpis(filtered_df)

col1, col2, col3, col4 = st.columns(4)

col1.metric("⏱ Avg Recovery Delay", f"{delay_kpis['Average Delay']:.1f} days")
col2.metric("📊 Median Delay", f"{delay_kpis['Median Delay']:.1f} days")
col3.metric("🚨 Max Delay", f"{delay_kpis['Max Delay']:.0f} days")
col4.metric(
    "🐢 Slow Cases (>180 days)",
    f"{delay_kpis['Slow Cases (> 180 Days)']:,}"
)

st.divider()

# -------------------------------------------------------
# ROW 1
# -------------------------------------------------------

left, right = st.columns(2)

with left:
    st.plotly_chart(
        time_claims_trend_chart(filtered_df), use_container_width=True
    )

with right:
    st.plotly_chart(
        time_recovery_trend_chart(filtered_df), use_container_width=True
    )

# -------------------------------------------------------
# ROW 2
# -------------------------------------------------------

left, right = st.columns(2)

with left:
    st.plotly_chart(
        time_collection_rate_chart(filtered_df), use_container_width=True
    )

with right:
    st.plotly_chart(
        recovery_delay_histogram(filtered_df), use_container_width=True
    )

st.divider()

# -------------------------------------------------------
# SLOW CASES TABLE
# -------------------------------------------------------

st.subheader("🐢 Slowest Recovery Cases (> 180 Days)")

slow_cases = (
    filtered_df[filtered_df["Recovery Delay (Days)"] > 180]
    [
        [
            "Claim Number", "Officer", "Location",
            "Recovery Amount", "Recovery Delay (Days)"
        ]
    ]
    .sort_values("Recovery Delay (Days)", ascending=False)
)

if slow_cases.empty:
    st.success("No claims currently exceed a 180-day recovery delay.")
else:
    st.dataframe(slow_cases, use_container_width=True, height=400)

    csv = slow_cases.to_csv(index=False)

    st.download_button(
        "⬇ Download Slow Cases",
        csv,
        file_name="slow_recovery_cases.csv",
        mime="text/csv"
    )
