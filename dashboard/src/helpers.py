import pandas as pd
import streamlit as st

from src.preprocessing import prepare_data
from src.config import DATA_PATH


MONTH_ORDER = [
    "January", "February", "March", "April",
    "May", "June", "July", "August",
    "September", "October", "November", "December"
]


def format_money(value, currency="SAR"):
    """
    Compact currency formatting for KPI tiles (e.g. "SAR 35.73M"
    instead of "SAR 35,733,872"), so large totals never overflow
    and get clipped with "...".
    """

    if value is None or pd.isna(value):
        return f"{currency} 0"

    sign = "-" if value < 0 else ""
    value = abs(value)

    if value >= 1_000_000:
        formatted = f"{value / 1_000_000:.2f}M"
    elif value >= 1_000:
        formatted = f"{value / 1_000:.1f}K"
    else:
        formatted = f"{value:,.0f}"

    return f"{sign}{currency} {formatted}"


@st.cache_data(show_spinner="Loading claims data...")
def load_data(data_path=DATA_PATH):
    """
    Loads and preprocesses the claims dataset. Cached so every page
    reuses the same cleaned dataframe instead of re-reading Excel.
    """
    return prepare_data(data_path)


# -------------------------------------------------------
# EXECUTIVE
# -------------------------------------------------------

def executive_kpis(df):
    """
    Executive KPI calculations.
    """

    recovery = df["Recovery Amount"].sum()
    collected = df["Collected Amount"].sum()
    remaining = df["Remaining Amount"].sum()

    collection_rate = (
        collected / recovery * 100
        if recovery > 0 else 0
    )

    outstanding_rate = (
        remaining / recovery * 100
        if recovery > 0 else 0
    )

    avg_recovery = (
        recovery / len(df)
        if len(df) else 0
    )

    return {

        "Total Claims": len(df),

        "Recovery Amount": recovery,

        "Collected Amount": collected,

        "Remaining Amount": remaining,

        "Collection Rate": round(collection_rate, 2),

        "Outstanding Rate": round(outstanding_rate, 2),

        "Average Recovery": round(avg_recovery, 2),

        "Unique Debtors":
            df["Debtor Number"].nunique(),

        "Locations":
            df["Location"].nunique(),

        "Officers":
            df["Officer"].nunique(),

        "Open Claims":
            (df["Status"] != "Closed").sum(),

        "Closed Claims":
            (df["Status"] == "Closed").sum()

    }


def status_summary(df):
    """
    Claim counts by status, used for the status distribution chart.
    """

    summary = (
        df["Status"]
        .fillna("Unknown")
        .value_counts()
        .reset_index()
    )

    summary.columns = ["Status", "Claims"]

    return summary


# -------------------------------------------------------
# GEOGRAPHIC
# -------------------------------------------------------

def location_summary(df):
    """
    Geographic summary by standardized location.
    """

    summary = (
        df.groupby("Location")
        .agg(
            Claims=("Claim ID", "count"),
            Recovery=("Recovery Amount", "sum"),
            Collected=("Collected Amount", "sum"),
            Remaining=("Remaining Amount", "sum")
        )
        .reset_index()
    )

    summary["Collection Rate"] = (
        summary["Collected"]
        / summary["Recovery"]
        * 100
    ).round(2)

    summary["Avg Recovery"] = (
        summary["Recovery"]
        / summary["Claims"]
    ).round(2)

    summary["Priority"] = summary["Collection Rate"].apply(
        lambda rate:
            "🟢 Healthy" if rate >= 70 else
            "🟡 Watch" if rate >= 40 else
            "🔴 Critical"
    )

    return summary.sort_values(
        "Recovery",
        ascending=False
    )


# -------------------------------------------------------
# OFFICER
# -------------------------------------------------------

def officer_summary(df):
    """
    Officer performance summary.
    """

    summary = (
        df.groupby("Officer")
        .agg(
            Claims=("Claim ID", "count"),
            Recovery=("Recovery Amount", "sum"),
            Collected=("Collected Amount", "sum"),
            Remaining=("Remaining Amount", "sum")
        )
        .reset_index()
    )

    summary["Collection Rate"] = (
        summary["Collected"]
        / summary["Recovery"]
        * 100
    ).round(2)

    summary["Avg Recovery"] = (
        summary["Recovery"]
        / summary["Claims"]
    ).round(2)

    return summary.sort_values(
        "Recovery",
        ascending=False
    )


# -------------------------------------------------------
# DEBTOR
# -------------------------------------------------------

def debtor_summary(df):
    """
    Debtor level summary.
    """

    summary = (
        df.groupby(
            ["Debtor Number", "Debtor Name", "Debtor Type"]
        )
        .agg(
            Claims=("Claim ID", "count"),
            Recovery=("Recovery Amount", "sum"),
            Collected=("Collected Amount", "sum"),
            Remaining=("Remaining Amount", "sum")
        )
        .reset_index()
    )

    summary["Collection Rate"] = (
        summary["Collected"]
        / summary["Recovery"]
        * 100
    ).round(2)

    return summary.sort_values(
        "Recovery",
        ascending=False
    )


def debtor_type_summary(df):
    """
    Recovery performance grouped by debtor type (Insured / Third Party).
    """

    summary = (
        df.groupby("Debtor Type")
        .agg(
            Debtors=("Debtor Number", "nunique"),
            Claims=("Claim ID", "count"),
            Recovery=("Recovery Amount", "sum"),
            Collected=("Collected Amount", "sum"),
            Remaining=("Remaining Amount", "sum")
        )
        .reset_index()
    )

    summary["Collection Rate"] = (
        summary["Collected"]
        / summary["Recovery"]
        * 100
    ).round(2)

    return summary.sort_values(
        "Recovery",
        ascending=False
    )


def priority_debtors(df, min_claims=3, collection_rate_threshold=20):
    """
    High-exposure, low-collection debtors that should be prioritized
    for recovery efforts (above-median recovery, poor collection rate).
    """

    summary = debtor_summary(df)
    summary = summary[summary["Claims"] >= min_claims]

    if summary.empty:
        return summary

    priority = summary[
        (summary["Recovery"] > summary["Recovery"].median()) &
        (summary["Collection Rate"] < collection_rate_threshold)
    ]

    return priority.sort_values("Remaining", ascending=False)


# -------------------------------------------------------
# RECOVERY REASON
# -------------------------------------------------------

def recovery_reason_summary(df):
    """
    Recovery reason summary.
    """

    summary = (
        df.groupby("Recovery Reason")
        .agg(
            Claims=("Claim ID", "count"),
            Recovery=("Recovery Amount", "sum"),
            Collected=("Collected Amount", "sum"),
            Remaining=("Remaining Amount", "sum")
        )
        .reset_index()
    )

    summary["Collection Rate"] = (
        summary["Collected"]
        / summary["Recovery"]
        * 100
    ).round(2)

    summary["Avg Recovery"] = (
        summary["Recovery"]
        / summary["Claims"]
    ).round(2)

    return summary.sort_values(
        "Recovery",
        ascending=False
    )


def priority_reasons(df, min_claims=10, collection_rate_threshold=20):
    """
    Recovery reasons with large financial exposure but poor collection
    performance - operational bottlenecks worth prioritizing.
    """

    summary = recovery_reason_summary(df)
    summary = summary[summary["Claims"] >= min_claims]

    if summary.empty:
        return summary

    priority = summary[
        (summary["Recovery"] > summary["Recovery"].median()) &
        (summary["Collection Rate"] < collection_rate_threshold)
    ]

    return priority.sort_values("Remaining", ascending=False)


# -------------------------------------------------------
# TIME
# -------------------------------------------------------

def monthly_summary(df):
    """
    Monthly time analysis (numeric month, used for continuous trend
    lines on the Executive Dashboard).
    """

    temp = df.copy()

    temp["Year"] = temp["Accident Date"].dt.year
    temp["Month"] = temp["Accident Date"].dt.month
    temp["Month Name"] = temp["Accident Date"].dt.strftime("%b")

    summary = (
        temp.groupby(
            ["Year", "Month", "Month Name"]
        )
        .agg(
            Claims=("Claim ID", "count"),
            Recovery=("Recovery Amount", "sum"),
            Collected=("Collected Amount", "sum")
        )
        .reset_index()
        .sort_values(["Year", "Month"])
    )

    summary["Remaining"] = summary["Recovery"] - summary["Collected"]

    summary["Collection Rate"] = (
        summary["Collected"] / summary["Recovery"] * 100
    ).round(2)

    return summary


def time_summary(df):
    """
    Monthly time analysis with named months, used on the Time Analysis
    page (mirrors the 07_Time_Analysis notebook).
    """

    temp = df.copy()

    temp["Accident Year"] = temp["Accident Date"].dt.year
    temp["Accident Month"] = temp["Accident Date"].dt.month_name()
    temp["Accident Month No"] = temp["Accident Date"].dt.month

    summary = (
        temp.groupby(
            ["Accident Year", "Accident Month", "Accident Month No"]
        )
        .agg(
            Claims=("Claim ID", "count"),
            Recovery=("Recovery Amount", "sum"),
            Collected=("Collected Amount", "sum")
        )
        .reset_index()
    )

    summary["Accident Month"] = pd.Categorical(
        summary["Accident Month"],
        categories=MONTH_ORDER,
        ordered=True
    )

    summary["Collection Rate"] = (
        summary["Collected"] / summary["Recovery"] * 100
    ).round(2)

    summary["Accident Year"] = summary["Accident Year"].astype("Int64")

    return summary.sort_values(["Accident Year", "Accident Month No"])


def recovery_delay_kpis(df):
    """
    Recovery delay KPIs for the Time Analysis page.
    """

    delay = df["Recovery Delay (Days)"].dropna()

    return {
        "Average Delay": round(delay.mean(), 1) if len(delay) else 0,
        "Median Delay": round(delay.median(), 1) if len(delay) else 0,
        "Max Delay": round(delay.max(), 1) if len(delay) else 0,
        "Slow Cases (> 180 Days)": int((delay > 180).sum())
    }


# -------------------------------------------------------
# DATA QUALITY
# -------------------------------------------------------

def data_quality_summary(df):
    """
    Data quality metrics.
    """

    return {
        "Rows": len(df),
        "Columns": len(df.columns),
        "Duplicate Claims": df["Claim ID"].duplicated().sum(),
        "Missing Values": int(df.isna().sum().sum()),
        "Placeholder Numbers": (
            df["Debtor Number Status"]
            == "Placeholder"
        ).sum()
    }


def completeness_summary(df):
    """
    Missing value counts/percentages per column.
    """

    summary = pd.DataFrame({
        "Column": df.columns,
        "Missing": df.isna().sum().values,
        "Missing %": (df.isna().mean() * 100).round(2).values
    })

    return summary.sort_values("Missing %", ascending=False)


def consistency_summary(df):
    """
    Consistency checks: how much of the dataset was successfully
    standardized during preprocessing.
    """

    return pd.DataFrame({
        "Check": [
            "Standardized Locations",
            "Standardized Recovery Reasons",
            "Placeholder Debtor Numbers"
        ],
        "Count": [
            (df["Location"] != "Unknown").sum(),
            (df["Recovery Reason"] != "Not Specified").sum(),
            (df["Debtor Number Status"] == "Placeholder").sum()
        ]
    })


def validity_summary(df):
    """
    Validity checks: business-rule violations in the financial fields.
    """

    invalid_amounts = (
        df["Collected Amount"] > df["Recovery Amount"]
    ).sum()

    negative_remaining = (
        df["Remaining Amount"] < 0
    ).sum()

    future_accidents = (
        df["Accident Date"] > pd.Timestamp.today()
    ).sum()

    return pd.DataFrame({
        "Issue": [
            "Collected > Recovery",
            "Negative Remaining Amount",
            "Future Accident Dates"
        ],
        "Count": [
            invalid_amounts,
            negative_remaining,
            future_accidents
        ]
    })


def uniqueness_summary(df):
    """
    Duplicate record checks.
    """

    return pd.DataFrame({
        "Metric": ["Duplicate Claim IDs", "Duplicate Claim Numbers"],
        "Count": [
            df["Claim ID"].duplicated().sum(),
            df["Claim Number"].duplicated().sum()
        ]
    })


def data_quality_score(df):
    """
    Overall dataset health score out of 100 (mirrors 08_Data_Quality
    notebook: penalizes missing data, duplicate claim numbers,
    placeholder debtor numbers, and unknown locations).
    """

    missing_percentage = (
        df.isna().sum().sum()
        / (len(df) * len(df.columns))
        * 100
    )

    duplicate_claim_number = df["Claim Number"].duplicated().sum()

    placeholder_numbers_count = (
        df["Debtor Number Status"] == "Placeholder"
    ).sum()

    unknown_locations = (df["Location"] == "Unknown").sum()

    quality = 100
    quality -= missing_percentage * 0.3
    quality -= duplicate_claim_number * 0.2
    quality -= placeholder_numbers_count * 0.05
    quality -= unknown_locations * 0.05

    return max(0, round(quality, 2))


def business_risks_summary(df):
    """
    Business risk register shown on the Data Quality page.
    """

    return pd.DataFrame({
        "Risk": [
            "Missing Operational Data",
            "Placeholder Contact Numbers",
            "Duplicate Claim Numbers",
            "Unknown Locations"
        ],
        "Business Impact": [
            "Incomplete Reporting",
            "Customer Follow-up Failure",
            "Reporting/Reconciliation Errors",
            "Reduced Geographic Insight"
        ],
        "Count": [
            int(df.isna().sum().sum()),
            int((df["Debtor Number Status"] == "Placeholder").sum()),
            int(df["Claim Number"].duplicated().sum()),
            int((df["Location"] == "Unknown").sum())
        ]
    })