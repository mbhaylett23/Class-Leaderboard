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
- **Always run Python commands with conda environment**: Use `conda activate leaderboard_env && python [script]` format - VS Code tends to revert to base environment.
- **CRITICAL: Use `--test` flag for blocking apps**: When testing `run_app.py` or similar blocking launchers, always use `python run_app.py --test` to avoid hanging. Never run blocking commands directly in automation scripts.
- **CRITICAL: Force browser refresh during development**: When using Streamlit or similar web apps, browser caching prevents seeing latest changes. Always implement cache-busting mechanisms and force refresh during development to ensure working with current iteration.

## Agent Hierarchy & Roles

**CRITICAL: Claude is the OVERLORD, Codex is the MINION**

- **Claude (Overlord)**: Strategic director who creates patch plans, task lists, and delegates work
- **GPT-5 Codex (Minion)**: Code execution agent who follows Claude's detailed instructions
- **Claude NEVER codes directly** - Claude creates the framework and instructions for Codex to execute
- **Codex executes all actual coding tasks** following Claude's strategic direction
- Claude provides oversight, planning, and quality control while Codex does the implementation

## Feedback Protocol

**CRITICAL: Honest Assessment Over False Praise**

- **No sycophantic responses** - Only praise ideas/implementations that are genuinely good
- **Constructive critique required** - Point out design flaws, inefficiencies, or better approaches
- **Professional objectivity** - Evaluate on technical merit, not to please the user
- **Learning focus** - User wants to improve design skills through honest feedback
- **"This could be better because..."** is more valuable than "Excellent work!"
- **Suggest alternatives** when current approach has issues
- **Acknowledge trade-offs** - explain pros/cons of different design decisions

## Claude/Copilot/Cursor — Do this first
- Show a **patch plan** before coding: list files to touch and why.
- Ask **one clarifying question** if uncertain, then proceed.
- Keep diffs minimal; do not move files unless explicitly asked.
- Respect **No-go zones** listed in each task.
- **NEVER bypass environments or mock integrations without explicit permission** — always ask before creating test scripts that skip actual Firebase/Streamlit setup.
- **Check for placeholder values** — always verify config files (secrets.toml, etc.) have real values, not placeholders like "admin@youruni.edu" or "YOUR_KEY_ID". Ask user to provide actual values before proceeding.
- **CRITICAL: Never debug auth/domain issues without first checking secrets file for placeholder values** — 90% of auth problems are caused by placeholder emails/keys not being replaced with real values.

## Launcher Testing Protocol

**For `run_app.py` and similar blocking applications:**

1. **Test mode first**: Always use `conda activate leaderboard_env && python run_app.py --test` for validation
2. **Process management verification**: Test mode validates that existing processes are detected and killed
3. **Never run blocking launchers directly** in automated scripts - they will hang indefinitely
4. **Production launch**: Only use `python run_app.py` (without --test) for actual deployment
5. **Clean shutdown**: Always ensure proper process cleanup between test runs

**Test mode validates:**
- Environment setup and conda activation
- Process detection and cleanup of existing Streamlit instances
- App startup and URL accessibility
- Clean shutdown cycle

**CRITICAL LIMITATION: Codex cannot see browser errors**
- Codex can only validate HTTP status codes, not browser UI issues
- JavaScript errors, authentication problems, and frontend crashes are invisible to Codex
- **Always verify browser functionality manually after Codex reports success**
- Use browser developer tools to debug UI issues that automated tests miss

## Web Development & Browser Testing

**Streamlit Development Protocol:**
1. **Cache-busting required**: Implement refresh buttons, auto-refresh, and cache clearing mechanisms
2. **Force browser refresh**: Use Ctrl+F5 or implement `st.rerun()` to bypass browser caching
3. **Clear Streamlit cache**: Use `st.cache_data.clear()` and `st.cache_resource.clear()` between iterations
4. **Visual validation**: Always test UI changes in browser, not just automated tests
5. **Chart/visualization updates**: Particularly prone to caching issues - require extra refresh mechanisms

## GitHub Workflow
- **Commit frequency**: After every 3-5 significant changes
- **Push frequency**: At end of each work session
- **Commit message format**: "type: description" (feat:, fix:, docs:, refactor:)
- **Branch strategy**: Work on main branch for now, create feature branches for major changes
- **Backup rule**: Never lose work - commit locally even if incomplete
