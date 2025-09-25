import streamlit as st
from google.cloud import firestore
from google.oauth2 import service_account

@st.cache_resource
def get_db():
    creds_info = st.secrets.get("gcp_service_account")
    if not creds_info:
        raise RuntimeError("Missing gcp_service_account in secrets.")
    creds = service_account.Credentials.from_service_account_info(creds_info)
    return firestore.Client(credentials=creds, project=st.secrets.get("FIREBASE_PROJECT_ID"))

def allowed_domain():
    return st.secrets.get("ALLOWED_EMAIL_DOMAIN", "@example.edu").lower()

def admin_emails():
    raw = st.secrets.get("ADMIN_EMAILS", "")
    return {e.strip().lower() for e in raw.split(",") if e.strip()}
