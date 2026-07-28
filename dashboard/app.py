import os
import sys

sys.path.append(os.path.dirname(__file__))

import streamlit as st

from src.helpers import load_data, executive_kpis, format_money

st.set_page_config(
    page_title="Insurance Claims Recovery Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
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
    font-size:26px;
    font-weight:700;
    white-space:nowrap;
    overflow:visible;
}
</style>
""", unsafe_allow_html=True)

st.title("🚗 Insurance Claims Recovery Dashboard")

st.markdown("""
### Welcome

This dashboard provides an interactive, executive-level analysis of insurance
recovery claims performance.

Use the sidebar to navigate between:

- 📊 Executive Dashboard
- 🌍 Geographic Analysis
- 👨‍💼 Officer Performance
- 👤 Debtor Analysis
- ⚠ Recovery Reasons
- 📅 Time Analysis
- 🧹 Data Quality
""")

df = load_data()
kpis = executive_kpis(df)

st.divider()
st.subheader("Portfolio Snapshot")

col1, col2, col3, col4 = st.columns(4)

col1.metric("📄 Total Claims", f"{kpis['Total Claims']:,}")
col2.metric("💰 Recovery Portfolio", format_money(kpis["Recovery Amount"]))
col3.metric("✅ Collection Rate", f"{kpis['Collection Rate']:.2f}%")
col4.metric("⌛ Outstanding Balance", format_money(kpis["Remaining Amount"]))

st.info("Select a page from the left sidebar to begin exploring.")