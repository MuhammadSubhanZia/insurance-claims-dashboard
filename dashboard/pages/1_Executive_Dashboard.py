import os
import sys

sys.path.append(
    os.path.dirname(os.path.dirname(__file__))
)

import streamlit as st
from src.helpers import (
    load_data,
    executive_kpis,
    format_money
)

from src.charts import (
    collection_donut,
    claim_status_chart,
    monthly_trend_chart,
    recovery_trend_chart,
    top_locations_chart,
    officer_recovery_chart
)

# -------------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------------

st.set_page_config(
    page_title="Executive Dashboard",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>

div[data-testid="metric-container"]{
    background-color:#FFFFFF;
    border:1px solid #E5E7EB;
    padding:18px 20px;
    border-radius:14px;
    box-shadow:0px 2px 8px rgba(0,0,0,0.08);
}

div[data-testid="metric-container"] > label{
    font-size:14px;
    font-weight:600;
    color:#6B7280;
}

div[data-testid="stMetricValue"]{
    font-size:24px;
    font-weight:700;
    white-space:nowrap;
    overflow:visible;
}

</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------
# LOAD DATA
# -------------------------------------------------------

df = load_data()

# -------------------------------------------------------
# SIDEBAR
# -------------------------------------------------------

st.sidebar.header("🎛 Dashboard Controls")

# -----------------------------
# Year
# -----------------------------
years = sorted(
    df["Accident Date"]
    .dt.year
    .dropna()
    .unique(),
    reverse=True
)

selected_years = st.sidebar.multiselect(
    "Year",
    years,
    default=years
)

# -----------------------------
# Claim Status
# -----------------------------
statuses = sorted(df["Status"].dropna().unique())

selected_statuses = st.sidebar.multiselect(
    "Claim Status",
    statuses,
    default=statuses
)

# -----------------------------
# Location
# -----------------------------
all_locations = sorted(
    df["Location"]
    .dropna()
    .unique()
    .tolist()
)

selected_locations = st.sidebar.multiselect(
    "Location",
    all_locations,
    default=all_locations,
    help="All locations are selected by default so totals match the "
         "full dataset. Narrow this down to focus on specific areas."
)

# -----------------------------
# Search Officer
# -----------------------------
officer_search = st.sidebar.text_input(
    "Officer contains..."
)

if st.sidebar.button("🔄 Reset Filters"):
    st.rerun()

# -------------------------------------------------------
# FILTER DATA
# -------------------------------------------------------

filtered_df = df.copy()

filtered_df = filtered_df[
    filtered_df["Accident Date"]
    .dt.year
    .isin(selected_years)
]

filtered_df = filtered_df[
    filtered_df["Status"]
    .isin(selected_statuses)
]

filtered_df = filtered_df[
    filtered_df["Location"]
    .isin(selected_locations)
]

if officer_search:
    filtered_df = filtered_df[
        filtered_df["Officer"]
        .str.contains(
            officer_search,
            case=False,
            na=False
        )
    ]

if filtered_df.empty:
    st.warning("No records found for the selected filters.")
    st.stop()

# -------------------------------------------------------
# TITLE
# -------------------------------------------------------

st.title("📊 Insurance Claims Executive Dashboard")

st.caption(
    "Interactive business intelligence dashboard for insurance recovery analysis."
)

st.markdown("---")
st.subheader("Current Selection")
st.info(
    f"""
📄 **Showing:** {len(filtered_df):,} Claims

📅 **Years:** {", ".join(map(str, selected_years))}

📌 **Status:** {", ".join(selected_statuses)}

📍 **Locations:** {len(selected_locations)} Selected

👤 **Officer Search:** {officer_search if officer_search else "All"}
"""
)

# -------------------------------------------------------
# KPIs
# -------------------------------------------------------

kpis = executive_kpis(filtered_df)

avg_recovery = (
    filtered_df["Recovery Amount"].mean()
)

placeholder = (
    filtered_df["Debtor Number Status"]
    .eq("Placeholder")
    .sum()
)

approved = (
    filtered_df["Status"]
    .eq("Approved")
    .sum()
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "📄 Total Claims",
    f"{kpis['Total Claims']:,}"
)

col2.metric(
    "💰 Recovery",
    format_money(kpis["Recovery Amount"])
)

col3.metric(
    "✅ Collected",
    format_money(kpis["Collected Amount"])
)

col4.metric(
    "📈 Collection Rate",
    f"{kpis['Collection Rate']:.2f}%"
)

col5, col6, col7, col8 = st.columns(4)

col5.metric(
    "⌛ Remaining",
    format_money(kpis["Remaining Amount"])
)

col6.metric(
    "📊 Avg Recovery",
    format_money(avg_recovery)
)

col7.metric(
    "⚠ Placeholder Debtors",
    f"{placeholder:,}"
)

col8.metric(
    "✔ Approved Claims",
    f"{approved:,}"
)

st.divider()

# -------------------------------------------------------
# ROW 1
# -------------------------------------------------------

left, right = st.columns(2)

with left:

    st.plotly_chart(
        collection_donut(filtered_df),
        use_container_width=True
    )

with right:

    st.plotly_chart(
        claim_status_chart(filtered_df),
        use_container_width=True
    )

# -------------------------------------------------------
# ROW 2
# -------------------------------------------------------

left, right = st.columns(2)

with left:

    st.plotly_chart(
        monthly_trend_chart(filtered_df),
        use_container_width=True
    )

with right:

    st.plotly_chart(
        recovery_trend_chart(filtered_df),
        use_container_width=True
    )

# -------------------------------------------------------
# ROW 3
# -------------------------------------------------------

left, right = st.columns(2)

with left:

    st.plotly_chart(
        top_locations_chart(filtered_df),
        use_container_width=True
    )

with right:

    st.plotly_chart(
        officer_recovery_chart(filtered_df),
        use_container_width=True
    )

st.divider()

# -------------------------------------------------------
# RECENT CLAIMS
# -------------------------------------------------------

st.subheader("Recent Claims")

search = st.text_input(
    "🔍 Search Claim Number..."
)

table = filtered_df.copy()

if search:

    table = table[
        table["Claim Number"]
        .astype(str)
        .str.contains(
            search,
            case=False,
            na=False
        )
    ]

columns = [

    "Claim Number",
    "Status",
    "Officer",
    "Location",
    "Recovery Amount",
    "Collected Amount",
    "Remaining Amount",
    "Recovery Reason",
    "Accident Date"

]

st.dataframe(

    table[columns]
    .sort_values(
        "Accident Date",
        ascending=False
    ),

    use_container_width=True,
    height=450

)

csv = table.to_csv(index=False)

st.download_button(

    "⬇ Download Filtered Data",

    csv,

    file_name="claims_dashboard_export.csv",

    mime="text/csv"

)

st.divider()