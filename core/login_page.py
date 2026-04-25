"""
Login & Signup Page — shown when user is not authenticated.
"""
import streamlit as st
from core.auth import authenticate_user, create_user, create_session


def show_login_page():
    st.markdown("""
    <style>
      .auth-container {
        max-width: 420px;
        margin: 2rem auto;
        padding: 2.5rem;
        background: #0f1420;
        border: 1px solid #1c2a42;
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.4), 0 0 0 1px rgba(0,245,196,0.05);
        position: relative;
        overflow: hidden;
      }
      .auth-container::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, #00f5c4, #7c6aff, #ff6b6b);
      }
      .auth-logo {
        text-align: center;
        font-family: 'Syne', sans-serif;
        font-size: 2rem;
        font-weight: 800;
        background: linear-gradient(120deg, #00f5c4, #7c6aff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
      }
      .auth-subtitle {
        text-align: center;
        color: #5a6e94;
        font-size: 0.85rem;
        margin-bottom: 2rem;
      }
      .auth-divider {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin: 1.2rem 0;
        color: #5a6e94;
        font-size: 0.78rem;
      }
      .auth-divider::before, .auth-divider::after {
        content: '';
        flex: 1;
        height: 1px;
        background: #1c2a42;
      }
    </style>
    """, unsafe_allow_html=True)

    # Center the auth card
    _, center, _ = st.columns([1, 2, 1])

    with center:
        st.markdown('<div class="auth-logo">KPIverse</div>', unsafe_allow_html=True)
        st.markdown('<div class="auth-subtitle">AI-Powered Business Intelligence</div>', unsafe_allow_html=True)

        tab_login, tab_signup = st.tabs(["Sign In", "Create Account"])

        # ── LOGIN TAB ────────────────────────────────────────────────────────
        with tab_login:
            st.markdown("#### Welcome back")
            username = st.text_input("Username or Email", placeholder="Enter username or email", key="login_user")
            password = st.text_input("Password", type="password", placeholder="Enter password", key="login_pass")

            col1, col2 = st.columns([2, 1])
            with col1:
                remember = st.checkbox("Keep me signed in", value=True)

            if st.button("Sign In →", use_container_width=True, key="login_btn"):
                if not username or not password:
                    st.error("Please fill in all fields.")
                else:
                    result = authenticate_user(username, password)
                    if result["ok"]:
                        token = create_session(result["user_id"])
                        st.session_state["auth_token"] = token
                        st.session_state["user"] = result
                        st.success(f"Welcome back, {result['full_name'] or result['username']}!")
                        st.rerun()
                    else:
                        st.error(result["message"])

        # ── SIGNUP TAB ───────────────────────────────────────────────────────
        with tab_signup:
            st.markdown("#### Create your account")
            full_name = st.text_input("Full Name", placeholder="John Smith", key="signup_name")
            email = st.text_input("Email", placeholder="john@company.com", key="signup_email")
            new_username = st.text_input("Username", placeholder="johnsmith", key="signup_user")
            new_password = st.text_input("Password", type="password", placeholder="Min. 6 characters", key="signup_pass")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Repeat password", key="signup_confirm")

            if st.button("Create Account →", use_container_width=True, key="signup_btn"):
                if not all([full_name, email, new_username, new_password, confirm_password]):
                    st.error("Please fill in all fields.")
                elif new_password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    result = create_user(new_username, email, new_password, full_name)
                    if result["ok"]:
                        st.success("Account created! Please sign in.")
                    else:
                        st.error(result["message"])