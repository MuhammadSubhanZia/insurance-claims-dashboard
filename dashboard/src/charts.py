import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from .helpers import (
    location_summary,
    officer_summary,
    debtor_summary,
    debtor_type_summary,
    recovery_reason_summary,
    monthly_summary,
    time_summary,
    status_summary,
    completeness_summary,
    consistency_summary,
    validity_summary,
    MONTH_ORDER
)

BLUE = "#2563eb"
GREEN = "#16a34a"
RED = "#dc2626"
AMBER = "#d97706"

MONTH_TICKS = dict(
    tickmode="array",
    tickvals=list(range(1, 13)),
    ticktext=[
        "Jan", "Feb", "Mar", "Apr",
        "May", "Jun", "Jul", "Aug",
        "Sep", "Oct", "Nov", "Dec"
    ]
)


# -------------------------------------------------------
# EXECUTIVE
# -------------------------------------------------------

def collection_donut(df):

    values = [
        df["Collected Amount"].sum(),
        df["Remaining Amount"].sum()
    ]

    labels = [
        "Collected",
        "Remaining"
    ]

    fig = px.pie(
        values=values,
        names=labels,
        hole=0.65,
        color=labels,
        color_discrete_map={
            "Collected": GREEN,
            "Remaining": RED
        }
    )

    fig.update_layout(
        title="Recovery Collection Status",
        legend_title="",
        height=430,
        template="plotly_white"
    )

    return fig


def claim_status_chart(df):

    status = status_summary(df)

    fig = px.bar(
        status,
        x="Status",
        y="Claims",
        color="Claims",
        color_continuous_scale="Blues"
    )

    fig.update_layout(
        title="Claim Status Distribution",
        template="plotly_white",
        coloraxis_showscale=False,
        height=430
    )

    return fig


def top_locations_chart(df):

    summary = (
        location_summary(df)
        .head(10)
        .sort_values("Recovery")
    )

    fig = px.bar(
        summary,
        x="Recovery",
        y="Location",
        orientation="h",
        color="Recovery",
        color_continuous_scale="Blues"
    )

    fig.update_layout(
        title="Top 10 Locations by Recovery",
        template="plotly_white",
        coloraxis_showscale=False,
        height=430
    )

    return fig


def monthly_trend_chart(df):

    summary = monthly_summary(df)

    # Show every year present in the (already sidebar-filtered) data
    # rather than silently dropping older/newer years.
    summary["Month"] = pd.Categorical(
        summary["Month"],
        categories=range(1, 13),
        ordered=True
    )

    fig = px.line(
        summary,
        x="Month",
        y="Claims",
        color="Year",
        markers=True
    )

    fig.update_xaxes(**MONTH_TICKS)

    fig.update_layout(
        title="Monthly Claim Trend",
        template="plotly_white",
        height=430
    )

    return fig


def recovery_trend_chart(df):

    summary = monthly_summary(df)

    # Show every year present in the (already sidebar-filtered) data
    # rather than silently dropping older/newer years.
    summary["Month"] = pd.Categorical(
        summary["Month"],
        categories=range(1, 13),
        ordered=True
    )

    fig = px.line(
        summary,
        x="Month",
        y="Recovery",
        color="Year",
        markers=True
    )

    fig.update_xaxes(**MONTH_TICKS)

    fig.update_layout(
        title="Recovery Trend",
        template="plotly_white",
        height=430
    )

    return fig


def officer_recovery_chart(df):

    summary = (
        officer_summary(df)
        .head(15)
        .sort_values("Recovery")
    )

    fig = px.bar(
        summary,
        x="Recovery",
        y="Officer",
        orientation="h",
        color="Recovery",
        color_continuous_scale="Blues"
    )

    fig.update_layout(
        title="Top Officers by Recovery",
        template="plotly_white",
        coloraxis_showscale=False,
        height=430
    )

    return fig


# -------------------------------------------------------
# OFFICER PERFORMANCE
# -------------------------------------------------------

def claims_per_officer_chart(df):

    summary = (
        officer_summary(df)
        .sort_values("Claims", ascending=False)
        .head(15)
        .sort_values("Claims")
    )

    fig = px.bar(
        summary,
        x="Claims",
        y="Officer",
        orientation="h",
        color="Claims",
        color_continuous_scale="Blues"
    )

    fig.update_layout(
        title="Claims Handled by Officer",
        template="plotly_white",
        coloraxis_showscale=False,
        height=430
    )

    return fig


def officer_collection_chart(df):

    summary = (
        officer_summary(df)
        .sort_values("Recovery", ascending=False)
        .head(15)
        .sort_values("Collection Rate")
    )

    fig = px.bar(
        summary,
        x="Collection Rate",
        y="Officer",
        orientation="h",
        color="Collection Rate",
        color_continuous_scale="RdYlGn"
    )

    fig.update_layout(
        title="Officer Collection Rate (%)",
        template="plotly_white",
        coloraxis_showscale=False,
        height=430
    )

    return fig


def officer_collected_chart(df):

    summary = (
        officer_summary(df)
        .sort_values("Collected", ascending=False)
        .head(15)
        .sort_values("Collected")
    )

    fig = px.bar(
        summary,
        x="Collected",
        y="Officer",
        orientation="h",
        color="Collected",
        color_continuous_scale="Blues"
    )

    fig.update_layout(
        title="Total Collected by Officer",
        template="plotly_white",
        coloraxis_showscale=False,
        height=430
    )

    return fig


# -------------------------------------------------------
# GEOGRAPHIC
# -------------------------------------------------------

def claims_by_location_chart(df):

    summary = (
        location_summary(df)
        .sort_values("Claims", ascending=False)
        .head(10)
        .sort_values("Claims")
    )

    fig = px.bar(
        summary,
        x="Claims",
        y="Location",
        orientation="h",
        color="Claims",
        color_continuous_scale="Blues"
    )

    fig.update_layout(
        title="Claims Volume by Location",
        template="plotly_white",
        coloraxis_showscale=False,
        height=430
    )

    return fig


def location_collection_chart(df):

    summary = (
        location_summary(df)
        .sort_values("Recovery", ascending=False)
        .head(15)
        .sort_values("Collection Rate")
    )

    fig = px.bar(
        summary,
        x="Collection Rate",
        y="Location",
        orientation="h",
        color="Collection Rate",
        color_continuous_scale="RdYlGn"
    )

    fig.update_layout(
        title="Collection Rate by Location (%)",
        template="plotly_white",
        coloraxis_showscale=False,
        height=430
    )

    return fig


def remaining_by_location_chart(df):

    summary = (
        location_summary(df)
        .sort_values("Remaining", ascending=False)
        .head(10)
        .sort_values("Remaining")
    )

    fig = px.bar(
        summary,
        x="Remaining",
        y="Location",
        orientation="h",
        color="Remaining",
        color_continuous_scale="Reds"
    )

    fig.update_layout(
        title="Outstanding Balance by Location",
        template="plotly_white",
        coloraxis_showscale=False,
        height=430
    )

    return fig


def location_performance_matrix(df):

    summary = location_summary(df)

    fig = px.scatter(
        summary,
        x="Recovery",
        y="Collection Rate",
        size="Claims",
        color="Remaining",
        hover_name="Location",
        color_continuous_scale="Reds",
        size_max=45
    )

    fig.update_layout(
        title="Location Performance Matrix",
        template="plotly_white",
        height=480
    )

    return fig


# -------------------------------------------------------
# DEBTOR
# -------------------------------------------------------

def top_debtors_chart(df):

    summary = (
        debtor_summary(df)
        .sort_values("Remaining", ascending=False)
        .head(15)
        .sort_values("Remaining")
    )

    fig = px.bar(
        summary,
        x="Remaining",
        y="Debtor Name",
        orientation="h",
        color="Remaining",
        color_continuous_scale="Reds"
    )

    fig.update_layout(
        title="Top Debtors by Remaining Amount",
        template="plotly_white",
        coloraxis_showscale=False,
        height=430
    )

    return fig


def debtor_type_chart(df):

    summary = debtor_type_summary(df)

    fig = px.pie(
        summary,
        values="Recovery",
        names="Debtor Type",
        hole=.55
    )

    fig.update_layout(
        title="Recovery by Debtor Type",
        template="plotly_white",
        height=430
    )

    return fig


def debtor_performance_matrix(df, min_claims=3):

    summary = debtor_summary(df)
    summary = summary[summary["Claims"] >= min_claims]

    fig = px.scatter(
        summary,
        x="Recovery",
        y="Collection Rate",
        size="Claims",
        color="Remaining",
        hover_name="Debtor Name",
        color_continuous_scale="Reds",
        size_max=40
    )

    fig.update_layout(
        title=f"Debtor Performance Matrix (Claims ≥ {min_claims})",
        template="plotly_white",
        height=480
    )

    return fig


# -------------------------------------------------------
# RECOVERY REASON
# -------------------------------------------------------

def recovery_reason_chart(df):

    summary = (
        recovery_reason_summary(df)
        .head(10)
        .sort_values("Recovery")
    )

    fig = px.bar(
        summary,
        x="Recovery",
        y="Recovery Reason",
        orientation="h",
        color="Recovery",
        color_continuous_scale="Blues"
    )

    fig.update_layout(
        title="Top Recovery Reasons",
        template="plotly_white",
        coloraxis_showscale=False,
        height=430
    )

    return fig


def recovery_reason_rate_chart(df, min_claims=10):

    summary = recovery_reason_summary(df)
    summary = (
        summary[summary["Claims"] >= min_claims]
        .head(15)
        .sort_values("Collection Rate")
    )

    fig = px.bar(
        summary,
        x="Collection Rate",
        y="Recovery Reason",
        orientation="h",
        color="Collection Rate",
        color_continuous_scale="RdYlGn"
    )

    fig.update_layout(
        title=f"Collection Rate by Reason (Claims ≥ {min_claims})",
        template="plotly_white",
        coloraxis_showscale=False,
        height=430
    )

    return fig


def reason_performance_matrix(df, min_claims=10):

    summary = recovery_reason_summary(df)
    summary = summary[summary["Claims"] >= min_claims]

    fig = px.scatter(
        summary,
        x="Recovery",
        y="Collection Rate",
        size="Claims",
        color="Remaining",
        hover_name="Recovery Reason",
        color_continuous_scale="Reds",
        size_max=40
    )

    fig.update_layout(
        title=f"Recovery Reason Performance Matrix (Claims ≥ {min_claims})",
        template="plotly_white",
        height=480
    )

    return fig


# -------------------------------------------------------
# TIME ANALYSIS
# -------------------------------------------------------

def time_claims_trend_chart(df):

    summary = time_summary(df)

    fig = px.line(
        summary,
        x="Accident Month",
        y="Claims",
        color="Accident Year",
        markers=True,
        category_orders={"Accident Month": MONTH_ORDER}
    )

    fig.update_layout(
        title="Monthly Claim Trend",
        template="plotly_white",
        xaxis_title="",
        height=430
    )

    return fig


def time_recovery_trend_chart(df):

    summary = time_summary(df)

    fig = px.line(
        summary,
        x="Accident Month",
        y="Recovery",
        color="Accident Year",
        markers=True,
        category_orders={"Accident Month": MONTH_ORDER}
    )

    fig.update_layout(
        title="Monthly Recovery Trend",
        template="plotly_white",
        xaxis_title="",
        height=430
    )

    return fig


def time_collection_rate_chart(df):

    summary = time_summary(df)

    fig = px.line(
        summary,
        x="Accident Month",
        y="Collection Rate",
        color="Accident Year",
        markers=True,
        category_orders={"Accident Month": MONTH_ORDER}
    )

    fig.update_layout(
        title="Collection Rate Trend (%)",
        template="plotly_white",
        xaxis_title="",
        height=430
    )

    return fig


def recovery_delay_histogram(df):

    fig = px.histogram(
        df,
        x="Recovery Delay (Days)",
        nbins=40,
        color_discrete_sequence=[BLUE]
    )

    fig.update_layout(
        title="Recovery Delay Distribution",
        template="plotly_white",
        height=430
    )

    return fig


# -------------------------------------------------------
# DATA QUALITY
# -------------------------------------------------------

def completeness_chart(df):

    summary = (
        completeness_summary(df)
        .head(15)
        .sort_values("Missing %")
    )

    fig = px.bar(
        summary,
        x="Missing %",
        y="Column",
        orientation="h",
        color="Missing %",
        color_continuous_scale="Reds",
        text="Missing %"
    )

    fig.update_layout(
        title="Top Columns with Missing Values",
        template="plotly_white",
        coloraxis_showscale=False,
        height=430
    )

    return fig


def consistency_chart(df):

    summary = consistency_summary(df)

    fig = px.bar(
        summary,
        x="Check",
        y="Count",
        color="Check",
        text="Count"
    )

    fig.update_layout(
        title="Consistency Checks",
        template="plotly_white",
        xaxis_title="",
        showlegend=False,
        height=430
    )

    return fig


def validity_chart(df):

    summary = validity_summary(df)

    fig = px.bar(
        summary,
        x="Issue",
        y="Count",
        color="Issue",
        text="Count"
    )

    fig.update_layout(
        title="Validity Checks",
        template="plotly_white",
        xaxis_title="",
        showlegend=False,
        height=430
    )

    return fig


def quality_gauge_chart(score):

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            title={"text": "Overall Data Quality Score"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": BLUE},
                "steps": [
                    {"range": [0, 50], "color": "#fee2e2"},
                    {"range": [50, 80], "color": "#fef3c7"},
                    {"range": [80, 100], "color": "#dcfce7"}
                ]
            }
        )
    )

    fig.update_layout(
        template="plotly_white",
        height=350
    )

    return fig


def placeholder_chart(df):

    counts = (
        df["Debtor Number Status"]
        .value_counts()
        .reset_index()
    )

    counts.columns = [
        "Status",
        "Count"
    ]

    fig = px.pie(
        counts,
        values="Count",
        names="Status",
        hole=.6
    )

    fig.update_layout(
        title="Placeholder Numbers",
        template="plotly_white",
        height=430
    )

    return fig