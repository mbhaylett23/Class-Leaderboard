import streamlit as st
from . import data
from .models import Category
import pandas as pd
import altair as alt

def student_view(user):
    st.header("Student — Live Voting")

    classes = data.list_classes()
    class_id = st.selectbox("Class", [c["id"] for c in classes], format_func=lambda i: next(c["name"] for c in classes if c["id"]==i)) if classes else None
    if not class_id:
        st.info("No active classes yet.")
        return

    sessions = [s for s in data.list_sessions(class_id) if s.get("status") in ("open","scheduled","closed")]
    sess = st.selectbox("Session", [s["id"] for s in sessions], format_func=lambda i: next(s["title"] for s in sessions if s["id"]==i)) if sessions else None
    if not sess:
        st.info("No sessions.")
        return

    sess_obj = next(s for s in sessions if s["id"]==sess)
    cats = [Category(**c) for c in sess_obj.get("categories", [])]

    st.subheader("Vote")
    team_id = st.text_input("Presenting Team ID (temporary field)")
    ratings = {}
    for c in cats:
        ratings[c.id] = st.slider(c.label, 1, 5, 3, key=f"cat_{c.id}")

    if st.button("Submit Vote", type="primary"):
        if any(v is None for v in ratings.values()):
            st.error("Please rate all categories before submitting.")
        else:
            data.submit_vote(class_id, sess, user_id=user["email"], team_id=team_id, ratings=ratings)
            st.success("Vote submitted.")

    st.subheader("Live Leaderboard")
    scores = data.aggregate_scores(class_id, sess, [c.model_dump() for c in cats], sess_obj["weighting"]["teacherPct"], sess_obj["weighting"]["peersPct"])
    if not scores:
        st.info("No votes yet.")
        return
    df = pd.DataFrame([{"team":k, **v} for k,v in scores.items()])
    chart = alt.Chart(df).mark_bar().encode(y="team:N", x="combined:Q", tooltip=["peer_sum","teacher_sum","combined"])
    st.altair_chart(chart, use_container_width=True)

    with st.expander("Details (categories: peers vs teacher)"):
        rows = []
        for team, vals in scores.items():
            for cid, comp in vals["cats"].items():
                rows.append({"team":team, "category":cid, "peer":comp["peer"], "teacher":comp["teacher"]})
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
