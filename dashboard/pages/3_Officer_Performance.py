import os
import sys

sys.path.append(
    os.path.dirname(os.path.dirname(__file__))
)

import streamlit as st

from src.helpers import (
    load_data,
    officer_summary
)

from src.charts import (
    officer_recovery_chart,
    claims_per_officer_chart,
    officer_collected_chart,
    officer_collection_chart
)

st.set_page_config(
    page_title="Officer Performance",
    page_icon="👨‍💼",
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

officer_search = st.sidebar.text_input("Officer contains...")

filtered_df = df[
    df["Accident Date"].dt.year.isin(selected_years) &
    df["Status"].isin(selected_statuses)
]

if officer_search:
    filtered_df = filtered_df[
        filtered_df["Officer"].str.contains(
            officer_search, case=False, na=False
        )
    ]

if filtered_df.empty:
    st.warning("No records found for the selected filters.")
    st.stop()

# -------------------------------------------------------
# TITLE
# -------------------------------------------------------

st.title("👨‍💼 Officer Performance Analysis")
st.caption(
    "Workload distribution, recovery portfolios, and collection "
    "efficiency by recovery officer."
)
st.markdown("---")

summary = officer_summary(filtered_df)

# -------------------------------------------------------
# KPIs
# -------------------------------------------------------

busiest = summary.loc[summary["Claims"].idxmax()]
top_recovery = summary.loc[summary["Recovery"].idxmax()]
best_collector = summary.loc[summary["Collection Rate"].idxmax()]

col1, col2, col3, col4 = st.columns(4)

col1.metric("👥 Active Officers", f"{summary['Officer'].nunique():,}")
col2.metric(
    "📄 Busiest Officer",
    busiest["Officer"],
    f"{busiest['Claims']:,} claims"
)
col3.metric(
    "💰 Top Recovery Officer",
    top_recovery["Officer"],
    f"SAR {top_recovery['Recovery']:,.0f}"
)
col4.metric(
    "✅ Best Collection Rate",
    best_collector["Officer"],
    f"{best_collector['Collection Rate']:.1f}%"
)

st.divider()

# -------------------------------------------------------
# ROW 1
# -------------------------------------------------------

left, right = st.columns(2)

with left:
    st.plotly_chart(
        officer_recovery_chart(filtered_df), use_container_width=True
    )

with right:
    st.plotly_chart(
        officer_collection_chart(filtered_df), use_container_width=True
    )

# -------------------------------------------------------
# ROW 2
# -------------------------------------------------------

left, right = st.columns(2)

with left:
    st.plotly_chart(
        claims_per_officer_chart(filtered_df), use_container_width=True
    )

with right:
    st.plotly_chart(
        officer_collected_chart(filtered_df), use_container_width=True
    )

st.divider()

# -------------------------------------------------------
# TABLE
# -------------------------------------------------------

st.subheader("Officer Scorecard")

st.dataframe(
    summary[
        [
            "Officer", "Claims", "Recovery", "Collected",
            "Remaining", "Collection Rate", "Avg Recovery"
        ]
    ],
    use_container_width=True,
    height=450
)

csv = summary.to_csv(index=False)

st.download_button(
    "⬇ Download Officer Scorecard",
    csv,
    file_name="officer_scorecard.csv",
    mime="text/csv"
)
