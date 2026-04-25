"""
KPIverse — Main Entry Point with Auth
Run with: streamlit run app.py
"""
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="KPIverse",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&family=DM+Mono:wght@400;500&display=swap');

  :root {
    --bg:        #07090f;
    --surface:   #0f1420;
    --surface2:  #161d2e;
    --border:    #1c2a42;
    --accent1:   #00f5c4;
    --accent2:   #7c6aff;
    --accent3:   #ff6b6b;
    --accent4:   #ffd166;
    --text:      #dce8ff;
    --muted:     #5a6e94;
  }

  *, *::before, *::after { box-sizing: border-box; }

  html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
  }

  .stApp {
    background:
      radial-gradient(ellipse 70% 50% at 5% 15%,  rgba(0,245,196,0.07) 0%, transparent 55%),
      radial-gradient(ellipse 50% 40% at 95% 85%,  rgba(124,106,255,0.09) 0%, transparent 55%),
      radial-gradient(ellipse 40% 30% at 50% 50%,  rgba(255,107,107,0.04) 0%, transparent 60%),
      var(--bg) !important;
    min-height: 100vh;
  }

  [data-testid="stSidebar"] {
    background: linear-gradient(160deg, #0d1526 0%, #08090f 100%) !important;
    border-right: 1px solid var(--border) !important;
    position: relative;
  }
  [data-testid="stSidebar"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--accent1), var(--accent2), var(--accent3));
    z-index: 10;
  }

  h1, h2, h3, h4 {
    font-family: 'Syne', sans-serif !important;
    font-weight: 800 !important;
    letter-spacing: -0.02em !important;
  }
  h1 {
    font-size: 2.4rem !important;
    background: linear-gradient(120deg, var(--accent1) 0%, #5ee7d0 40%, var(--accent2) 100%);
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    margin-bottom: 0.1rem !important;
  }
  h2 { color: var(--text) !important; font-size: 1.4rem !important; }
  h3 {
    color: var(--accent1) !important;
    font-size: 0.78rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    font-weight: 600 !important;
  }

  [data-testid="metric-container"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    padding: 1.3rem 1.2rem !important;
    position: relative !important;
    overflow: hidden !important;
    transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease !important;
  }
  [data-testid="metric-container"]:hover {
    transform: translateY(-3px) !important;
    border-color: rgba(0,245,196,0.5) !important;
    box-shadow: 0 8px 30px rgba(0,245,196,0.1) !important;
  }
  [data-testid="metric-container"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent1), var(--accent2));
  }
  [data-testid="stMetricValue"] {
    font-family: 'DM Mono', monospace !important;
    font-size: 1.9rem !important;
    font-weight: 500 !important;
    color: var(--accent1) !important;
    line-height: 1.1 !important;
  }
  [data-testid="stMetricLabel"] {
    font-size: 0.72rem !important;
    color: var(--muted) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
  }
  [data-testid="stMetricDelta"] {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.78rem !important;
  }

  .stButton > button {
    background: linear-gradient(135deg, var(--accent1) 0%, #3dd9b3 50%, var(--accent2) 100%) !important;
    color: #05080f !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.02em !important;
    padding: 0.58rem 1.5rem !important;
    transition: all 0.25s ease !important;
    box-shadow: 0 2px 20px rgba(0,245,196,0.25) !important;
    cursor: pointer !important;
  }
  .stButton > button:hover {
    transform: translateY(-2px) scale(1.02) !important;
    box-shadow: 0 6px 28px rgba(0,245,196,0.45) !important;
  }
  .stButton > button:active { transform: translateY(0) scale(0.99) !important; }

  .logout-btn > button {
    background: linear-gradient(135deg, #ff6b6b, #cc3333) !important;
    box-shadow: 0 2px 20px rgba(255,107,107,0.25) !important;
  }
  .logout-btn > button:hover {
    box-shadow: 0 6px 28px rgba(255,107,107,0.45) !important;
  }

  .stTabs [data-baseweb="tab-list"] {
    background: var(--surface) !important;
    border-radius: 12px !important;
    padding: 5px !important;
    gap: 4px !important;
    border: 1px solid var(--border) !important;
  }
  .stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--muted) !important;
    border-radius: 9px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.88rem !important;
    padding: 0.4rem 1rem !important;
    transition: all 0.2s !important;
    border: 1px solid transparent !important;
  }
  .stTabs [data-baseweb="tab"]:hover { color: var(--text) !important; background: var(--surface2) !important; }
  .stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, rgba(0,245,196,0.12), rgba(124,106,255,0.12)) !important;
    color: var(--accent1) !important;
    border: 1px solid rgba(0,245,196,0.25) !important;
  }

  .stTextInput > div > div > input,
  .stTextArea textarea {
    background: var(--surface) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
  }
  .stTextInput > div > div > input:focus,
  .stTextArea textarea:focus {
    border-color: var(--accent1) !important;
    box-shadow: 0 0 0 3px rgba(0,245,196,0.08) !important;
    outline: none !important;
  }

  [data-testid="stFileUploadDropzone"] {
    background: var(--surface) !important;
    border: 2px dashed var(--border) !important;
    border-radius: 14px !important;
    transition: all 0.25s !important;
  }
  [data-testid="stFileUploadDropzone"]:hover {
    border-color: var(--accent1) !important;
    background: rgba(0,245,196,0.03) !important;
    box-shadow: 0 0 0 4px rgba(0,245,196,0.05) !important;
  }

  [data-testid="stChatMessage"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    margin-bottom: 0.6rem !important;
    transition: border-color 0.2s !important;
  }
  [data-testid="stChatMessage"]:last-child {
    border-color: rgba(124,106,255,0.3) !important;
    box-shadow: 0 4px 20px rgba(124,106,255,0.06) !important;
  }

  [data-testid="stChatInput"] textarea {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
    transition: all 0.2s !important;
  }
  [data-testid="stChatInput"] textarea:focus {
    border-color: var(--accent1) !important;
    box-shadow: 0 0 0 3px rgba(0,245,196,0.08) !important;
  }

  .streamlit-expanderHeader {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.88rem !important;
    color: var(--muted) !important;
    transition: all 0.2s !important;
    padding: 0.7rem 1rem !important;
  }
  .streamlit-expanderHeader:hover {
    border-color: rgba(124,106,255,0.4) !important;
    color: var(--text) !important;
  }

  .stSelectbox [data-baseweb="select"] > div {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    transition: border-color 0.2s !important;
  }
  .stSelectbox [data-baseweb="select"] > div:hover { border-color: var(--accent2) !important; }

  [data-testid="stAlert"] {
    border-radius: 12px !important;
    border-left: 3px solid !important;
    font-family: 'DM Sans', sans-serif !important;
  }

  [data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    overflow: hidden !important;
  }

  code {
    font-family: 'DM Mono', monospace !important;
    color: var(--accent1) !important;
    background: rgba(0,245,196,0.07) !important;
    padding: 0.12em 0.45em !important;
    border-radius: 5px !important;
    font-size: 0.88em !important;
  }

  hr { border-color: var(--border) !important; margin: 1rem 0 !important; }

  [data-testid="stNumberInput"] input {
    background: var(--surface) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
  }

  [data-testid="stPageLink"] a {
    color: var(--accent1) !important;
    font-weight: 500 !important;
    text-decoration: none !important;
    transition: color 0.2s !important;
  }
  [data-testid="stPageLink"] a:hover { color: var(--accent2) !important; }

  .stCaption, [data-testid="stCaptionContainer"] {
    color: var(--muted) !important;
    font-size: 0.78rem !important;
  }

  .user-badge {
    background: linear-gradient(135deg, rgba(0,245,196,0.08), rgba(124,106,255,0.08));
    border: 1px solid rgba(0,245,196,0.2);
    border-radius: 12px;
    padding: 0.8rem 1rem;
    margin-bottom: 0.5rem;
  }
  .user-badge .name {
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 0.95rem;
    color: #dce8ff;
  }
  .user-badge .role {
    font-size: 0.72rem;
    color: #00f5c4;
    text-transform: uppercase;
    letter-spacing: 0.08em;
  }

  ::-webkit-scrollbar { width: 5px; height: 5px; }
  ::-webkit-scrollbar-track { background: var(--bg); }
  ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
  ::-webkit-scrollbar-thumb:hover { background: var(--accent2); }
</style>
""", unsafe_allow_html=True)


# ── Auth Check ─────────────────────────────────────────────────────────────────
from core.auth import validate_session, delete_session, cleanup_expired_sessions
from core.login_page import show_login_page

cleanup_expired_sessions()

if "user" not in st.session_state:
    token = st.session_state.get("auth_token")
    if token:
        user = validate_session(token)
        if user:
            st.session_state["user"] = user
        else:
            st.session_state.pop("auth_token", None)

if "user" not in st.session_state:
    show_login_page()
    st.stop()

user = st.session_state["user"]

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## KPIverse")
    st.markdown("*AI-Powered Business Intelligence*")
    st.divider()

    # User badge
    st.markdown(f"""
    <div class="user-badge">
      <div class="name"> {user.get('full_name') or user['username']}</div>
      <div style="font-size:0.78rem; color:#5a6e94; margin-top:2px;">@{user['username']}</div>
      <div class="role">● {user.get('role','user')}</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        api_key = st.text_input("Groq API Key", type="password", placeholder="gsk_...")
        if api_key:
            os.environ["GROQ_API_KEY"] = api_key
            st.success("API key set ✓")
    else:
        st.success("✓ API key loaded from .env")

    st.divider()
    st.markdown("**Navigation**")
    st.page_link("app.py", label="Home")
    st.page_link("pages/1_Upload_Data.py", label="Upload Data")
    st.page_link("pages/2_KPI_Dashboard.py", label="KPI Dashboard")
    st.page_link("pages/3_Ask_Insights.py", label="Ask Insights (AI)")
    st.page_link("pages/4_My_Data.py", label="My Data")
    st.page_link("pages/5_Profile.py", label="Profile & Settings")

    st.divider()

    st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
    if st.button("Sign Out", use_container_width=True):
        token = st.session_state.pop("auth_token", None)
        if token:
            delete_session(token)
        st.session_state.pop("user", None)
        st.session_state.pop("loaded_dfs", None)
        st.session_state.pop("chat_history", None)
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    st.caption("Built with Streamlit · ChromaDB · Groq")
    


# ── Home Page ─────────────────────────────────────────────────────────────────
st.markdown("# KPIverse")
st.markdown(f"##### Welcome back, **{user.get('full_name') or user['username']}**")
st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### Step 1")
    st.markdown("**Upload Your Data**")
    st.markdown("Upload CSV/Excel files or connect to a SQL database. Your data is chunked and embedded into a local ChromaDB vector store.")
    st.page_link("pages/1_Upload_Data.py", label="→ Upload Data")

with col2:
    st.markdown("### Step 2")
    st.markdown("**Explore KPI Dashboard**")
    st.markdown("Auto-computed Sales & Finance KPIs with interactive Plotly charts — revenue trends, margins, burn rate, and more.")
    st.page_link("pages/2_KPI_Dashboard.py", label="→ View Dashboard")

with col3:
    st.markdown("### Step 3")
    st.markdown("**Ask AI Insights**")
    st.markdown("Chat with AI using RAG. Ask questions in plain English — the AI retrieves relevant data and answers with grounded insights.")
    st.page_link("pages/3_Ask_Insights.py", label="→ Ask Insights")

st.divider()
st.markdown("### Supported KPIs")
tab1, tab2 = st.tabs(["Sales & Revenue", "Finance & Accounting"])

with tab1:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        - Total Revenue & MoM/YoY Growth
        - Average Deal / Transaction Size
        - Win Rate & Pipeline Value
        - Monthly Recurring Revenue (MRR)
        """)
    with c2:
        st.markdown("""
        - Customer Lifetime Value (LTV)
        - Churn Rate
        - Revenue per Sales Rep
        - Revenue by Category / Segment
        """)

with tab2:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        - Gross Margin & Net Profit Margin
        - EBITDA
        - Burn Rate & Cash Runway
        - Current Ratio
        """)
    with c2:
        st.markdown("""
        - Accounts Receivable / Payable Days
        - Operating Cash Flow
        - Return on Equity (ROE)
        - Revenue vs Expense Comparison
        """)