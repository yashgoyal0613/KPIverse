"""
Page 3 — Ask Insights (RAG-powered AI Chat)
Users ask business questions; Claude answers using ChromaDB context.
"""
import streamlit as st
from core.llm import ask_with_sources
from core.embedder import list_sources, collection_stats

st.set_page_config(page_title="Ask Insights · KPIverse", layout="wide")

# Auth guard
if "user" not in st.session_state:
    st.warning("Please sign in to use AI insights.")
    st.page_link("app.py", label="→ Go to Sign In")
    st.stop()

user = st.session_state["user"]

st.markdown("# Ask Insights")
st.markdown("Ask questions about your business data in plain English. KPIverse uses your uploaded data as context.")
st.divider()

# ── Session state ──────────────────────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "rag_sources" not in st.session_state:
    st.session_state["rag_sources"] = []

# ── Sidebar controls ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Chat Settings")

    try:
        sources = list_sources()
    except Exception:
        sources = []

    source_filter = st.selectbox(
        "Filter by data source",
        ["All sources"] + sources,
        help="Limit RAG retrieval to a specific dataset",
    )
    source_filter = None if source_filter == "All sources" else source_filter

    n_chunks = st.slider("Context chunks", min_value=3, max_value=10, value=6,
                         help="More chunks = richer context but slower response")

    st.divider()
    if st.button("Clear Chat"):
        st.session_state["chat_history"] = []
        st.session_state["rag_sources"] = []
        st.rerun()

    st.divider()
    try:
        stats = collection_stats()
        st.metric("Chunks in DB", stats["total_chunks"])
        st.metric("Sources", stats["source_count"])
    except Exception:
        st.caption("ChromaDB not initialized")

# ── Guard: no data ─────────────────────────────────────────────────────────────
try:
    stats = collection_stats()
    if stats["total_chunks"] == 0:
        st.warning("No data in ChromaDB yet. Go to **Upload Data**, load a file, and click **Embed into ChromaDB**.")
        st.page_link("pages/1_Upload_Data.py", label="→ Upload Data")
        st.stop()
except Exception as e:
    st.error(f"ChromaDB error: {e}")
    st.stop()

# ── Suggested questions ────────────────────────────────────────────────────────
if not st.session_state["chat_history"]:
    st.markdown("### Try asking:")
    suggestions = [
        "What is the total revenue and how does it trend month over month?",
        "Which product/category drives the most revenue?",
        "What is our gross margin and how does it compare to industry benchmarks?",
        "Calculate our burn rate and estimate the cash runway.",
        "Are there any revenue anomalies or months where growth dropped significantly?",
        "What are the top 3 recommendations to improve profitability?",
    ]
    cols = st.columns(2)
    for i, q in enumerate(suggestions):
        with cols[i % 2]:
            if st.button(q, key=f"sug_{i}", use_container_width=True):
                st.session_state["pending_question"] = q
                st.rerun()
    st.divider()

# ── Render chat history ────────────────────────────────────────────────────────
for turn in st.session_state["chat_history"]:
    with st.chat_message(turn["role"]):
        st.markdown(turn["content"])

# ── Chat input ─────────────────────────────────────────────────────────────────
# Handle suggestion button clicks
pending = st.session_state.pop("pending_question", None)
prompt = st.chat_input("Ask anything about your business data…") or pending

if prompt:
    # Show user message
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state["chat_history"].append({"role": "user", "content": prompt})

    # Build history for context (exclude last user message, already appended)
    history_for_llm = st.session_state["chat_history"][:-1]

    # Call LLM
    with st.chat_message("assistant"):
        with st.spinner("Retrieving context and generating insight…"):
            try:
                answer, chunks = ask_with_sources(
                    prompt,
                    chat_history=history_for_llm,
                    source_filter=source_filter,
                    n_context_chunks=n_chunks,
                )
                st.markdown(answer)

                # Show citations in expander
                if chunks:
                    with st.expander(f" {len(chunks)} source chunks used", expanded=False):
                        for c in chunks:
                            st.markdown(f"**{c['source']}** — Relevance: `{c['relevance']:.0%}`")
                            st.caption(c["text"][:300] + "…" if len(c["text"]) > 300 else c["text"])
                            st.divider()

            except ValueError as e:
                answer = f" {e}"
                st.error(answer)
            except Exception as e:
                answer = f"Error: {e}"
                st.error(answer)

    st.session_state["chat_history"].append({"role": "assistant", "content": answer})