"""
Page 2 — KPI Dashboard
Auto-compute KPIs from session DataFrames and render Plotly charts.
"""
import streamlit as st
import pandas as pd
from utils.kpi_calculator import auto_compute_kpis, COLUMN_ALIASES
from utils.charts import (
    revenue_trend, kpi_bar_chart, margin_gauge,
    revenue_by_category, monthly_comparison, runway_indicator,
)

st.set_page_config(page_title="KPI Dashboard · KPIverse", layout="wide")

# Auth guard
if "user" not in st.session_state:
    st.warning("Please sign in to view the dashboard.")
    st.page_link("app.py", label="→ Go to Sign In")
    st.stop()

user = st.session_state["user"]

st.markdown("# KPI Dashboard")
st.markdown("Auto-detected KPIs and visualizations from your uploaded data.")
st.divider()

# ── Guard: no data ─────────────────────────────────────────────────────────────
loaded = st.session_state.get("loaded_dfs", {})
if not loaded:
    st.warning("No data loaded. Go to **Upload Data** and load a CSV, Excel, or SQL table first.")
    st.page_link("pages/1_Upload_Data.py", label="→ Upload Data")
    st.stop()

# ── Dataset selector ───────────────────────────────────────────────────────────
dataset_name = st.selectbox("Select dataset", list(loaded.keys()))
df: pd.DataFrame = loaded[dataset_name]

st.caption(f"`{dataset_name}` — {df.shape[0]:,} rows × {df.shape[1]} columns")
st.divider()

# ── Auto-compute KPIs ──────────────────────────────────────────────────────────
kpis = auto_compute_kpis(df)

# ── KPI Metric Cards ───────────────────────────────────────────────────────────
if kpis:
    st.markdown("### Key Metrics")
    cols = st.columns(min(4, len(kpis)))
    for i, (k, v) in enumerate(kpis.items()):
        with cols[i % len(cols)]:
            if isinstance(v, float) and "%" in k:
                st.metric(k, f"{v:.1f}%")
            elif isinstance(v, float):
                st.metric(k, f"{v:,.2f}")
            else:
                st.metric(k, str(v))
else:
    st.info("Could not auto-detect standard KPI columns. Use the column mapper below.")

st.divider()

# ── Column Mapper ──────────────────────────────────────────────────────────────
with st.expander("Column Mapper (override auto-detection)", expanded=False):
    st.markdown("Map your column names to KPI categories:")
    c1, c2, c3 = st.columns(3)
    col_options = ["— none —"] + list(df.columns)

    with c1:
        rev_col = st.selectbox("Revenue / Sales column", col_options)
        cogs_col = st.selectbox("COGS column", col_options)
    with c2:
        date_col = st.selectbox("Date / Period column", col_options)
        exp_col = st.selectbox("Expenses column", col_options)
    with c3:
        cat_col = st.selectbox("Category / Segment column", col_options)
        profit_col = st.selectbox("Net Profit column", col_options)

    rev_col = None if rev_col == "— none —" else rev_col
    cogs_col = None if cogs_col == "— none —" else cogs_col
    date_col = None if date_col == "— none —" else date_col
    exp_col = None if exp_col == "— none —" else exp_col
    cat_col = None if cat_col == "— none —" else cat_col
    profit_col = None if profit_col == "— none —" else profit_col

st.divider()

# ── Charts Section ─────────────────────────────────────────────────────────────
st.markdown("### Visualizations")

charts_rendered = 0

# Revenue trend
if rev_col and date_col:
    try:
        fig = revenue_trend(df, date_col, rev_col)
        st.plotly_chart(fig, use_container_width=True)
        charts_rendered += 1
    except Exception as e:
        st.warning(f"Could not render revenue trend: {e}")

# Revenue vs Expenses
if rev_col and date_col:
    try:
        fig = monthly_comparison(df, date_col, rev_col, exp_col)
        st.plotly_chart(fig, use_container_width=True)
        charts_rendered += 1
    except Exception as e:
        st.warning(f"Could not render comparison: {e}")

# Margin gauges
col_g1, col_g2 = st.columns(2)
if kpis.get("Gross Margin (%)") is not None:
    with col_g1:
        fig = margin_gauge(kpis["Gross Margin (%)"], "Gross Margin")
        st.plotly_chart(fig, use_container_width=True)
        charts_rendered += 1

if kpis.get("Net Profit Margin (%)") is not None:
    with col_g2:
        fig = margin_gauge(kpis["Net Profit Margin (%)"], "Net Profit Margin", max_val=50)
        st.plotly_chart(fig, use_container_width=True)
        charts_rendered += 1

# Revenue by category (donut)
if rev_col and cat_col:
    try:
        col1, col2 = st.columns(2)
        with col1:
            fig = revenue_by_category(df, cat_col, rev_col)
            st.plotly_chart(fig, use_container_width=True)
            charts_rendered += 1
    except Exception as e:
        st.warning(f"Could not render category chart: {e}")

# KPI bar chart from auto-computed values
if kpis and len(kpis) >= 2:
    # Only include numeric KPIs that make sense in a bar chart (no %)
    bar_kpis = {k: v for k, v in kpis.items() if isinstance(v, (int, float)) and "%" not in k}
    if bar_kpis:
        fig = kpi_bar_chart(bar_kpis)
        st.plotly_chart(fig, use_container_width=True)
        charts_rendered += 1

# Fallback
if charts_rendered == 0:
    st.info("No charts could be auto-rendered. Use the **Column Mapper** above to map your columns and charts will appear automatically.")

st.divider()

# ── Raw Data Preview ───────────────────────────────────────────────────────────
with st.expander("Raw Data Preview"):
    st.dataframe(df, use_container_width=True, height=300)

    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        csv = df.to_csv(index=False)
        st.download_button("⬇ Download as CSV", csv, file_name=f"{dataset_name}.csv", mime="text/csv")