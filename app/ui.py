
from datetime import date, timedelta

import pandas as pd
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from sqlalchemy.orm import Session

from app.database import engine
from app.models import StudyTopic
from app.scheduler import Topic, generate_schedule


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Study Planner",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------------------------------------
# PROFESSIONAL LIGHT THEME
# --------------------------------------------------

st.markdown(
    """
    <style>
    .stApp {
        background: #F6F8F7;
        color: #192B2A;
    }

    [data-testid="stHeader"] {
        background: #F6F8F7;
    }

    [data-testid="stSidebar"] {
        background: #FFFFFF;
        border-right: 1px solid #E3EAE6;
    }

    [data-testid="stSidebar"] * {
        color: #263B38;
    }

    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span {
        color: #526663 !important;
    }

    .block-container {
        max-width: 1220px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .brand-title {
        font-size: 1.45rem;
        font-weight: 750;
        letter-spacing: -0.04em;
        color: #192B2A;
    }

    .eyebrow {
        color: #53716B;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-bottom: 0.7rem;
    }

    .hero-title {
        color: #192B2A;
        font-size: clamp(2rem, 4vw, 2.8rem);
        line-height: 1.2;
        font-weight: 750;
        letter-spacing: -0.045em;
        margin-bottom: 0.65rem;
    }

    .hero-copy {
        color: #687875;
        font-size: 1rem;
        line-height: 1.7;
        max-width: 700px;
        margin-bottom: 1.6rem;
    }

    .section-title {
        color: #192B2A;
        font-size: 1.2rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        margin-top: 0.5rem;
        margin-bottom: 0.35rem;
    }

    .muted {
        color: #71807D;
        font-size: 0.88rem;
        line-height: 1.6;
    }

    [data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E3EAE6;
        border-radius: 12px;
        padding: 18px 20px;
    }

    [data-testid="stMetricLabel"] {
        color: #526663 !important;
    }

    [data-testid="stMetricValue"] {
        color: #192B2A !important;
    }

    [data-testid="stForm"] {
        background: #FFFFFF;
        border: 1px solid #E3EAE6;
        border-radius: 14px;
        padding: 22px;
    }

    .stButton > button,
    .stFormSubmitButton > button,
    .stDownloadButton > button {
        background: #214E47 !important;
        color: #FFFFFF !important;
        border: 1px solid #214E47 !important;
        border-radius: 8px !important;
        min-height: 42px;
        font-weight: 600 !important;
    }

    .stButton > button p,
    .stFormSubmitButton > button p,
    .stDownloadButton > button p {
        color: #FFFFFF !important;
    }

    .stButton > button:hover,
    .stFormSubmitButton > button:hover,
    .stDownloadButton > button:hover {
        background: #173C36 !important;
        border-color: #173C36 !important;
    }

    [data-testid="stDataFrame"] {
        background: #FFFFFF;
        border: 1px solid #E3EAE6;
        border-radius: 10px;
        overflow: hidden;
    }

    hr {
        border-color: #E3EAE6;
    }

    #MainMenu,
    footer {
        visibility: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# DATABASE FUNCTIONS
# --------------------------------------------------

def load_topics():
    """Load subjects saved in PostgreSQL."""
    with Session(engine) as session:
        rows = (
            session.query(StudyTopic)
            .order_by(StudyTopic.exam_date, StudyTopic.id)
            .all()
        )

        return [
            {
                "id": item.id,
                "name": item.name,
                "exam_date": item.exam_date,
                "difficulty": item.difficulty,
                "confidence": item.confidence,
                "estimated_hours": item.estimated_hours,
            }
            for item in rows
        ]


def save_topic(name, exam_date, difficulty, confidence, hours):
    """Save a new subject."""
    with Session(engine) as session:
        topic = StudyTopic(
            name=name.strip(),
            exam_date=exam_date,
            difficulty=difficulty,
            confidence=confidence,
            estimated_hours=hours,
        )
        session.add(topic)
        session.commit()


def delete_topic(topic_id):
    """Delete a selected subject from PostgreSQL."""
    with Session(engine) as session:
        topic = session.get(StudyTopic, topic_id)

        if topic is None:
            return False

        session.delete(topic)
        session.commit()
        return True


def navigate_to(destination):
    """Navigate to a selected page."""
    st.session_state["page"] = destination


def render_header(eyebrow, title, description):
    """Display a consistent page heading."""
    st.markdown(
        f"""
        <div class="eyebrow">{eyebrow}</div>
        <div class="hero-title">{title}</div>
        <div class="hero-copy">{description}</div>
        """,
        unsafe_allow_html=True,
    )


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "page" not in st.session_state:
    st.session_state["page"] = "Overview"

if "generated_schedule" not in st.session_state:
    st.session_state["generated_schedule"] = None

if "unscheduled_hours" not in st.session_state:
    st.session_state["unscheduled_hours"] = 0.0


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.markdown(
        '<div class="brand-title">Study Planner</div>',
        unsafe_allow_html=True,
    )
    st.caption("PERSONAL LEARNING WORKSPACE")
    st.divider()

    st.radio(
        "WORKSPACE",
        ["Overview", "My Subjects", "Study Schedule"],
        key="page",
    )

    st.divider()
    st.caption("Organise your time. Stay consistent.")
    st.caption(f"Today · {date.today():%d %b %Y}")


topics = load_topics()
page = st.session_state["page"]


# --------------------------------------------------
# OVERVIEW
# --------------------------------------------------

if page == "Overview":

    render_header(
        "YOUR WORKSPACE",
        "Make time for what matters.",
        "Your study commitments, upcoming exams and priorities, "
        "organised in one clear workspace.",
    )

    upcoming = sorted(
        [
            item for item in topics
            if item["exam_date"] >= date.today()
        ],
        key=lambda item: item["exam_date"],
    )

    total_hours = sum(
        item["estimated_hours"] for item in topics
    )

    next_exam = (
        upcoming[0]["exam_date"].strftime("%d %b %Y")
        if upcoming
        else "No upcoming exams"
    )

    col1, col2, col3 = st.columns(3)

    col1.metric("Saved subjects", len(topics))
    col2.metric("Estimated study hours", f"{total_hours:g} h")
    col3.metric("Next exam", next_exam)

    st.write("")

    st.markdown(
        '<div class="section-title">Upcoming exams</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="muted">Your next deadlines, based on saved subjects.</div>',
        unsafe_allow_html=True,
    )

    if upcoming:
        exam_rows = [
            {
                "Subject": item["name"],
                "Exam date": item["exam_date"].strftime("%d %b %Y"),
                "Day": item["exam_date"].strftime("%A"),
                "Days remaining": (
                    item["exam_date"] - date.today()
                ).days,
                "Confidence": f'{item["confidence"]}/5',
                "Difficulty": f'{item["difficulty"]}/5',
            }
            for item in upcoming
        ]

        st.dataframe(
            pd.DataFrame(exam_rows),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No upcoming exams. Add a subject to get started.")

    st.write("")

    left, right = st.columns([1.25, 1])

    with left:
        st.markdown(
            '<div class="section-title">Learning priorities</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="muted">Subjects that may need more attention.</div>',
            unsafe_allow_html=True,
        )

        if topics:
            priorities = sorted(
                topics,
                key=lambda item: (
                    item["confidence"],
                    -item["difficulty"],
                    item["exam_date"],
                ),
            )[:5]

            for item in priorities:
                st.markdown(f'**{item["name"]}**')
                st.caption(
                    f'Confidence {item["confidence"]}/5 · '
                    f'Difficulty {item["difficulty"]}/5 · '
                    f'Exam {item["exam_date"]:%d %b %Y}'
                )
        else:
            st.caption("Your saved subjects will appear here.")

    with right:
        st.markdown(
            '<div class="section-title">Quick actions</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="muted">Continue with your study planning.</div>',
            unsafe_allow_html=True,
        )

        st.write("")

        st.button(
            "Add a subject",
            key="quick_add_subject",
            use_container_width=True,
            on_click=navigate_to,
            args=("My Subjects",),
        )

        st.button(
            "Build a study schedule",
            key="quick_build_schedule",
            use_container_width=True,
            on_click=navigate_to,
            args=("Study Schedule",),
        )


# --------------------------------------------------
# MY SUBJECTS: ADD AND DELETE
# --------------------------------------------------

elif page == "My Subjects":

    render_header(
        "SUBJECT MANAGEMENT",
        "My subjects",
        "Add subjects, track exam dates and manage your preparation.",
    )

    st.markdown(
        '<div class="section-title">Add a subject</div>',
        unsafe_allow_html=True,
    )

    with st.form("add_subject_form", clear_on_submit=True):

        name = st.text_input(
            "Subject name",
            placeholder="e.g. Algorithms and Data Structures",
        )

        col1, col2 = st.columns(2)

        with col1:
            exam = st.date_input(
                "Exam date",
                value=date.today() + timedelta(days=7),
                min_value=date.today(),
            )

            st.caption(f"Exam day: **{exam.strftime('%A')}**")

            difficulty = st.slider(
                "Difficulty",
                min_value=1,
                max_value=5,
                value=3,
                help="1 = easy, 5 = very difficult",
            )

        with col2:
            confidence = st.slider(
                "Current confidence",
                min_value=1,
                max_value=5,
                value=3,
                help="1 = low confidence, 5 = high confidence",
            )

            hours = st.number_input(
                "Estimated study hours needed",
                min_value=0.5,
                max_value=100.0,
                value=3.0,
                step=0.5,
            )

        submitted = st.form_submit_button(
            "Save subject",
            use_container_width=True,
        )

        if submitted:
            if not name.strip():
                st.error("Please enter a subject name.")
            else:
                try:
                    save_topic(
                        name,
                        exam,
                        difficulty,
                        confidence,
                        hours,
                    )
                    st.session_state["generated_schedule"] = None
                    st.success(f"{name.strip()} saved successfully.")
                    st.rerun()
                except Exception as error:
                    st.error(
                        "Could not save the subject. "
                        "Please check your database connection."
                    )
                    st.exception(error)

    st.write("")

    st.markdown(
        '<div class="section-title">Saved subjects</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="muted">Subjects currently stored in your database.</div>',
        unsafe_allow_html=True,
    )

    if topics:
        subject_rows = [
            {
                "Subject": item["name"],
                "Exam date": item["exam_date"].strftime("%d %b %Y"),
                "Day": item["exam_date"].strftime("%A"),
                "Difficulty": item["difficulty"],
                "Confidence": item["confidence"],
                "Estimated hours": item["estimated_hours"],
            }
            for item in topics
        ]

        st.dataframe(
            pd.DataFrame(subject_rows),
            use_container_width=True,
            hide_index=True,
        )

        st.write("")

        st.markdown(
            '<div class="section-title">Delete a subject</div>',
            unsafe_allow_html=True,
        )
        st.caption(
            "Choose a subject and confirm before deleting it permanently."
        )

        topic_options = {
            f'{item["name"]} — {item["exam_date"]:%d %b %Y} (ID: {item["id"]})':
                item["id"]
            for item in topics
        }

        selected_label = st.selectbox(
            "Select subject",
            list(topic_options.keys()),
            key="delete_subject_selection",
        )

        confirm_delete = st.checkbox(
            "I confirm that I want to delete this subject.",
            key="confirm_delete_subject",
        )

        if st.button(
            "Delete selected subject",
            type="secondary",
            use_container_width=False,
        ):
            if not confirm_delete:
                st.warning("Please confirm before deleting the subject.")
            else:
                selected_id = topic_options[selected_label]

                try:
                    deleted = delete_topic(selected_id)

                    if deleted:
                        st.session_state["generated_schedule"] = None
                        st.success("Subject deleted successfully.")
                        st.rerun()
                    else:
                        st.error("Subject not found. Refresh and try again.")
                except Exception as error:
                    st.error("Could not delete the subject.")
                    st.exception(error)

    else:
        st.info("No subjects saved yet. Add your first subject above.")


# --------------------------------------------------
# STUDY SCHEDULE
# --------------------------------------------------

elif page == "Study Schedule":

    render_header(
        "STUDY PLANNING",
        "Your study schedule",
        "Generate a study plan based on your saved subjects, exam dates "
        "and daily availability.",
    )

    if not topics:
        st.info(
            "Add at least one subject in My Subjects before generating a plan."
        )

        st.button(
            "Go to My Subjects",
            on_click=navigate_to,
            args=("My Subjects",),
        )

    else:
        with st.form("schedule_settings_form"):

            col1, col2, col3 = st.columns(3)

            with col1:
                start = st.date_input(
                    "Start date",
                    value=date.today(),
                    min_value=date.today(),
                )

            with col2:
                daily_hours = st.number_input(
                    "Available study hours per day",
                    min_value=0.5,
                    max_value=12.0,
                    value=2.0,
                    step=0.5,
                )

            with col3:
                session_hours = st.number_input(
                    "Session duration in hours",
                    min_value=0.5,
                    max_value=3.0,
                    value=1.0,
                    step=0.5,
                )

            generate = st.form_submit_button(
                "Generate study schedule",
                use_container_width=True,
            )

        if generate:
            planner_topics = [
                Topic(
                    name=item["name"],
                    exam_date=item["exam_date"],
                    difficulty=item["difficulty"],
                    confidence=item["confidence"],
                    estimated_hours=item["estimated_hours"],
                )
                for item in topics
            ]

            try:
                result = generate_schedule(
                    topics=planner_topics,
                    start_date=start,
                    daily_available_hours=daily_hours,
                    session_hours=session_hours,
                )

                schedule_rows = [
                    {
                        "Date": item.date.strftime("%d %b %Y"),
                        "Day": item.date.strftime("%A"),
                        "Subject": item.topic,
                        "Duration (hours)": item.duration_hours,
                        "Priority score": round(item.priority_score, 3),
                    }
                    for item in result.sessions
                ]

                st.session_state["generated_schedule"] = schedule_rows
                st.session_state["unscheduled_hours"] = (
                    result.unscheduled_hours
                )

            except ValueError as error:
                st.error(str(error))

        schedule_rows = st.session_state["generated_schedule"]

        if schedule_rows is not None:
            st.write("")

            if schedule_rows:
                st.markdown(
                    '<div class="section-title">Planned study sessions</div>',
                    unsafe_allow_html=True,
                )

                st.dataframe(
                    pd.DataFrame(schedule_rows),
                    use_container_width=True,
                    hide_index=True,
                )

                csv_data = pd.DataFrame(schedule_rows).to_csv(index=False)

                st.download_button(
                    "Download schedule as CSV",
                    data=csv_data,
                    file_name="study_schedule.csv",
                    mime="text/csv",
                )
            else:
                st.warning(
                    "No sessions were scheduled with the current settings."
                )

            unscheduled = st.session_state["unscheduled_hours"]

            if unscheduled:
                st.warning(
                    f"{unscheduled:.1f} study hours could not be scheduled. "
                    "Consider starting earlier or increasing your daily "
                    "study availability."
                )
