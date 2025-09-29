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
