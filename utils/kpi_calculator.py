"""
KPI Calculator — Sales & Revenue + Finance & Accounting formulas.
All functions accept pandas DataFrames or scalar values.
"""
import pandas as pd
import numpy as np
from typing import Optional


# ─────────────────────────────────────────────
#  SALES & REVENUE KPIs
# ─────────────────────────────────────────────

def total_revenue(df: pd.DataFrame, revenue_col: str) -> float:
    return df[revenue_col].sum()


def revenue_growth(current: float, previous: float) -> float:
    """Month-over-Month or Year-over-Year growth %."""
    if previous == 0:
        return 0.0
    return round(((current - previous) / previous) * 100, 2)


def average_deal_size(df: pd.DataFrame, revenue_col: str, deals_col: Optional[str] = None) -> float:
    if deals_col:
        total_deals = df[deals_col].sum()
    else:
        total_deals = len(df)
    return round(df[revenue_col].sum() / total_deals, 2) if total_deals else 0.0


def win_rate(won: int, total_opportunities: int) -> float:
    if total_opportunities == 0:
        return 0.0
    return round((won / total_opportunities) * 100, 2)


def customer_lifetime_value(avg_purchase_value: float, purchase_frequency: float, customer_lifespan_years: float) -> float:
    return round(avg_purchase_value * purchase_frequency * customer_lifespan_years, 2)


def churn_rate(churned_customers: int, total_customers_start: int) -> float:
    if total_customers_start == 0:
        return 0.0
    return round((churned_customers / total_customers_start) * 100, 2)


def monthly_recurring_revenue(df: pd.DataFrame, monthly_amount_col: str) -> float:
    return round(df[monthly_amount_col].sum(), 2)


def revenue_per_rep(total_rev: float, num_reps: int) -> float:
    return round(total_rev / num_reps, 2) if num_reps else 0.0


def pipeline_value(df: pd.DataFrame, deal_value_col: str, probability_col: Optional[str] = None) -> float:
    if probability_col and probability_col in df.columns:
        return round((df[deal_value_col] * df[probability_col] / 100).sum(), 2)
    return round(df[deal_value_col].sum(), 2)


# ─────────────────────────────────────────────
#  FINANCE & ACCOUNTING KPIs
# ─────────────────────────────────────────────

def gross_margin(revenue: float, cogs: float) -> float:
    if revenue == 0:
        return 0.0
    return round(((revenue - cogs) / revenue) * 100, 2)


def net_profit_margin(net_profit: float, revenue: float) -> float:
    if revenue == 0:
        return 0.0
    return round((net_profit / revenue) * 100, 2)


def ebitda(operating_income: float, depreciation: float, amortization: float) -> float:
    return round(operating_income + depreciation + amortization, 2)


def burn_rate(df: pd.DataFrame, expense_col: str, period: str = "monthly") -> float:
    """Average monthly cash burn."""
    total = df[expense_col].sum()
    months = len(df) if period == "monthly" else len(df) / 12
    return round(total / months, 2) if months else 0.0


def runway_months(cash_balance: float, monthly_burn: float) -> float:
    if monthly_burn <= 0:
        return float("inf")
    return round(cash_balance / monthly_burn, 1)


def current_ratio(current_assets: float, current_liabilities: float) -> float:
    if current_liabilities == 0:
        return 0.0
    return round(current_assets / current_liabilities, 2)


def accounts_receivable_days(avg_ar: float, annual_revenue: float) -> float:
    if annual_revenue == 0:
        return 0.0
    return round((avg_ar / annual_revenue) * 365, 1)


def accounts_payable_days(avg_ap: float, cogs: float) -> float:
    if cogs == 0:
        return 0.0
    return round((avg_ap / cogs) * 365, 1)


def operating_cash_flow(net_income: float, depreciation: float, working_capital_change: float) -> float:
    return round(net_income + depreciation - working_capital_change, 2)


def return_on_equity(net_income: float, shareholders_equity: float) -> float:
    if shareholders_equity == 0:
        return 0.0
    return round((net_income / shareholders_equity) * 100, 2)


# ─────────────────────────────────────────────
#  AUTO-DETECT & COMPUTE ALL KPIs FROM DATAFRAME
# ─────────────────────────────────────────────

COLUMN_ALIASES = {
    "revenue": ["revenue", "sales", "amount", "total_sales", "gross_revenue", "net_revenue", "income"],
    "cogs": ["cogs", "cost_of_goods", "cost_of_goods_sold", "cost_of_sales"],
    "expenses": ["expenses", "expense", "costs", "operating_expenses", "total_expenses"],
    "net_profit": ["net_profit", "profit", "net_income", "earnings"],
    "depreciation": ["depreciation", "depr", "d&a"],
    "date": ["date", "month", "period", "year", "time"],
    "deal_value": ["deal_value", "deal_size", "opportunity_value", "pipeline_value"],
    "probability": ["probability", "prob", "win_probability", "close_probability"],
}


def _find_col(df: pd.DataFrame, aliases: list[str]) -> Optional[str]:
    lowered = {c.lower(): c for c in df.columns}
    for alias in aliases:
        if alias in lowered:
            return lowered[alias]
    return None


def auto_compute_kpis(df: pd.DataFrame) -> dict:
    """
    Auto-detect columns and compute all applicable KPIs.
    Returns a dict of {kpi_name: value}.
    """
    results = {}
    rev_col = _find_col(df, COLUMN_ALIASES["revenue"])
    cogs_col = _find_col(df, COLUMN_ALIASES["cogs"])
    exp_col = _find_col(df, COLUMN_ALIASES["expenses"])
    profit_col = _find_col(df, COLUMN_ALIASES["net_profit"])
    depr_col = _find_col(df, COLUMN_ALIASES["depreciation"])
    date_col = _find_col(df, COLUMN_ALIASES["date"])
    deal_col = _find_col(df, COLUMN_ALIASES["deal_value"])
    prob_col = _find_col(df, COLUMN_ALIASES["probability"])

    if rev_col:
        results["Total Revenue"] = total_revenue(df, rev_col)
        results["Average Deal / Transaction Size"] = average_deal_size(df, rev_col)

        if cogs_col:
            cogs_total = df[cogs_col].sum()
            rev_total = df[rev_col].sum()
            results["Gross Margin (%)"] = gross_margin(rev_total, cogs_total)

        if profit_col:
            profit_total = df[profit_col].sum()
            rev_total = df[rev_col].sum()
            results["Net Profit Margin (%)"] = net_profit_margin(profit_total, rev_total)

        # MoM growth if date column exists
        if date_col:
            try:
                df[date_col] = pd.to_datetime(df[date_col])
                monthly = df.groupby(df[date_col].dt.to_period("M"))[rev_col].sum().sort_index()
                if len(monthly) >= 2:
                    results["MoM Revenue Growth (%)"] = revenue_growth(
                        float(monthly.iloc[-1]), float(monthly.iloc[-2])
                    )
            except Exception:
                pass

    if exp_col:
        burn = df[exp_col].mean()
        results["Avg Monthly Burn Rate"] = round(burn, 2)

    if deal_col:
        results["Pipeline Value"] = pipeline_value(df, deal_col, prob_col)

    if profit_col and depr_col:
        results["EBITDA"] = ebitda(
            df[profit_col].sum(),
            df[depr_col].sum(),
            0
        )

    return results


def kpis_to_text(kpis: dict, dataset_name: str = "uploaded data") -> str:
    """Convert KPI dict to a readable text chunk for embedding."""
    lines = [f"KPI Summary for {dataset_name}:", ""]
    for k, v in kpis.items():
        if isinstance(v, float):
            lines.append(f"  • {k}: {v:,.2f}")
        else:
            lines.append(f"  • {k}: {v}")
    return "\n".join(lines)