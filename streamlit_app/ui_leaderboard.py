"""Dedicated fullscreen leaderboard view for projection."""
from __future__ import annotations

import time
from datetime import datetime
from typing import Dict, List

import altair as alt
import pandas as pd
import streamlit as st

from . import data

REFRESH_SECONDS = 5
TEACHER_BAR_COLOR = "#3B82F6"
PEER_BAR_COLOR = "#16A34A"


def _get_query_param(name: str) -> str | None:
    value = st.query_params.get(name)
    if isinstance(value, list):
        return value[0] if value else None
    return value


def _update_query_params(**kwargs) -> None:
    params = st.query_params
    for key, value in kwargs.items():
        if value is None:
            params.pop(key, None)
        else:
            params[key] = value


def _pick_class(classes: List[Dict]) -> str | None:
    if not classes:
        st.warning("No active classes available.")
        return None

    class_ids = [c["id"] for c in classes]
    class_lookup = {c["id"]: c for c in classes}
    preselected = _get_query_param("class")

    index = class_ids.index(preselected) if preselected in class_lookup else 0
    selected = st.selectbox(
        "Class",
        class_ids,
        index=index,
        format_func=lambda cid: class_lookup[cid].get("name", cid),
        label_visibility="collapsed",
        key="leaderboard_class",
    )
    if selected != preselected:
        _update_query_params(view="leaderboard", **{"class": selected})
    return selected


def _pick_session(class_id: str) -> Dict | None:
    sessions = data.list_sessions(class_id)
    if not sessions:
        st.warning("No sessions found for this class yet.")
        return None

    visible_sessions = [s for s in sessions if s.get("status") in {"open", "scheduled", "closed"}]
    if not visible_sessions:
        st.warning("No active or recent sessions to display.")
        return None

    session_lookup = {s["id"]: s for s in visible_sessions}
    preselected = _get_query_param("session")
    default_id = preselected if preselected in session_lookup else None

    if default_id is None:
        open_sessions = [s for s in visible_sessions if s.get("status") == "open"]
        default_id = (open_sessions[0]["id"] if open_sessions else visible_sessions[-1]["id"])

    selected = st.selectbox(
        "Session",
        [s["id"] for s in visible_sessions],
        index=[s["id"] for s in visible_sessions].index(default_id),
        format_func=lambda sid: session_lookup[sid].get("title", sid),
        label_visibility="collapsed",
        key="leaderboard_session",
    )
    if selected != preselected:
        _update_query_params(view="leaderboard", **{"class": class_id, "session": selected})
    return session_lookup[selected]


def _build_leaderboard_rows(class_id: str, session: Dict) -> pd.DataFrame:
    categories = session.get("categories", [])
    weighting = session.get("weighting", {})
    teacher_pct = int(weighting.get("teacherPct", 50))
    peers_pct = int(weighting.get("peersPct", 50))

    raw_scores = data.aggregate_scores(class_id, session["id"], categories, teacher_pct, peers_pct)
    teams = data.list_teams(class_id)
    team_lookup = {t["id"]: t for t in teams}

    rows = []
    all_ids = sorted({*raw_scores.keys(), *team_lookup.keys()})
    for team_id in all_ids:
        metrics = raw_scores.get(team_id, {})
        combined = int(metrics.get("combined", 0))
        teacher_sum = int(metrics.get("teacher_sum", 0)) if metrics else 0
        peer_sum = int(metrics.get("peer_sum", 0)) if metrics else 0
        team_name = team_lookup.get(team_id, {}).get("name", team_id)
        rows.append({
            "Rank": 0,
            "Team": team_name,
            "Team ID": team_id,
            "Combined": combined,
            "Teacher": teacher_sum,
            "Peers": peer_sum,
            "TeamColor": data.get_team_color(team_name or team_id),
        })

    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df = df.sort_values("Combined", ascending=False).reset_index(drop=True)
    df["Rank"] = df.index + 1
    return df


def leaderboard_view(role: str = "student") -> None:
    """Render a large-format, auto-refreshing leaderboard view."""
    role_key = (role or "student").strip().lower()
    is_admin_view = role_key == "admin"

    st.cache_data.clear()
    st.cache_resource.clear()

    if st.button("🔄 Force Refresh", key="leaderboard_force_refresh"):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.rerun()

    cache_buster = int(time.time())

    st.markdown(
        """
        <style>
        header {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .block-container {padding-top: 1.5rem; max-width: 1200px;}
        .leaderboard-title {font-size: 3rem; text-align: center; margin-bottom: 0.5rem;}
        .leaderboard-caption {text-align: center; font-size: 1.1rem; margin-bottom: 1.5rem;}
        .metric-card {text-align: center; font-size: 1.4rem;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    classes = data.list_classes()
    class_id = _pick_class(classes)
    if not class_id:
        time.sleep(REFRESH_SECONDS)
        st.rerun()

    session = _pick_session(class_id)
    if not session:
        time.sleep(REFRESH_SECONDS)
        st.rerun()

    st.markdown(f"<div class='leaderboard-title'>🏆 {session.get('title', 'Live Leaderboard')}</div>", unsafe_allow_html=True)

    # Export buttons for admin view
    if is_admin_view:
        export_cols = st.columns([1, 1, 1, 3])
        with export_cols[0]:
            csv_data = data.export_to_csv(class_id, session["id"])
            if csv_data:
                st.download_button(
                    label="Export CSV",
                    data=csv_data,
                    file_name=f"session_{session['id']}_rankings.csv",
                    mime="text/csv",
                    key="leaderboard_export_csv",
                )
        with export_cols[1]:
            excel_data = data.export_to_excel(class_id, session["id"])
            if excel_data:
                st.download_button(
                    label="Export Excel",
                    data=excel_data,
                    file_name=f"session_{session['id']}_rankings.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="leaderboard_export_excel",
                )
        with export_cols[2]:
            if st.button("Back to Dashboard", key="back_to_dashboard"):
                st.query_params.clear()
                st.rerun()

    df = _build_leaderboard_rows(class_id, session)
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.markdown(
        f"<div class='leaderboard-caption'>Refreshing every {REFRESH_SECONDS}s · Last updated {timestamp}</div>",
        unsafe_allow_html=True,
    )

    if df.empty:
        st.info("Waiting for the first votes to arrive…")
        time.sleep(REFRESH_SECONDS)
        st.rerun()

    top_row = df.iloc[0]
    st.metric("Leaderboard Leader", f"{top_row['Team']} (Score {top_row['Combined']})")

    team_order = df["Team"].tolist()
    team_colors = df["TeamColor"].tolist()
    df["CacheKey"] = cache_buster

    if not is_admin_view:
        chart_height = max(280, 70 * len(df))
        chart_data = df[["Team", "Combined", "TeamColor", "Rank", "CacheKey"]]
        chart = (
            alt.Chart(chart_data)
            .mark_bar(cornerRadiusTopRight=6, cornerRadiusBottomRight=6)
            .encode(
                y=alt.Y(
                    "Team:N",
                    sort=team_order,
                    title="Team",
                    axis=alt.Axis(labelFontSize=16, titleFontSize=18),
                ),
                x=alt.X(
                    "Combined:Q",
                    title="Weighted Score",
                    axis=alt.Axis(labelFontSize=16, titleFontSize=18),
                ),
                color=alt.Color(
                    "Team:N",
                    scale=alt.Scale(domain=team_order, range=team_colors),
                    legend=None,
                ),
                detail=alt.Detail("CacheKey:Q"),
                tooltip=[
                    alt.Tooltip("Rank:O", title="Rank"),
                    alt.Tooltip("Team:N", title="Team"),
                    alt.Tooltip("Combined:Q", title="Weighted Score"),
                ],
            )
            .properties(height=chart_height, width="container")
        )
        st.altair_chart(chart, use_container_width=True)

        st.dataframe(
            df[["Rank", "Team", "Team ID", "Combined"]],
            use_container_width=True,
            hide_index=True,
        )
    else:
        admin_rows: List[Dict] = []
        for _, row in df.iterrows():
            base = {
                "Team": row["Team"],
                "Rank": int(row["Rank"]),
                "TeamColor": row["TeamColor"],
                "TeacherTotal": int(row["Teacher"]),
                "PeerTotal": int(row["Peers"]),
                "CombinedTotal": int(row["Combined"]),
                "CacheKey": cache_buster,
            }
            admin_rows.append({**base, "ScoreType": "Teacher", "Value": int(row["Teacher"])})
            admin_rows.append({**base, "ScoreType": "Peers", "Value": int(row["Peers"])})
            admin_rows.append({**base, "ScoreType": "Combined", "Value": int(row["Combined"])})

        admin_df = pd.DataFrame(admin_rows)
        teacher_peer_chart = (
            alt.Chart(admin_df[admin_df["ScoreType"].isin(["Teacher", "Peers"])])
            .mark_bar(cornerRadiusTopLeft=2, cornerRadiusTopRight=2)
            .encode(
                x=alt.X(
                    "Team:N",
                    sort=team_order,
                    title="Team",
                    axis=alt.Axis(labelFontSize=14, labelAngle=-20),
                ),
                y=alt.Y("Value:Q", title="Score"),
                color=alt.Color(
                    "ScoreType:N",
                    scale=alt.Scale(domain=["Teacher", "Peers"], range=[TEACHER_BAR_COLOR, PEER_BAR_COLOR]),
                    legend=alt.Legend(title="Components"),
                ),
                xOffset=alt.XOffset("ScoreType:N"),
                detail=alt.Detail("CacheKey:Q"),
                tooltip=[
                    alt.Tooltip("Team:N", title="Team"),
                    alt.Tooltip("ScoreType:N", title="Component"),
                    alt.Tooltip("Value:Q", title="Score"),
                ],
            )
        )

        combined_chart = (
            alt.Chart(admin_df[admin_df["ScoreType"] == "Combined"])
            .mark_bar(cornerRadiusTopLeft=2, cornerRadiusTopRight=2)
            .encode(
                x=alt.X(
                    "Team:N",
                    sort=team_order,
                    title="Team",
                    axis=alt.Axis(labelFontSize=14, labelAngle=-20),
                ),
                y=alt.Y("Value:Q", title="Score"),
                color=alt.Color(
                    "Team:N",
                    scale=alt.Scale(domain=team_order, range=team_colors),
                    legend=None,
                ),
                xOffset=alt.XOffset("ScoreType:N"),
                detail=alt.Detail("CacheKey:Q"),
                tooltip=[
                    alt.Tooltip("Team:N", title="Team"),
                    alt.Tooltip("CombinedTotal:Q", title="Weighted"),
                    alt.Tooltip("TeacherTotal:Q", title="Teacher Sum"),
                    alt.Tooltip("PeerTotal:Q", title="Student Sum"),
                ],
            )
        )

        chart = (
            (teacher_peer_chart + combined_chart)
            .properties(width="container", height=420)
            .configure_axis(labelFontSize=14, titleFontSize=16)
        )
        st.altair_chart(chart, use_container_width=True)
        st.caption("Teacher (blue), Student (green), Combined (team color)")

        st.dataframe(
            df[["Rank", "Team", "Team ID", "Teacher", "Peers", "Combined"]],
            use_container_width=True,
            hide_index=True,
        )

    time.sleep(REFRESH_SECONDS)
    st.rerun()
