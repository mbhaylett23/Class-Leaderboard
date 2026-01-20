import hashlib
import streamlit as st
from typing import List, Dict
from datetime import datetime
from .firebase import get_db

db = get_db()

def class_ref(class_id): return db.collection("classes").document(class_id)
def session_ref(class_id, session_id): return class_ref(class_id).collection("sessions").document(session_id)
def vote_ref(class_id, session_id, user_id): return session_ref(class_id, session_id).collection("votes").document(user_id)
def teacher_vote_ref(class_id, session_id, admin_id): return session_ref(class_id, session_id).collection("teacherVotes").document(admin_id)
def team_ref(class_id, team_id): return class_ref(class_id).collection("teams").document(team_id)
def user_ref(class_id, user_id): return class_ref(class_id).collection("users").document(user_id)

def list_teams(class_id):
    return [{**d.to_dict(), "id": d.id} for d in class_ref(class_id).collection("teams").stream()]

def get_session(class_id, session_id):
    doc = session_ref(class_id, session_id).get()
    return ({**doc.to_dict(), "id": doc.id} if doc.exists else None)

def list_classes():
    return [ {**d.to_dict(), "id": d.id} for d in db.collection("classes").where("archived","==",False).stream() ]

def list_sessions(class_id):
    return [ {**d.to_dict(), "id": d.id} for d in class_ref(class_id).collection("sessions").order_by("createdAt").stream() ]

def create_session(class_id, payload: dict):
    payload["createdAt"] = datetime.utcnow()
    doc = class_ref(class_id).collection("sessions").document()
    payload["id"] = doc.id
    doc.set(payload)
    return payload

def set_session_status(class_id, session_id, status: str):
    stamp = {"status": status}
    if status == "open":
        stamp["openedAt"] = datetime.utcnow()
    elif status == "closed":
        stamp["closedAt"] = datetime.utcnow()
    session_ref(class_id, session_id).update(stamp)

def submit_vote(class_id, session_id, user_id, team_id, ratings: Dict[str,int], super_vote=False):
    now = datetime.utcnow()
    vote = {"userId": user_id, "teamId": team_id, "ratings": ratings, "superVote": super_vote, "updatedAt": now}
    doc = vote_ref(class_id, session_id, user_id).get()
    if doc.exists:
        prev = doc.to_dict()
        history = prev.get("editedHistory", [])
        history.append({"ts": now, "ratings": prev.get("ratings", {})})
        vote["editedHistory"] = history
        vote["createdAt"] = prev.get("createdAt")
    else:
        vote["createdAt"] = now
    vote_ref(class_id, session_id, user_id).set(vote)
    return vote

def submit_teacher_vote(class_id, session_id, admin_id, team_id, ratings: Dict[str,int]):
    clean = {}
    for cid, score in ratings.items():
        value = int(score)
        if value < 1 or value > 5:
            raise ValueError("Teacher rating must be between 1 and 5")
        clean[cid] = value
    now = datetime.utcnow()
    doc = {"userId": admin_id, "teamId": team_id, "ratings": clean, "updatedAt": now, "createdAt": now}
    teacher_vote_ref(class_id, session_id, admin_id).set(doc)
    return doc

def aggregate_scores(class_id, session_id, categories: List[dict], teacherPct: int, peersPct: int):
    cats = [c["id"] for c in categories]
    votes = list(session_ref(class_id, session_id).collection("votes").stream())
    tvotes = list(session_ref(class_id, session_id).collection("teacherVotes").stream())

    per_team = {}
    for v in votes:
        d = v.to_dict()
        t = d["teamId"]
        per_team.setdefault(t, {"peer_sum":0, "teacher_sum":0, "cats":{cid:{"peer":0,"teacher":0} for cid in cats}})
        s = sum(int(d["ratings"].get(cid,0)) for cid in cats)
        per_team[t]["peer_sum"] += s
        for cid in cats:
            per_team[t]["cats"][cid]["peer"] += int(d["ratings"].get(cid,0))

    for tv in tvotes:
        d = tv.to_dict()
        t = d["teamId"]
        per_team.setdefault(t, {"peer_sum":0, "teacher_sum":0, "cats":{cid:{"peer":0,"teacher":0} for cid in cats}})
        s = sum(int(d["ratings"].get(cid,0)) for cid in cats)
        per_team[t]["teacher_sum"] += s
        for cid in cats:
            per_team[t]["cats"][cid]["teacher"] += int(d["ratings"].get(cid,0))

    for t,vals in per_team.items():
        vals["combined"] = int(vals["peer_sum"] * (peersPct/100.0) + vals["teacher_sum"] * (teacherPct/100.0))
    return per_team


_TEAM_COLOR_PALETTE = [
    "#636EFA",  # vivid indigo
    "#EF553B",  # soft red
    "#00CC96",  # bright green
    "#AB63FA",  # lavender
    "#FFA15A",  # warm orange
    "#19D3F3",  # aqua blue
    "#FF6692",  # pink coral
    "#B6E880",  # lime tint
    "#FF97FF",  # fuchsia
    "#FECB52",  # amber
]
_TEAM_COLOR_DEFAULT = "#636EFA"


def get_team_color(team_name: str) -> str:
    """Return a deterministic color for a team name or identifier."""
    if not team_name:
        return _TEAM_COLOR_DEFAULT
    normalized = team_name.strip().lower()
    if not normalized:
        return _TEAM_COLOR_DEFAULT
    digest = hashlib.sha256(normalized.encode("utf-8")).digest()
    index = digest[0] % len(_TEAM_COLOR_PALETTE)
    return _TEAM_COLOR_PALETTE[index]


def export_session_data(class_id: str, session_id: str) -> Dict:
    """Export all data for a session including votes, teams, and scores."""
    import pandas as pd

    session = get_session(class_id, session_id)
    if not session:
        return {"error": "Session not found"}

    categories = session.get("categories", [])
    weighting = session.get("weighting", {})
    teacher_pct = int(weighting.get("teacherPct", 50))
    peers_pct = int(weighting.get("peersPct", 50))

    # Get votes
    votes = list(session_ref(class_id, session_id).collection("votes").stream())
    teacher_votes = list(session_ref(class_id, session_id).collection("teacherVotes").stream())
    teams = list_teams(class_id)
    team_lookup = {t["id"]: t.get("name", t["id"]) for t in teams}

    # Build vote records
    vote_records = []
    for v in votes:
        d = v.to_dict()
        record = {
            "voter_id": d.get("userId", ""),
            "team_id": d.get("teamId", ""),
            "team_name": team_lookup.get(d.get("teamId", ""), d.get("teamId", "")),
            "vote_type": "peer",
            "created_at": d.get("createdAt", ""),
            "updated_at": d.get("updatedAt", ""),
        }
        for cat in categories:
            cat_id = cat["id"]
            record[f"rating_{cat_id}"] = d.get("ratings", {}).get(cat_id, 0)
        vote_records.append(record)

    for tv in teacher_votes:
        d = tv.to_dict()
        record = {
            "voter_id": d.get("userId", ""),
            "team_id": d.get("teamId", ""),
            "team_name": team_lookup.get(d.get("teamId", ""), d.get("teamId", "")),
            "vote_type": "teacher",
            "created_at": d.get("createdAt", ""),
            "updated_at": d.get("updatedAt", ""),
        }
        for cat in categories:
            cat_id = cat["id"]
            record[f"rating_{cat_id}"] = d.get("ratings", {}).get(cat_id, 0)
        vote_records.append(record)

    # Build scores summary
    scores = aggregate_scores(class_id, session_id, categories, teacher_pct, peers_pct)
    score_records = []
    for team_id, metrics in scores.items():
        score_records.append({
            "team_id": team_id,
            "team_name": team_lookup.get(team_id, team_id),
            "peer_score": metrics.get("peer_sum", 0),
            "teacher_score": metrics.get("teacher_sum", 0),
            "combined_score": metrics.get("combined", 0),
        })

    return {
        "session": session,
        "votes": vote_records,
        "scores": score_records,
        "categories": categories,
    }


def export_to_csv(class_id: str, session_id: str) -> bytes:
    """Export session data to CSV format."""
    import pandas as pd
    import io

    data = export_session_data(class_id, session_id)
    if "error" in data:
        return b""

    # Create scores DataFrame
    scores_df = pd.DataFrame(data["scores"])
    scores_df = scores_df.sort_values("combined_score", ascending=False).reset_index(drop=True)
    scores_df.insert(0, "rank", range(1, len(scores_df) + 1))

    output = io.StringIO()
    scores_df.to_csv(output, index=False)
    return output.getvalue().encode("utf-8")


def export_to_excel(class_id: str, session_id: str) -> bytes:
    """Export session data to Excel format with multiple sheets."""
    import pandas as pd
    import io

    data = export_session_data(class_id, session_id)
    if "error" in data:
        return b""

    # Create DataFrames
    scores_df = pd.DataFrame(data["scores"])
    scores_df = scores_df.sort_values("combined_score", ascending=False).reset_index(drop=True)
    scores_df.insert(0, "rank", range(1, len(scores_df) + 1))

    votes_df = pd.DataFrame(data["votes"])

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        scores_df.to_excel(writer, sheet_name="Rankings", index=False)
        if not votes_df.empty:
            votes_df.to_excel(writer, sheet_name="Votes", index=False)

    return output.getvalue()
