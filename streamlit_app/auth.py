import streamlit as st, requests

AUTH_URL = "https://identitytoolkit.googleapis.com/v1"

def _get_api_key():
    return st.secrets.get("FIREBASE_WEB_API_KEY")

def _domain_ok(email: str) -> bool:
    # Allow admin emails to bypass domain restriction
    from .firebase import admin_emails
    allowed = admin_emails()
    email_lower = email.lower().strip()
    if email_lower in allowed:
        return True
    if any(item.startswith("@") and email_lower.endswith(item) for item in allowed):
        return True

    dom = st.secrets.get("ALLOWED_EMAIL_DOMAIN", "@example.edu").lower()
    return email_lower.endswith(dom)

def signup(email: str, password: str):
    if not _domain_ok(email):
        return None, "This app is restricted to the university domain."
    url = f"{AUTH_URL}/accounts:signUp?key={_get_api_key()}"
    r = requests.post(url, json={"email": email, "password": password, "returnSecureToken": True}, timeout=10)
    if r.ok:
        return r.json(), None
    return None, r.json().get("error", {}).get("message", "Signup failed")

def signin(email: str, password: str):
    url = f"{AUTH_URL}/accounts:signInWithPassword?key={_get_api_key()}"
    r = requests.post(url, json={"email": email, "password": password, "returnSecureToken": True}, timeout=10)
    if r.ok:
        return r.json(), None
    return None, r.json().get("error", {}).get("message", "Login failed")

def send_password_reset(email: str):
    url = f"{AUTH_URL}/accounts:sendOobCode?key={_get_api_key()}"
    r = requests.post(url, json={"requestType":"PASSWORD_RESET","email":email}, timeout=10)
    return r.ok
