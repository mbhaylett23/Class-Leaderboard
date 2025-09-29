# Class Leaderboard - Project Roadmap & Status

**Last Updated**: 2025-09-27
**Current Phase**: Web App Completion & Testing

## Project Overview
Live classroom leaderboard with student voting (1–5 stars), teacher/peer weighting, admin console, real-time projection display.

**Stack**: Streamlit UI + Firebase Auth + Firestore DB
**Domain**: @iqs.url.edu email addresses
**Target Users**: Students, Teachers, Admin

---

## Current Implementation Status ✅

### ✅ COMPLETED FEATURES
- **Authentication System**: Firebase email/password with domain normalization
- **Core Voting**: Students rate teams 1-5 across custom categories
- **Score Aggregation**: Teacher/peer weighted scoring with configurable percentages
- **Admin Console**: Session management, voting oversight
- **Real-time Leaderboard**: Auto-refreshing fullscreen view for projection
- **Multi-class Support**: Separate leaderboards per class
- **Clean Launcher**: `run_app.py` with process management and conda environment detection
- **Test Coverage**: Comprehensive pytest suite for leaderboard functionality

### ✅ RECENT IMPLEMENTATIONS (2025-09-27)
- **Process Management**: Clean Streamlit startup with existing process termination
- **Environment Detection**: Conda environment auto-detection with pip fallback
- **Production Ready**: Self-contained launcher perfect for permanent hosting
- **Leaderboard Window**: Dedicated fullscreen view with query parameter handling
- **Dependency Management**: psutil added to requirements.txt

### 🔄 CURRENT FOCUS
- **Testing Phase**: Validate all components in leaderboard_env
- **Deployment Planning**: Streamlit Community Cloud preparation

---

## Phase Roadmap

### 📍 PHASE 1: Web App Perfection (CURRENT)
**Goal**: Production-ready web application
**Timeline**: Current - 1 week

**Remaining Tasks**:
- [ ] Complete testing in leaderboard_env
- [ ] Validate launcher functionality
- [ ] Deploy to Streamlit Community Cloud
- [ ] User acceptance testing with real classroom

**Success Criteria**:
- All tests pass consistently
- Clean startup/shutdown cycle
- Stable multi-user concurrent access
- Reliable real-time updates

### 📱 PHASE 2: Mobile-Friendly Enhancement (NEXT)
**Goal**: Progressive Web App capabilities
**Timeline**: 2-4 weeks after Phase 1

**Features**:
- [ ] PWA manifest for "installable" web app
- [ ] Mobile-optimized voting interface
- [ ] Touch-friendly leaderboard controls
- [ ] Offline capability for poor connectivity
- [ ] Push notifications for voting periods

**Success Criteria**:
- App installable from mobile browsers
- Native-like mobile experience
- Works on iOS and Android devices
- Handles network interruptions gracefully

### 🚀 PHASE 3: Native Mobile App (FUTURE)
**Goal**: True native mobile application
**Timeline**: 2-3 months (if justified by usage)

**Technology**: React Native + Expo (recommended)
**Features**:
- [ ] Native iOS/Android apps
- [ ] App Store distribution
- [ ] Enhanced mobile UI/UX
- [ ] Advanced offline capabilities
- [ ] Mobile-specific features (camera voting, etc.)

**Decision Point**: Proceed only if web/PWA usage demonstrates need

---

## Deployment Strategy

### Option 1: Streamlit Community Cloud ⭐ RECOMMENDED
**Why**: Free, professional, zero-maintenance
- **URL**: https://class-leaderboard-yourname.streamlit.app
- **Cost**: $0 for educational use
- **Setup**: GitHub repo + secrets upload
- **Benefits**: Auto-scaling, HTTPS, global CDN

### Option 2: Local Network Hosting
**Why**: Complete control, classroom-only access
- **Modify**: `run_app.py` to bind 0.0.0.0:8501
- **Access**: http://YOUR_IP:8501
- **Requirements**: Network configuration

### Option 3: Tunnel Services (Testing)
**Why**: Quick public access for testing
- **ngrok**: `ngrok http 8501`
- **Cloudflare Tunnel**: Free alternative

---

## Technical Architecture

### File Structure
```
streamlit_app/
  app.py                # Main routing + auth + view switching
  ui_student.py         # Student voting interface
  ui_admin.py          # Admin session management
  ui_leaderboard.py    # Fullscreen projection display
  data.py              # Firestore CRUD + score aggregation
  firebase.py          # Firestore client setup
  models.py            # Pydantic data models
  auth.py              # Firebase authentication

tests/
  test_scoring.py      # Score calculation tests
  test_rules.py        # Business logic tests
  test_leaderboard_window.py  # Leaderboard functionality tests

run_app.py             # Production launcher with process management
requirements.txt       # All dependencies including psutil
```

### Key URLs
- **Main App**: `http://localhost:8501`
- **Leaderboard View**: `http://localhost:8501/?view=leaderboard`
- **Admin Console**: Login → Admin view (for admin users)

---

## Agent Roles & Development Process

### CRITICAL: Agent Hierarchy
- **Claude (Overlord)**: Strategic director, creates patch plans, delegates work
- **Codex (Minion)**: Code execution agent, follows detailed instructions
- **Claude NEVER codes directly** - creates framework for Codex to execute

### Development Workflow
1. **Thin-slice work**: One narrow outcome per task
2. **UI-first then logic**: Build layouts before wiring data
3. **Minimal diffs**: Touch smallest file set, <60 LOC changes
4. **Modularity**: UI in ui_*.py, logic in data.py, client in firebase.py
5. **Tests as contract**: Update tests matching acceptance criteria

---

## Emergency Recovery Info

### If Session Reboots
1. **Read this document first** - full context restoration
2. **Check AGENTS.md** - development guardrails and roles
3. **Review git status** - see current changes
4. **Run tests** - validate current state

### Critical Files for Context
- `AGENTS.md` - Project guardrails and agent roles
- `PROJECT_ROADMAP.md` - This document
- `streamlit_app/app.py` - Main application entry point
- `run_app.py` - Production launcher
- `test_leaderboard_window.py` - Latest test implementation

### Environment Setup
```bash
conda activate leaderboard_env
conda install psutil  # if needed
python -m pytest test_leaderboard_window.py  # validate tests
python run_app.py  # start application
```

---

## Success Metrics

### Phase 1 (Web App)
- [ ] 100% test coverage passing
- [ ] Sub-3 second startup time
- [ ] Support 50+ concurrent users
- [ ] 99%+ uptime on Streamlit Cloud

### Phase 2 (PWA)
- [ ] Mobile install rate >50%
- [ ] Mobile user session time >web
- [ ] Offline functionality tested

### Phase 3 (Native Mobile)
- [ ] App store approval
- [ ] 4+ star rating
- [ ] Native features utilized

---

**Next Session TODO**: Have Codex complete testing validation and report results.