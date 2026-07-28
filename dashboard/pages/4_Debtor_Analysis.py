import os
import sys

sys.path.append(
    os.path.dirname(os.path.dirname(__file__))
)

import streamlit as st

from src.helpers import (
    load_data,
    debtor_summary,
    priority_debtors
)

from src.charts import (
    top_debtors_chart,
    debtor_type_chart,
    debtor_performance_matrix
)

st.set_page_config(
    page_title="Debtor Analysis",
    page_icon="👤",
    layout="wide"
)

df = load_data()

# -------------------------------------------------------
# SIDEBAR
# -------------------------------------------------------

st.sidebar.header("🎛 Filters")

debtor_types = sorted(df["Debtor Type"].dropna().unique())

selected_types = st.sidebar.multiselect(
    "Debtor Type", debtor_types, default=debtor_types
)

min_claims = st.sidebar.slider(
    "Minimum claims per debtor (performance matrix)",
    min_value=1, max_value=10, value=3
)

filtered_df = df[df["Debtor Type"].isin(selected_types)]

if filtered_df.empty:
    st.warning("No records found for the selected filters.")
    st.stop()

# -------------------------------------------------------
# TITLE
# -------------------------------------------------------

st.title("👤 Debtor Analysis")
st.caption(
    "High-value debtors, collection efficiency, and outstanding "
    "liabilities across the recovery portfolio."
)
st.markdown("---")

summary = debtor_summary(filtered_df)

# -------------------------------------------------------
# KPIs
# -------------------------------------------------------

highest_recovery = summary.iloc[0]
highest_remaining = summary.sort_values("Remaining", ascending=False).iloc[0]

eligible = summary[summary["Claims"] >= 2]
best_collector = (
    eligible.sort_values("Collection Rate", ascending=False).iloc[0]
    if not eligible.empty else summary.iloc[0]
)

col1, col2, col3, col4 = st.columns(4)

col1.metric("👤 Unique Debtors", f"{summary['Debtor Number'].nunique():,}")
col2.metric(
    "💰 Highest Recovery",
    highest_recovery["Debtor Name"],
    f"SAR {highest_recovery['Recovery']:,.0f}"
)
col3.metric(
    "⌛ Highest Outstanding",
    highest_remaining["Debtor Name"],
    f"SAR {highest_remaining['Remaining']:,.0f}"
)
col4.metric(
    "✅ Best Collector",
    best_collector["Debtor Name"],
    f"{best_collector['Collection Rate']:.1f}%"
)

st.divider()

# -------------------------------------------------------
# ROW 1
# -------------------------------------------------------

left, right = st.columns(2)

with left:
    st.plotly_chart(
        top_debtors_chart(filtered_df), use_container_width=True
    )

with right:
    st.plotly_chart(
        debtor_type_chart(filtered_df), use_container_width=True
    )

# -------------------------------------------------------
# ROW 2 - PERFORMANCE MATRIX
# -------------------------------------------------------

st.plotly_chart(
    debtor_performance_matrix(filtered_df, min_claims=min_claims),
    use_container_width=True
)

st.caption(
    "Bubble size reflects claim volume, color reflects outstanding "
    "balance. Debtors in the lower-right are large exposures with "
    "weak collection performance."
)

st.divider()

# -------------------------------------------------------
# PRIORITY DEBTORS
# -------------------------------------------------------

st.subheader("⚠ Priority Debtors")
st.caption(
    "Above-median recovery exposure combined with a collection rate "
    "below 20% - these accounts warrant immediate follow-up."
)

priority = priority_debtors(filtered_df, min_claims=min_claims)

if priority.empty:
    st.success("No debtors currently meet the priority criteria.")
else:
    st.dataframe(
        priority[
            [
                "Debtor Name", "Debtor Type", "Claims",
                "Recovery", "Collected", "Remaining", "Collection Rate"
            ]
        ],
        use_container_width=True,
        height=300
    )

st.divider()

# -------------------------------------------------------
# TABLE
# -------------------------------------------------------

st.subheader("Debtor Scorecard")

st.dataframe(
    summary[
        [
            "Debtor Name", "Debtor Type", "Claims", "Recovery",
            "Collected", "Remaining", "Collection Rate"
        ]
    ],
    use_container_width=True,
    height=450
)

csv = summary.to_csv(index=False)

st.download_button(
    "⬇ Download Debtor Scorecard",
    csv,
    file_name="debtor_scorecard.csv",
    mime="text/csv"
)
