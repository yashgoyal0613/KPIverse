"""
Page 1 — Upload & Ingest Data (with per-user data storage)
"""
import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

from core.ingestor import (
    ingest_csv, ingest_excel, ingest_sql_table,
    ingest_sql_query, list_tables, dataframe_summary,
)
from core.embedder import embed_text, collection_stats, delete_source, list_sources
from core.auth import save_dataset_record, get_user_datasets
from utils.kpi_calculator import auto_compute_kpis, kpis_to_text

st.set_page_config(page_title="Upload Data · KPIverse", layout="wide")

# Auth guard
if "user" not in st.session_state:
    st.warning("Please sign in to upload data.")
    st.page_link("app.py", label="→ Go to Sign In")
    st.stop()

user = st.session_state["user"]

st.markdown("# Upload Data")
st.markdown("Ingest CSV/Excel files or connect to a SQL database. Data is embedded into ChromaDB for RAG-powered insights.")
st.divider()

if "loaded_dfs" not in st.session_state:
    st.session_state["loaded_dfs"] = {}

left, right = st.columns([3, 2])

with left:
    tab_file, tab_sql = st.tabs(["CSV / Excel Upload", "SQL Database"])

    with tab_file:
        uploaded = st.file_uploader(
            "Drop CSV or Excel files here",
            type=["csv", "xlsx", "xls"],
            accept_multiple_files=True,
        )

        if uploaded:
            for file in uploaded:
                file_bytes = file.read()
                fname = file.name.lower()

                if fname.endswith(".csv"):
                    df = ingest_csv(file_bytes, file.name)
                    dfs = {file.name: df}
                else:
                    dfs = ingest_excel(file_bytes)

                for sheet_name, df in dfs.items():
                    display_key = f"{file.name} › {sheet_name}" if len(dfs) > 1 else file.name
                    st.session_state["loaded_dfs"][display_key] = df

                    with st.expander(f"{display_key}  ({df.shape[0]:,} rows × {df.shape[1]} cols)", expanded=True):
                        st.dataframe(df.head(10), use_container_width=True)

                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button(f"Embed into ChromaDB", key=f"embed_{display_key}"):
                                with st.spinner("Embedding…"):
                                    # Unique chroma key per user
                                    chroma_key = f"u{user['user_id']}_{display_key}"

                                    summary = dataframe_summary(df, chroma_key)
                                    n1 = embed_text(summary, chroma_key, metadata={
                                        "type": "summary", "user_id": str(user["user_id"])
                                    })

                                    kpis = auto_compute_kpis(df)
                                    n2 = 0
                                    if kpis:
                                        kpi_text = kpis_to_text(kpis, chroma_key)
                                        n2 = embed_text(kpi_text, chroma_key + "_kpis", metadata={
                                            "type": "kpis", "user_id": str(user["user_id"])
                                        })

                                    # Save record to SQLite
                                    save_dataset_record(
                                        user_id=user["user_id"],
                                        name=display_key,
                                        filename=file.name,
                                        row_count=df.shape[0],
                                        col_count=df.shape[1],
                                        chroma_key=chroma_key,
                                    )

                                st.success(f"Embedded {n1 + n2} chunks ✓  —  saved to your account")

                        with col_b:
                            if st.button(f"Load to Session", key=f"session_{display_key}"):
                                st.success("Added to dashboard session ✓")

    with tab_sql:
        st.markdown("**Connection String**")
        default_conn = os.getenv("DATABASE_URL", "sqlite:///./data/business.db")
        conn_str = st.text_input("Connection string", value=default_conn, label_visibility="collapsed")

        if st.button("Connect & List Tables"):
            try:
                tables = list_tables(conn_str)
                st.session_state["sql_tables"] = tables
                st.session_state["sql_conn"] = conn_str
                st.success(f"Connected — {len(tables)} tables found")
            except Exception as e:
                st.error(f"Connection failed: {e}")

        if "sql_tables" in st.session_state:
            selected_table = st.selectbox("Table", st.session_state["sql_tables"])
            row_limit = st.number_input("Row limit", min_value=100, max_value=100_000, value=5_000, step=500)

            if st.button("Load Table"):
                with st.spinner(f"Loading {selected_table}…"):
                    df = ingest_sql_table(st.session_state["sql_conn"], selected_table, limit=row_limit)
                    st.session_state["loaded_dfs"][selected_table] = df
                    st.dataframe(df.head(10), use_container_width=True)
                    st.success(f"Loaded {df.shape[0]:,} rows")

            st.divider()
            st.markdown("**Or run custom SQL:**")
            custom_sql = st.text_area("SQL Query", value="SELECT * FROM sales LIMIT 1000", height=100)
            if st.button("Run Query"):
                try:
                    df = ingest_sql_query(st.session_state["sql_conn"], custom_sql)
                    st.session_state["loaded_dfs"]["custom_query"] = df
                    st.dataframe(df.head(10), use_container_width=True)
                    st.success(f"Query returned {df.shape[0]:,} rows")
                except Exception as e:
                    st.error(f"Query failed: {e}")

with right:
    st.markdown("### ChromaDB Status")
    try:
        stats = collection_stats()
        st.metric("Total Chunks", f"{stats['total_chunks']:,}")
        st.metric("Data Sources", stats["source_count"])

        if stats["sources"]:
            st.markdown("**Your Stored Sources:**")
            user_prefix = f"u{user['user_id']}_"
            user_sources = [s for s in stats["sources"] if s.startswith(user_prefix)]
            other_sources = [s for s in stats["sources"] if not s.startswith(user_prefix)]

            for src in user_sources:
                col_s, col_d = st.columns([4, 1])
                with col_s:
                    st.markdown(f"• `{src.replace(user_prefix, '')}`")
                with col_d:
                    if st.button("🗑", key=f"del_{src}"):
                        delete_source(src)
                        delete_source(src + "_kpis")
                        st.warning(f"Deleted")
                        st.rerun()

            if not user_sources:
                st.info("No data embedded yet.")
        else:
            st.info("No data embedded yet.")

    except Exception as e:
        st.error(f"ChromaDB error: {e}")

    st.divider()
    st.markdown("### Your Saved Datasets")
    datasets = get_user_datasets(user["user_id"])
    if datasets:
        for ds in datasets[:5]:
            st.markdown(f"**{ds['name']}** — {ds['row_count']:,} rows")
            st.caption(ds["uploaded_at"][:16])
        if len(datasets) > 5:
            st.page_link("pages/4_My_Data.py", label=f"→ View all {len(datasets)} datasets")
    else:
        st.caption("No datasets saved yet.")

    st.divider()
    st.markdown("### Session DataFrames")
    if st.session_state["loaded_dfs"]:
        for name, df in st.session_state["loaded_dfs"].items():
            st.markdown(f"**{name}** — {df.shape[0]:,} rows")
    else:
        st.caption("No data loaded in session yet.")