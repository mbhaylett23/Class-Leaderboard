# AGENTS.md — Project Guardrails (Read me first)

**Project:** Class Leaderboard with live voting, teacher/peer weighting, admin console, archives.  
**Stack:** Streamlit UI, Firebase Auth (email/password), Firestore DB.

## Principles
1) Thin-slice work: one narrow outcome per task.
2) UI-first then logic: build layouts/hierarchy with placeholders before wiring data.
3) Minimal diffs: touch the smallest file set needed; keep changes under ~60 LOC where possible.
4) Modularity & file hygiene: UI in `ui_*.py`, logic in `data.py`, Firestore client in `firebase.py`, models in `models.py`.
5) Tests as contract: update/add tests in `tests/` matching acceptance criteria.
6) Durable, short context: every task starts with the template in `docs/SPRINT_NOTES.md`.
7) No scope creep: new ideas go into `docs/BACKLOG.md`.
8) **User feedback is key**: Always provide clear visual feedback for user actions (success/error messages, loading states, confirmation dialogs). Users should never wonder if their action worked.

## Directory rules
```
streamlit_app/
  app.py                # routing + auth + view switch
  ui_student.py         # student UI
  ui_admin.py           # admin UI
  data.py               # Firestore CRUD + aggregations (pure funcs)
  firebase.py           # Firestore client (service account from secrets)
  models.py             # Pydantic models
  .streamlit/
    secrets.TEMPLATE.toml
docs/
  SPRINT_NOTES.md
  BACKLOG.md
  WIREFRAMES/
tests/
  test_scoring.py
  test_rules.py
README.md
requirements.txt
```

## Coding conventions
- Python 3.11+, Streamlit 1.36+.
- Keep functions ≤50 LOC when possible; prefer pure functions for scoring.
- Secrets only via `st.secrets` (cloud) or `.env` (local). Never hardcode.
- Prefer conda environments; attempt `conda` setup before falling back to `pip` installs.
- **Always run Python commands with conda environment**: Use `conda activate [env] && python [script]` format - VS Code tends to revert to base environment.

## Agent Hierarchy & Roles

**CRITICAL: Claude is the OVERLORD, Codex is the MINION**

- **Claude (Overlord)**: Strategic director who creates patch plans, task lists, and delegates work
- **GPT-5 Codex (Minion)**: Code execution agent who follows Claude's detailed instructions
- **Claude NEVER codes directly** - Claude creates the framework and instructions for Codex to execute
- **Codex executes all actual coding tasks** following Claude's strategic direction
- Claude provides oversight, planning, and quality control while Codex does the implementation

## Claude/Copilot/Cursor — Do this first
- Show a **patch plan** before coding: list files to touch and why.
- Ask **one clarifying question** if uncertain, then proceed.
- Keep diffs minimal; do not move files unless explicitly asked.
- Respect **No-go zones** listed in each task.
- **NEVER bypass environments or mock integrations without explicit permission** — always ask before creating test scripts that skip actual Firebase/Streamlit setup.
- **Check for placeholder values** — always verify config files (secrets.toml, etc.) have real values, not placeholders like "admin@youruni.edu" or "YOUR_KEY_ID". Ask user to provide actual values before proceeding.
- **CRITICAL: Never debug auth/domain issues without first checking secrets file for placeholder values** — 90% of auth problems are caused by placeholder emails/keys not being replaced with real values.

## GitHub Workflow
- **Commit frequency**: After every 3-5 significant changes
- **Push frequency**: At end of each work session
- **Commit message format**: "type: description" (feat:, fix:, docs:, refactor:)
- **Branch strategy**: Work on main branch for now, create feature branches for major changes
- **Backup rule**: Never lose work - commit locally even if incomplete
