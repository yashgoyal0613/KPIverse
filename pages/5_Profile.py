"""
Page 5 — Profile & Settings
User profile info, password change, account stats.
"""
import streamlit as st
from core.auth import get_user_by_id, change_password, get_user_datasets

st.set_page_config(page_title="Profile · KPIverse", layout="wide")

# Auth guard
if "user" not in st.session_state:
    st.warning("Please sign in to view your profile.")
    st.page_link("app.py", label="→ Go to Sign In")
    st.stop()

user = st.session_state["user"]
user_data = get_user_by_id(user["user_id"])

st.markdown("# Profile & Settings")
st.divider()

left, right = st.columns([2, 1])

with left:
    # ── Profile Info ──────────────────────────────────────────────────────────
    st.markdown("### Account Info")
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            st.text_input("Full Name", value=user_data.get("full_name", ""), disabled=True)
            st.text_input("Username", value=user_data.get("username", ""), disabled=True)
        with c2:
            st.text_input("Email", value=user_data.get("email", ""), disabled=True)
            st.text_input("Role", value=user_data.get("role", "user").capitalize(), disabled=True)

        st.caption(f"Account created: {user_data.get('created_at', '—')[:16]}")
        st.caption(f"Last login: {user_data.get('last_login', '—')[:16] if user_data.get('last_login') else 'First session'}")

    st.divider()

    # ── Change Password ───────────────────────────────────────────────────────
    st.markdown("### Change Password")
    old_pw = st.text_input("Current Password", type="password", key="old_pw")
    new_pw = st.text_input("New Password", type="password", key="new_pw", placeholder="Min. 6 characters")
    confirm_pw = st.text_input("Confirm New Password", type="password", key="confirm_pw")

    if st.button("Update Password", key="change_pw_btn"):
        if not old_pw or not new_pw or not confirm_pw:
            st.error("Please fill in all password fields.")
        elif new_pw != confirm_pw:
            st.error("New passwords do not match.")
        else:
            result = change_password(user["user_id"], old_pw, new_pw)
            if result["ok"]:
                st.success(result["message"])
            else:
                st.error(result["message"])

with right:
    # ── Account Stats ─────────────────────────────────────────────────────────
    st.markdown("### Your Stats")
    datasets = get_user_datasets(user["user_id"])
    total_rows = sum(d["row_count"] for d in datasets)

    st.metric("Datasets Uploaded", len(datasets))
    st.metric("Total Rows Stored", f"{total_rows:,}")

    st.divider()
    st.markdown("### Session Info")
    st.caption(f"Logged in as: `{user['username']}`")
    token = st.session_state.get("auth_token", "")
    st.caption(f"Session token: `{token[:12]}…`" if token else "No token found")

    st.divider()
    st.markdown("### Quick Links")
    st.page_link("pages/1_Upload_Data.py", label="→ Upload Data")
    st.page_link("pages/4_My_Data.py", label="→ My Datasets")
    st.page_link("pages/3_Ask_Insights.py", label="→ Ask AI")