import os
import sys

sys.path.append(
    os.path.dirname(os.path.dirname(__file__))
)

import streamlit as st

from src.helpers import (
    load_data,
    data_quality_summary,
    data_quality_score,
    business_risks_summary
)

from src.charts import (
    quality_gauge_chart,
    completeness_chart,
    consistency_chart,
    validity_chart,
    placeholder_chart
)

st.set_page_config(
    page_title="Data Quality",
    page_icon="🧹",
    layout="wide"
)

df = load_data()

st.title("🧹 Data Quality Assessment")
st.caption(
    "Dataset health scorecard - completeness, consistency, validity, "
    "and uniqueness checks on the cleaned recovery dataset."
)
st.markdown("---")

# -------------------------------------------------------
# SCORECARD KPIs
# -------------------------------------------------------

metrics = data_quality_summary(df)

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("📄 Total Rows", f"{metrics['Rows']:,}")
col2.metric("📊 Total Columns", f"{metrics['Columns']:,}")
col3.metric("🔁 Duplicate Claims", f"{metrics['Duplicate Claims']:,}")
col4.metric("❓ Missing Values", f"{metrics['Missing Values']:,}")
col5.metric("⚠ Placeholder Numbers", f"{metrics['Placeholder Numbers']:,}")

st.divider()

# -------------------------------------------------------
# QUALITY GAUGE
# -------------------------------------------------------

score = data_quality_score(df)

st.plotly_chart(quality_gauge_chart(score), use_container_width=True)

st.divider()

# -------------------------------------------------------
# COMPLETENESS / CONSISTENCY
# -------------------------------------------------------

left, right = st.columns(2)

with left:
    st.plotly_chart(completeness_chart(df), use_container_width=True)

with right:
    st.plotly_chart(consistency_chart(df), use_container_width=True)

# -------------------------------------------------------
# VALIDITY / PLACEHOLDER
# -------------------------------------------------------

left, right = st.columns(2)

with left:
    st.plotly_chart(validity_chart(df), use_container_width=True)

with right:
    st.plotly_chart(placeholder_chart(df), use_container_width=True)

st.divider()

# -------------------------------------------------------
# BUSINESS RISKS
# -------------------------------------------------------

st.subheader("Business Risks")

st.dataframe(
    business_risks_summary(df),
    use_container_width=True,
    height=220
)

st.divider()

# -------------------------------------------------------
# RECOMMENDATIONS
# -------------------------------------------------------

st.subheader("Recommendations")

st.markdown("""
1. Continue enforcing standardized location mapping for new accident
   locations as they are added to the source system.
2. Validate debtor contact numbers at data entry to reduce placeholder
   values.
3. Reduce missing operational fields through mandatory entry forms.
4. Monitor duplicate claim numbers regularly and confirm their
   business meaning before deduplication.
5. Automate this preprocessing pipeline before every dashboard refresh.
""")
