import streamlit as st

# Must be called first, before any other Streamlit commands
st.set_page_config(page_title="Class Leaderboard", page_icon="🏁", layout="wide")

from streamlit_app.auth import signin, signup, send_password_reset
from streamlit_app.firebase import admin_emails
from streamlit_app.ui_student import student_view
from streamlit_app.ui_admin import admin_view
from streamlit_app.ui_leaderboard import leaderboard_view
from streamlit_app.ui_settings import settings_view

def normalize_email(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return ""
    return value if "@" in value else f"{value}@iqs.url.edu"

def login_box():
    tab_login, tab_signup, tab_reset = st.tabs(["Login","Register","Reset Password"])
    with tab_login:
        cols = st.columns([1, 2, 1])
        with cols[0]:
            st.write("")
        with cols[1]:
            username = st.text_input("Username", placeholder="firstname.lastname (we'll add @iqs.url.edu)", key="login_username", help="Enter your username - @iqs.url.edu will be added automatically if not present")
            email = normalize_email(username)
            if username and email:
                st.caption(f"📧 Logging in as: **{email}**")
            pw = st.text_input("Password", type="password")
            if st.button("Login", type="primary"):
                data, err = signin(email, pw)
                if err:
                    st.error(err)
                else:
                    st.session_state.user = {"email": data["email"]}
                    st.rerun()
        with cols[2]:
            st.write("")
    with tab_signup:
        cols = st.columns([1, 2, 1])
        with cols[0]:
            st.write("")
        with cols[1]:
            username = st.text_input("Username", placeholder="firstname.lastname (we'll add @iqs.url.edu)", key="su_username", help="Enter your username - @iqs.url.edu will be added automatically if not present")
            email = normalize_email(username)
            if username and email:
                st.caption(f"📧 Registering as: **{email}**")
            pw = st.text_input("Password", type="password", key="su_pw", help="Choose a strong password for your account")
        with cols[2]:
            st.write("")
        if st.button("Register", type="primary"):
            if not username:
                st.error("Please enter a username")
            elif not pw:
                st.error("Please enter a password")
            else:
                with st.spinner("Creating your account..."):
                    data, err = signup(email, pw)
                if err:
                    st.error(f"Registration failed: {err}")
                else:
                    st.success("🎉 **Account created successfully!** You can now log in with your credentials.")
                    st.balloons()
                    st.info("💡 **Next step:** Switch to the Login tab to access your account")
                    st.rerun()
    with tab_reset:
        cols = st.columns([1, 2, 1])
        with cols[0]:
            st.write("")
        with cols[1]:
            username = st.text_input("Username", placeholder="firstname.lastname (we'll add @iqs.url.edu)", key="rp_username", help="Enter your username - @iqs.url.edu will be added automatically if not present")
            email = normalize_email(username)
            if username and email:
                st.caption(f"📧 Reset link will be sent to: **{email}**")
        with cols[2]:
            st.write("")
        if st.button("Send reset link", type="primary"):
            if not username:
                st.error("Please enter a username")
            else:
                with st.spinner("Sending reset link..."):
                    ok = send_password_reset(email)
                if ok:
                    st.success("📧 **Reset link sent!** Check your email (including spam folder)")
                else:
                    st.error("Failed to send reset link. Please try again.")

def _first_query_value(value):
    if isinstance(value, list):
        return value[0] if value else ""
    return value or ""


def main():
    params = st.query_params
    view_value = _first_query_value(params.get("view"))
    user = st.session_state.get("user")
    if view_value.lower() == "leaderboard":
        role = "admin" if user and user["email"].lower() in admin_emails() else "student"
        leaderboard_view(role=role)
        st.stop()

    st.title("🏁 Class Leaderboard")
    if not user:
        login_box()
        st.stop()

    admin_list = admin_emails()
    is_admin = user["email"].lower() in admin_list
    if is_admin:
        nav_options = ["Leaderboard", "Admin Console"]
    else:
        nav_options = ["Voting", "Leaderboard", "Settings"]

    selection = st.sidebar.radio("Navigation", nav_options, key="sidebar_navigation")

    if selection == "Voting":
        student_view(user)
    elif selection == "Admin Console":
        admin_view(user)
    elif selection == "Settings":
        settings_view(user)
    else:  # Leaderboard
        role = "admin" if is_admin else "student"
        leaderboard_view(role=role)

    if st.sidebar.button("Logout"):
        st.session_state.clear(); st.rerun()

if __name__ == "__main__":
    main()
