# Live Class Leaderboard — Streamlit + Firebase (Starter)

Real-time classroom leaderboard with student voting (1–5 stars across categories), teacher/peer weighting, admin console, archives.

## Quick start
```bash
pip install -r requirements.txt
cp streamlit_app/.streamlit/secrets.TEMPLATE.toml streamlit_app/.streamlit/secrets.toml
# Fill secrets.toml with Firebase Web API key + service account JSON
streamlit run streamlit_app/app.py
```

## Deploy (Streamlit Community Cloud)
- Push to GitHub; set secrets in App → Settings → Secrets (paste your TOML).

## Repo guides
- Read **AGENTS.md** for guardrails (agent-first workflow).
- Use **docs/SPRINT_NOTES.md** template per change.
- Park ideas in **docs/BACKLOG.md**.
