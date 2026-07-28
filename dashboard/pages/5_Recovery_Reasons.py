import os
import sys

sys.path.append(
    os.path.dirname(os.path.dirname(__file__))
)

import streamlit as st

from src.helpers import (
    load_data,
    recovery_reason_summary,
    priority_reasons
)

from src.charts import (
    recovery_reason_chart,
    recovery_reason_rate_chart,
    reason_performance_matrix
)

st.set_page_config(
    page_title="Recovery Reasons",
    page_icon="⚠",
    layout="wide"
)

df = load_data()

# -------------------------------------------------------
# SIDEBAR
# -------------------------------------------------------

st.sidebar.header("🎛 Filters")

min_claims = st.sidebar.slider(
    "Minimum claims per reason",
    min_value=1, max_value=30, value=10
)

statuses = sorted(df["Status"].dropna().unique())

selected_statuses = st.sidebar.multiselect(
    "Claim Status", statuses, default=statuses
)

filtered_df = df[df["Status"].isin(selected_statuses)]

if filtered_df.empty:
    st.warning("No records found for the selected filters.")
    st.stop()

# -------------------------------------------------------
# TITLE
# -------------------------------------------------------

st.title("⚠ Recovery Reason Analysis")
st.caption(
    "Operational bottlenecks affecting claim collection, by recovery "
    "reason."
)
st.markdown("---")

summary = recovery_reason_summary(filtered_df)
filtered_summary = summary[summary["Claims"] >= min_claims]

# -------------------------------------------------------
# KPIs
# -------------------------------------------------------

highest_claims = summary.iloc[0]
highest_remaining = summary.sort_values("Remaining", ascending=False).iloc[0]

best_collection = (
    filtered_summary.sort_values("Collection Rate", ascending=False).iloc[0]
    if not filtered_summary.empty else summary.iloc[0]
)

col1, col2, col3, col4 = st.columns(4)

col1.metric("⚠ Distinct Reasons", f"{summary['Recovery Reason'].nunique():,}")
col2.metric(
    "📄 Most Common Reason",
    highest_claims["Recovery Reason"][:30],
    f"{highest_claims['Claims']:,} claims"
)
col3.metric(
    "⌛ Largest Outstanding",
    highest_remaining["Recovery Reason"][:30],
    f"SAR {highest_remaining['Remaining']:,.0f}"
)
col4.metric(
    "✅ Best Collection Rate",
    best_collection["Recovery Reason"][:30],
    f"{best_collection['Collection Rate']:.1f}%"
)

st.divider()

# -------------------------------------------------------
# ROW 1
# -------------------------------------------------------

left, right = st.columns(2)

with left:
    st.plotly_chart(
        recovery_reason_chart(filtered_df), use_container_width=True
    )

with right:
    st.plotly_chart(
        recovery_reason_rate_chart(filtered_df, min_claims=min_claims),
        use_container_width=True
    )

# -------------------------------------------------------
# ROW 2 - PERFORMANCE MATRIX
# -------------------------------------------------------

st.plotly_chart(
    reason_performance_matrix(filtered_df, min_claims=min_claims),
    use_container_width=True
)

st.divider()

# -------------------------------------------------------
# PRIORITY REASONS
# -------------------------------------------------------

st.subheader("⚠ Priority Recovery Reasons")
st.caption(
    "Above-median recovery exposure combined with a collection rate "
    "below 20% - operational bottlenecks worth prioritizing."
)

priority = priority_reasons(filtered_df, min_claims=min_claims)

if priority.empty:
    st.success("No recovery reasons currently meet the priority criteria.")
else:
    st.dataframe(
        priority[
            [
                "Recovery Reason", "Claims", "Recovery",
                "Collected", "Remaining", "Collection Rate"
            ]
        ],
        use_container_width=True,
        height=300
    )

st.divider()

# -------------------------------------------------------
# TABLE
# -------------------------------------------------------

st.subheader("Recovery Reason Scorecard")

st.dataframe(
    summary[
        [
            "Recovery Reason", "Claims", "Recovery",
            "Collected", "Remaining", "Collection Rate", "Avg Recovery"
        ]
    ],
    use_container_width=True,
    height=450
)

csv = summary.to_csv(index=False)

st.download_button(
    "⬇ Download Recovery Reason Scorecard",
    csv,
    file_name="recovery_reason_scorecard.csv",
    mime="text/csv"
)
