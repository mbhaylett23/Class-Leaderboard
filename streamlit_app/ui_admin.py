import streamlit as st
from . import data
from .models import Category
from datetime import datetime

CATEGORIES_POOL = [
    ("clarity","Clarity & Structure"),
    ("evidence","Evidence & Examples"),
    ("creativity","Creativity / Originality"),
    ("delivery","Delivery & Presence"),
    ("visuals","Visual Design / Slides"),
    ("techdepth","Technical Depth"),
    ("story","Storytelling / Narrative"),
    ("persuasion","Persuasion / Call-to-Action"),
]

def admin_view(user):
    st.header("Admin — Control Panel")

    st.subheader("Classes")
    classes = data.list_classes()
    cols = st.columns(2)
    with cols[0]:
        class_id = st.selectbox("Select class", [c["id"] for c in classes] if classes else [], format_func=lambda i: next(c["name"] for c in classes if c["id"]==i))
    with cols[1]:
        new_name = st.text_input("New class name")
        if st.button("Create Class"):
            if new_name:
                from .firebase import get_db
                db = get_db()
                ref = db.collection("classes").document()
                ref.set({"id":ref.id,"name":new_name,"archived":False,"createdAt":datetime.utcnow()})
                st.success("Class created"); st.rerun()

    if not class_id:
        st.stop()

    st.subheader("Sessions")
    sessions = data.list_sessions(class_id)

    with st.expander("Create Session"):
        title = st.text_input("Title")
        desc = st.text_area("Description")
        weighting = st.slider("Teacher weighting (%)", 0, 100, 50)
        allow_edits = st.toggle("Allow vote edits while session is open", True)
        st.info("💡 Sessions remain open until you manually close them. Perfect for multi-day presentations!")

        st.caption("Pick 4–5 categories")
        chosen = st.multiselect("Categories", CATEGORIES_POOL, default=CATEGORIES_POOL[:5], format_func=lambda t: t[1])
        if st.button("Create Session", type="primary"):
            cats = [Category(id=k,label=v).model_dump() for (k,v) in chosen]
            payload = {
                "title": title or f"Session {len(sessions)+1}",
                "description": desc,
                "tags": [],
                "categories": cats,
                "weighting": {"teacherPct": weighting, "peersPct": 100 - weighting},
                "status": "scheduled",
                "allowEditsUntilClose": allow_edits,
            }
            created = data.create_session(class_id, payload)
            st.success(f"Created session {created['title']}")

    st.subheader("Open/Close Session")
    if sessions:
        pick = st.selectbox("Session", [s["id"] for s in sessions], format_func=lambda i: next(s["title"] for s in sessions if s["id"]==i))
        s = next(s for s in sessions if s["id"]==pick)
        st.write(f"Status: **{s['status']}**")
        cols = st.columns(3)
        with cols[0]:
            if st.button("Open"):
                data.set_session_status(class_id, pick, "open"); st.rerun()
        with cols[1]:
            if st.button("Close"):
                data.set_session_status(class_id, pick, "closed"); st.rerun()
        with cols[2]:
            if st.button("Archive"):
                data.set_session_status(class_id, pick, "archived"); st.rerun()

        if pick:
            st.subheader("Export Data")
            export_cols = st.columns(3)
            with export_cols[0]:
                csv_data = data.export_to_csv(class_id, pick)
                if csv_data:
                    st.download_button(
                        label="Export CSV",
                        data=csv_data,
                        file_name=f"session_{pick}_rankings.csv",
                        mime="text/csv",
                        key=f"export_csv_{pick}",
                    )
                else:
                    st.button("Export CSV", disabled=True, key=f"export_csv_disabled_{pick}")
            with export_cols[1]:
                excel_data = data.export_to_excel(class_id, pick)
                if excel_data:
                    st.download_button(
                        label="Export Excel",
                        data=excel_data,
                        file_name=f"session_{pick}_rankings.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key=f"export_excel_{pick}",
                    )
                else:
                    st.button("Export Excel", disabled=True, key=f"export_excel_disabled_{pick}")

            st.subheader("Teacher Voting")
            team_cols = st.columns([2, 1])
            with team_cols[0]:
                # Get actual teams from current session votes
                teams = ["Team Alpha", "Team Beta", "Team Gamma"]  # TODO: get from session data
                st.selectbox("Team", teams, key=f"teacher_team_{pick}")
            with team_cols[1]:
                st.caption("Rate each category 1-5")
            slider_cols = st.columns(2)
            for idx, (cat_id, cat_label) in enumerate(CATEGORIES_POOL):
                with slider_cols[idx % 2]:
                    st.slider(cat_label, 1, 5, 3, key=f"teacher_vote_{pick}_{cat_id}")
            if st.button("Submit Teacher Vote", type="primary", key=f"teacher_submit_{pick}"):
                selected_team = st.session_state[f"teacher_team_{pick}"]
                ratings = {cat_id: st.session_state[f"teacher_vote_{pick}_{cat_id}"] for cat_id, _ in CATEGORIES_POOL}
                data.submit_teacher_vote(class_id, pick, user["email"], selected_team, ratings)
                st.success("Teacher vote recorded!")
