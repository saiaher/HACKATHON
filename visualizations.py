"""GovLENS - Visualization helpers. All functions take already-computed
risk data (df with risk_score/risk_level columns, or a breakdown dict)."""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def gauge_chart(score, title="Risk Score"):
    color = "#EF4444" if score >= 60 else "#F59E0B" if score >= 30 else "#10B981"
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={"x": [0, 1], "y": [0, 1]},
        title={"text": title, "font": {"size": 20}},
        gauge={
            "axis": {"range": [None, 100]},
            "bar": {"color": color},
            "bgcolor": "white",
            "borderwidth": 2,
            "bordercolor": "gray",
            "steps": [
                {"range": [0, 30], "color": "#D1FAE5"},
                {"range": [30, 60], "color": "#FEF3C7"},
                {"range": [60, 100], "color": "#FEE2E2"},
            ],
            "threshold": {"line": {"color": "black", "width": 4}, "thickness": 0.75, "value": score},
        },
    ))
    fig.update_layout(height=260, margin=dict(l=20, r=20, t=40, b=10), paper_bgcolor="white")
    return fig


def risk_breakdown_chart(breakdown):
    categories = ["Financial", "Cost", "Timeline", "Ghost Project", "Contractor", "ML Anomaly"]
    scores = [
        breakdown["financial"]["score"], breakdown["cost"]["score"], breakdown["timeline"]["score"],
        breakdown["ghost"]["score"], breakdown["contractor"]["score"], breakdown["ml_contribution"],
    ]
    max_scores = [25, 20, 20, 20, 15, 15]
    colors = ["#EF4444" if s > m * 0.6 else "#F59E0B" if s > m * 0.3 else "#10B981" for s, m in zip(scores, max_scores)]
    fig = go.Figure(go.Bar(y=categories, x=scores, orientation="h", marker=dict(color=colors),
                            text=[f"{s}/{m}" for s, m in zip(scores, max_scores)], textposition="auto"))
    fig.update_layout(title="Risk Breakdown by Category", xaxis_title="Score", height=300,
                       margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor="white")
    return fig


def risk_pie_chart(df):
    counts = df["risk_level"].value_counts().reindex(["LOW", "MEDIUM", "HIGH"]).fillna(0)
    fig = px.pie(values=counts.values, names=counts.index, title="Risk Distribution",
                 color=counts.index, color_discrete_map={"LOW": "#10B981", "MEDIUM": "#F59E0B", "HIGH": "#EF4444"})
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor="white")
    return fig


def geo_map(df):
    plot_df = df.dropna(subset=["gps_lat", "gps_lon"])
    if plot_df.empty:
        return None
    fig = px.scatter_geo(
        plot_df, lat="gps_lat", lon="gps_lon", color="risk_level",
        size="sanctioned_amount", hover_name="project_id",
        hover_data=["district", "state", "project_type", "risk_score", "est_completion_pct"],
        color_discrete_map={"LOW": "#10B981", "MEDIUM": "#F59E0B", "HIGH": "#EF4444"},
        scope="asia", height=420,
    )
    fig.update_geos(center=dict(lat=19.5, lon=75.5), projection_scale=5, showcountries=True)
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor="white")
    return fig


def timeline_chart(df):
    d = df.dropna(subset=["start_date"]).copy()
    if d.empty:
        return None
    d["month"] = d["start_date"].dt.to_period("M").astype(str)
    monthly = d.groupby("month").size().reset_index(name="count").sort_values("month")
    fig = px.line(monthly, x="month", y="count", title="Projects Started Over Time", markers=True)
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor="white",
                       xaxis_title="Month", yaxis_title="Projects")
    return fig


def bar_by(df, column, title):
    counts = df[column].value_counts().reset_index()
    counts.columns = [column, "count"]
    fig = px.bar(counts, x=column, y="count", title=title)
    fig.update_layout(height=320, margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor="white")
    return fig


def risk_by_group(df, column, title):
    grp = df.groupby(column)["risk_score"].mean().reset_index().sort_values("risk_score", ascending=False)
    fig = px.bar(grp, x=column, y="risk_score", title=title, color="risk_score",
                 color_continuous_scale=["#10B981", "#F59E0B", "#EF4444"])
    fig.update_layout(height=320, margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor="white")
    return fig


def fund_vs_expenditure_chart(df):
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["project_id"], y=df["sanctioned_amount"], name="Sanctioned"))
    fig.add_trace(go.Bar(x=df["project_id"], y=df["released_amount"], name="Released"))
    fig.add_trace(go.Bar(x=df["project_id"], y=df["expenditure"], name="Expenditure"))
    fig.update_layout(barmode="group", title="Fund Allocation vs Expenditure (sample)", height=350,
                       margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor="white")
    return fig
