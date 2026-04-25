"""
Data Ingestor — handles CSV, Excel, and SQL ingestion.
Returns normalized pandas DataFrames.
"""
import io
import pandas as pd
from sqlalchemy import create_engine, text, inspect
from typing import Optional


# ─────────────────────────────────────────────
#  CSV / EXCEL
# ─────────────────────────────────────────────

def ingest_csv(file_bytes: bytes, filename: str) -> pd.DataFrame:
    """Parse CSV from uploaded file bytes."""
    df = pd.read_csv(io.BytesIO(file_bytes))
    return _normalize(df, filename)


def ingest_excel(file_bytes: bytes, sheet_name: Optional[str] = None) -> dict[str, pd.DataFrame]:
    """
    Parse Excel file. Returns dict of {sheet_name: DataFrame}.
    If sheet_name is provided, only that sheet is returned.
    """
    xl = pd.ExcelFile(io.BytesIO(file_bytes))
    sheets = [sheet_name] if sheet_name else xl.sheet_names
    result = {}
    for sheet in sheets:
        df = xl.parse(sheet)
        result[sheet] = _normalize(df, sheet)
    return result


def _normalize(df: pd.DataFrame, source: str) -> pd.DataFrame:
    """Clean column names and drop fully-empty rows/columns."""
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    df.dropna(how="all", inplace=True)
    df.dropna(axis=1, how="all", inplace=True)
    return df


# ─────────────────────────────────────────────
#  SQL DATABASE
# ─────────────────────────────────────────────

def get_engine(connection_string: str):
    return create_engine(connection_string)


def list_tables(connection_string: str) -> list[str]:
    engine = get_engine(connection_string)
    inspector = inspect(engine)
    return inspector.get_table_names()


def ingest_sql_table(connection_string: str, table_name: str, limit: Optional[int] = 10_000) -> pd.DataFrame:
    """Load a SQL table into a DataFrame (with optional row limit)."""
    engine = get_engine(connection_string)
    query = f"SELECT * FROM {table_name}"
    if limit:
        query += f" LIMIT {limit}"
    with engine.connect() as conn:
        df = pd.read_sql(text(query), conn)
    return _normalize(df, table_name)


def ingest_sql_query(connection_string: str, query: str) -> pd.DataFrame:
    """Execute a custom SQL query and return results as DataFrame."""
    engine = get_engine(connection_string)
    with engine.connect() as conn:
        df = pd.read_sql(text(query), conn)
    return _normalize(df, "custom_query")


# ─────────────────────────────────────────────
#  DATAFRAME SUMMARY (for embedding)
# ─────────────────────────────────────────────

def dataframe_summary(df: pd.DataFrame, name: str, max_rows: int = 5) -> str:
    """
    Create a text summary of a DataFrame for RAG embedding.
    Includes schema, statistics, and sample rows.
    """
    lines = [
        f"Dataset: {name}",
        f"Shape: {df.shape[0]} rows × {df.shape[1]} columns",
        "",
        "Columns and types:",
    ]
    for col in df.columns:
        lines.append(f"  - {col} ({df[col].dtype})")

    lines += ["", "Numeric statistics:"]
    numeric_df = df.select_dtypes(include="number")
    if not numeric_df.empty:
        desc = numeric_df.describe().round(2)
        for col in desc.columns:
            stats = desc[col]
            lines.append(
                f"  {col}: min={stats['min']}, max={stats['max']}, "
                f"mean={stats['mean']:.2f}, std={stats['std']:.2f}"
            )

    lines += ["", f"Sample rows (first {max_rows}):"]
    lines.append(df.head(max_rows).to_string(index=False))

    return "\n".join(lines)