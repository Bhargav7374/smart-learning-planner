
from datetime import date, timedelta

import pytest

from app.scheduler import Topic, generate_schedule


START = date(2026, 10, 17)


def make_topic(
    name="ADA",
    exam_in_days=2,
    difficulty=3,
    confidence=3,
    hours=2.0,
):
    return Topic(
        name=name,
        exam_date=START + timedelta(days=exam_in_days),
        difficulty=difficulty,
        confidence=confidence,
        estimated_hours=hours,
    )


def test_generates_a_schedule():
    result = generate_schedule(
        topics=[make_topic(hours=2)],
        start_date=START,
        daily_available_hours=2,
    )

    assert len(result.sessions) == 2
    assert sum(s.duration_hours for s in result.sessions) == 2
    assert result.unscheduled_hours == {}


def test_never_exceeds_daily_available_hours():
    topics = [
        make_topic("ADA", exam_in_days=2, hours=3),
        make_topic("DBMS", exam_in_days=3, hours=3),
    ]

    result = generate_schedule(topics, START, daily_available_hours=2)

    totals = {}
    for session in result.sessions:
        totals[session.date] = (
            totals.get(session.date, 0) + session.duration_hours
        )

    assert all(hours <= 2 for hours in totals.values())


def test_earlier_exam_is_prioritized():
    topics = [
        make_topic("DBMS", exam_in_days=3, hours=1),
        make_topic("ADA", exam_in_days=1, hours=1),
    ]

    result = generate_schedule(topics, START, daily_available_hours=1)

    assert result.sessions[0].topic == "ADA"


def test_reports_unallocated_hours():
    topic = make_topic(exam_in_days=0, hours=3)

    result = generate_schedule(
        [topic],
        START,
        daily_available_hours=1,
    )

    assert sum(s.duration_hours for s in result.sessions) == 1
    assert result.unscheduled_hours == {"ADA": 2}


def test_rejects_zero_daily_availability():
    with pytest.raises(ValueError, match="Daily available hours"):
        generate_schedule(
            [make_topic()],
            START,
            daily_available_hours=0,
        )


def test_rejects_invalid_difficulty():
    topic = make_topic(difficulty=6)

    with pytest.raises(ValueError, match="Difficulty"):
        generate_schedule([topic], START, 2)


def test_rejects_exam_date_in_the_past():
    topic = Topic(
        name="ADA",
        exam_date=START - timedelta(days=1),
        difficulty=3,
        confidence=3,
        estimated_hours=1,
    )

    with pytest.raises(ValueError, match="before the start date"):
        generate_schedule([topic], START, 2)


def test_rejects_duplicate_topic_names():
    topics = [make_topic("ADA"), make_topic("ada")]

    with pytest.raises(ValueError, match="unique"):
        generate_schedule(topics, START, 2)
