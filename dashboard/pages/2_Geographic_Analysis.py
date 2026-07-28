import os
import sys

sys.path.append(
    os.path.dirname(os.path.dirname(__file__))
)

import streamlit as st

from src.helpers import (
    load_data,
    location_summary
)

from src.charts import (
    claims_by_location_chart,
    top_locations_chart,
    remaining_by_location_chart,
    location_collection_chart,
    location_performance_matrix
)

st.set_page_config(
    page_title="Geographic Analysis",
    page_icon="🌍",
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

statuses = sorted(df["Status"].dropna().unique())

selected_statuses = st.sidebar.multiselect(
    "Claim Status", statuses, default=statuses
)

all_locations = sorted(df["Location"].dropna().unique())

selected_locations = st.sidebar.multiselect(
    "Location", all_locations, default=all_locations
)

filtered_df = df[
    df["Accident Date"].dt.year.isin(selected_years) &
    df["Status"].isin(selected_statuses) &
    df["Location"].isin(selected_locations)
]

if filtered_df.empty:
    st.warning("No records found for the selected filters.")
    st.stop()

# -------------------------------------------------------
# TITLE
# -------------------------------------------------------

st.title("🌍 Geographic Analysis")
st.caption(
    "Recovery performance across accident locations - exposure, "
    "collection efficiency, and operational priority."
)
st.markdown("---")

summary = location_summary(filtered_df)

# -------------------------------------------------------
# KPIs
# -------------------------------------------------------

top_claims_loc = summary.loc[summary["Claims"].idxmax()]
top_recovery_loc = summary.loc[summary["Recovery"].idxmax()]
top_collection_loc = summary.loc[summary["Collection Rate"].idxmax()]

col1, col2, col3, col4 = st.columns(4)

col1.metric("📍 Locations Covered", f"{summary['Location'].nunique():,}")
col2.metric(
    "🏙 Highest Claim Volume",
    top_claims_loc["Location"],
    f"{top_claims_loc['Claims']:,} claims"
)
col3.metric(
    "💰 Highest Recovery",
    top_recovery_loc["Location"],
    f"SAR {top_recovery_loc['Recovery']:,.0f}"
)
col4.metric(
    "✅ Best Collection Rate",
    top_collection_loc["Location"],
    f"{top_collection_loc['Collection Rate']:.1f}%"
)

st.divider()

# -------------------------------------------------------
# ROW 1
# -------------------------------------------------------

left, right = st.columns(2)

with left:
    st.plotly_chart(
        top_locations_chart(filtered_df), use_container_width=True
    )

with right:
    st.plotly_chart(
        location_collection_chart(filtered_df), use_container_width=True
    )

# -------------------------------------------------------
# ROW 2
# -------------------------------------------------------

left, right = st.columns(2)

with left:
    st.plotly_chart(
        claims_by_location_chart(filtered_df), use_container_width=True
    )

with right:
    st.plotly_chart(
        remaining_by_location_chart(filtered_df), use_container_width=True
    )

# -------------------------------------------------------
# ROW 3 - PERFORMANCE MATRIX
# -------------------------------------------------------

st.plotly_chart(
    location_performance_matrix(filtered_df), use_container_width=True
)

st.caption(
    "Bubble size reflects claim volume, color reflects outstanding "
    "balance. Locations in the upper-right have both large portfolios "
    "and strong collection performance."
)

st.divider()

# -------------------------------------------------------
# SCORECARD TABLE
# -------------------------------------------------------

st.subheader("Geographic Scorecard")

st.dataframe(
    summary[
        [
            "Location", "Claims", "Recovery", "Collected",
            "Remaining", "Collection Rate", "Avg Recovery", "Priority"
        ]
    ],
    use_container_width=True,
    height=450
)

csv = summary.to_csv(index=False)

st.download_button(
    "⬇ Download Location Scorecard",
    csv,
    file_name="geographic_scorecard.csv",
    mime="text/csv"
)
