"""
Page 4 — My Data
Shows per-user uploaded dataset history stored in SQLite.
"""
import streamlit as st
from core.auth import get_user_datasets, delete_dataset_record
from core.embedder import delete_source, collection_stats

st.set_page_config(page_title="My Data · KPIverse", layout="wide")

# Auth guard
if "user" not in st.session_state:
    st.warning("Please sign in to view your data.")
    st.page_link("app.py", label="→ Go to Sign In")
    st.stop()

user = st.session_state["user"]

st.markdown("# My Data")
st.markdown("All datasets you have uploaded and embedded. Your data is private to your account.")
st.divider()

datasets = get_user_datasets(user["user_id"])

if not datasets:
    st.info("You haven't uploaded any datasets yet.")
    st.page_link("pages/1_Upload_Data.py", label="→ Upload Your First Dataset")
else:
    # Summary metrics
    total_rows = sum(d["row_count"] for d in datasets)
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Datasets", len(datasets))
    c2.metric("Total Rows Stored", f"{total_rows:,}")
    try:
        stats = collection_stats()
        c3.metric("ChromaDB Chunks", stats["total_chunks"])
    except Exception:
        c3.metric("ChromaDB Chunks", "—")

    st.divider()
    st.markdown("### Your Datasets")

    for ds in datasets:
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 2, 1])
            with col1:
                st.markdown(f"**{ds['name']}**")
                st.caption(f"File: `{ds['filename']}`")
            with col2:
                st.metric("Rows", f"{ds['row_count']:,}")
            with col3:
                st.metric("Cols", ds["col_count"])
            with col4:
                st.caption(f"Uploaded: {ds['uploaded_at'][:16]}")
                if ds.get("chroma_key"):
                    st.caption(f"ChromaDB: `{ds['chroma_key'][:20]}…`")
            with col5:
                if st.button("Delete", key=f"del_ds_{ds['id']}"):
                    # Delete from SQLite
                    delete_dataset_record(ds["id"], user["user_id"])
                    # Delete from ChromaDB
                    if ds.get("chroma_key"):
                        try:
                            delete_source(ds["chroma_key"])
                            delete_source(ds["chroma_key"] + "_kpis")
                        except Exception:
                            pass
                    st.success(f"Deleted `{ds['name']}`")
                    st.rerun()

            st.markdown("---")