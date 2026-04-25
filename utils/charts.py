"""
Reusable Plotly chart helpers for KPI Dashboard.
All functions return a plotly Figure object.
"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Optional

BRAND_COLORS = {
    "primary": "#0F62FE",
    "success": "#24A148",
    "warning": "#F1C21B",
    "danger":  "#DA1E28",
    "neutral": "#6F6F6F",
    "bg":      "#161616",
    "surface": "#262626",
    "text":    "#F4F4F4",
}

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=BRAND_COLORS["text"], family="IBM Plex Mono, monospace"),
    margin=dict(l=16, r=16, t=40, b=16),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
)


def revenue_trend(df: pd.DataFrame, date_col: str, revenue_col: str, title: str = "Revenue Trend") -> go.Figure:
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    monthly = df.groupby(df[date_col].dt.to_period("M"))[revenue_col].sum().reset_index()
    monthly[date_col] = monthly[date_col].astype(str)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly[date_col],
        y=monthly[revenue_col],
        mode="lines+markers",
        line=dict(color=BRAND_COLORS["primary"], width=2.5),
        marker=dict(size=6, color=BRAND_COLORS["primary"]),
        fill="tozeroy",
        fillcolor="rgba(15,98,254,0.08)",
        name="Revenue",
    ))
    fig.update_layout(title=title, **CHART_LAYOUT)
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.06)")
    return fig


def kpi_bar_chart(kpi_dict: dict, title: str = "KPI Overview") -> go.Figure:
    labels = list(kpi_dict.keys())
    values = [v for v in kpi_dict.values() if isinstance(v, (int, float))]
    labels = [k for k, v in kpi_dict.items() if isinstance(v, (int, float))]

    colors = [BRAND_COLORS["primary"]] * len(labels)

    fig = go.Figure(go.Bar(
        x=labels,
        y=values,
        marker=dict(color=colors, line=dict(color="rgba(0,0,0,0)")),
        text=[f"{v:,.1f}" for v in values],
        textposition="outside",
        textfont=dict(color=BRAND_COLORS["text"]),
    ))
    fig.update_layout(title=title, xaxis_tickangle=-30, **CHART_LAYOUT)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.06)")
    return fig


def margin_gauge(value: float, title: str = "Gross Margin", max_val: float = 100) -> go.Figure:
    color = BRAND_COLORS["success"] if value >= 40 else (
        BRAND_COLORS["warning"] if value >= 20 else BRAND_COLORS["danger"]
    )
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        number=dict(suffix="%", font=dict(color=BRAND_COLORS["text"])),
        gauge=dict(
            axis=dict(range=[0, max_val], tickcolor=BRAND_COLORS["neutral"]),
            bar=dict(color=color),
            bgcolor="rgba(255,255,255,0.05)",
            bordercolor="rgba(0,0,0,0)",
            steps=[
                dict(range=[0, 20], color="rgba(218,30,40,0.12)"),
                dict(range=[20, 40], color="rgba(241,194,27,0.12)"),
                dict(range=[40, max_val], color="rgba(36,161,72,0.12)"),
            ],
        ),
        title=dict(text=title, font=dict(color=BRAND_COLORS["text"])),
    ))
    fig.update_layout(height=220, **CHART_LAYOUT)
    return fig


def revenue_by_category(df: pd.DataFrame, category_col: str, revenue_col: str, title: str = "Revenue by Category") -> go.Figure:
    grouped = df.groupby(category_col)[revenue_col].sum().sort_values(ascending=False).reset_index()
    palette = px.colors.sequential.Blues_r[:len(grouped)]
    fig = go.Figure(go.Pie(
        labels=grouped[category_col],
        values=grouped[revenue_col],
        hole=0.55,
        marker=dict(colors=palette),
        textfont=dict(color=BRAND_COLORS["text"]),
    ))
    fig.update_layout(title=title, **CHART_LAYOUT)
    return fig


def monthly_comparison(df: pd.DataFrame, date_col: str, revenue_col: str, expense_col: Optional[str] = None) -> go.Figure:
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    grp_cols = [revenue_col]
    if expense_col and expense_col in df.columns:
        grp_cols.append(expense_col)
    monthly = df.groupby(df[date_col].dt.to_period("M"))[grp_cols].sum().reset_index()
    monthly[date_col] = monthly[date_col].astype(str)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=monthly[date_col], y=monthly[revenue_col],
        name="Revenue", marker_color=BRAND_COLORS["primary"],
    ))
    if expense_col and expense_col in monthly.columns:
        fig.add_trace(go.Bar(
            x=monthly[date_col], y=monthly[expense_col],
            name="Expenses", marker_color=BRAND_COLORS["danger"],
        ))
    fig.update_layout(title="Revenue vs Expenses", barmode="group", **CHART_LAYOUT)
    return fig


def runway_indicator(runway_months: float) -> go.Figure:
    color = BRAND_COLORS["success"] if runway_months >= 18 else (
        BRAND_COLORS["warning"] if runway_months >= 6 else BRAND_COLORS["danger"]
    )
    fig = go.Figure(go.Indicator(
        mode="number+delta",
        value=runway_months,
        number=dict(suffix=" mo", font=dict(color=color, size=48)),
        title=dict(text="Cash Runway", font=dict(color=BRAND_COLORS["text"])),
    ))
    fig.update_layout(height=160, **CHART_LAYOUT)
    return fig