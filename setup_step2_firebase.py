import json, pathlib, sys

PATH = pathlib.Path("streamlit_app/.streamlit/secrets.toml")
print("Firebase Setup Guide:\n1. https://console.firebase.google.com/ (create project)\n2. Enable Auth > Email/Password\n3. Create Firestore (production)\n4. Add Web App for API key\n5. Project Settings > Service Accounts > Generate key")
pid = input("Firebase project ID: ").strip()
api_key = input("Firebase Web API key: ").strip()
domain = input("Allowed email domain [@youruni.edu]: ").strip() or "@youruni.edu"
admins = input("Admin emails (comma separated) [admin@youruni.edu]: ").strip() or "admin@youruni.edu"
svc_path = input("Path to service account JSON (blank to keep placeholders): ").strip()
if not pid or not api_key:
    print("❌ Project ID and Web API key required."); sys.exit(1)
block = dict(
    type="service_account",
    project_id=pid,
    private_key_id="YOUR_KEY_ID",
    private_key="-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----\\n",
    client_email=f"service-account@{pid}.iam.gserviceaccount.com",
    client_id="",
    auth_uri="https://accounts.google.com/o/oauth2/auth",
    token_uri="https://oauth2.googleapis.com/token",
    auth_provider_x509_cert_url="https://www.googleapis.com/oauth2/v1/certs",
    client_x509_cert_url=f"https://www.googleapis.com/robot/v1/metadata/x509/service-account%40{pid}.iam.gserviceaccount.com",
)
if svc_path:
    try:
        loaded = json.load(open(svc_path))
        missing = {"type", "project_id", "private_key", "client_email"} - set(loaded)
        if missing:
            print("❌ Service account JSON missing:", ", ".join(sorted(missing))); sys.exit(2)
        for key in block:
            block[key] = str(loaded.get(key, block[key]))
        block["private_key"] = block["private_key"].replace("\n", "\\n")
    except (OSError, json.JSONDecodeError) as err:
        print(f"❌ Could not read service account JSON: {err}"); sys.exit(2)
PATH.parent.mkdir(parents=True, exist_ok=True)
lines = [
    f'ALLOWED_EMAIL_DOMAIN = "{domain}"',
    f'ADMIN_EMAILS = "{admins}"',
    f'FIREBASE_PROJECT_ID = "{pid}"',
    f'FIREBASE_WEB_API_KEY = "{api_key}"',
    f'FIREBASE_AUTH_DOMAIN = "{pid}.firebaseapp.com"',
    'FIREBASE_APP_ID = ""',
    '',
    '[gcp_service_account]',
    *[f"{k} = \"{v}\"" for k, v in block.items()],
]
PATH.write_text("\n".join(lines) + "\n")
print(f"✅ Firebase secrets saved to {PATH}. Next: streamlit run streamlit_app/app.py")
