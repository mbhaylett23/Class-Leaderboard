"""Student settings view stub."""
from __future__ import annotations

import streamlit as st


def settings_view(user: dict | None) -> None:
    """Render a placeholder settings panel for student users."""
    st.header("Student Settings")
    st.caption("Customize your voting experience. More options coming soon!")

    st.subheader("Account")
    st.text_input("Email", value=user.get("email", "") if user else "", disabled=True)

    st.subheader("Notifications")
    st.checkbox("Email me when a new session opens", value=True)
    st.checkbox("Notify me when results are published", value=True)

    st.info("Settings are in development. Reach out to your instructor for changes that need to stick across sessions.")

