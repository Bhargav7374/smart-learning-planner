
"""Core scheduling logic for Smart Learning Planner AI."""

from dataclasses import dataclass
from datetime import date, timedelta


@dataclass(frozen=True)
class Topic:
    name: str
    exam_date: date
    difficulty: int          # 1 (easy) to 5 (very difficult)
    confidence: int          # 1 (low) to 5 (high)
    estimated_hours: float


@dataclass(frozen=True)
class StudySession:
    date: date
    topic: str
    duration_hours: float
    priority_score: float


@dataclass
class ScheduleResult:
    sessions: list[StudySession]
    unscheduled_hours: dict[str, float]


def validate_inputs(
    topics: list[Topic],
    start_date: date,
    daily_available_hours: float,
    session_hours: float,
) -> None:
    if not topics:
        raise ValueError("Add at least one topic.")

    if daily_available_hours <= 0:
        raise ValueError("Daily available hours must be positive.")

    if session_hours <= 0:
        raise ValueError("Session duration must be positive.")

    if session_hours > daily_available_hours:
        raise ValueError(
            "Session duration cannot exceed daily available hours."
        )

    names = [topic.name.strip().lower() for topic in topics]
    if any(not name for name in names):
        raise ValueError("Topic names cannot be empty.")

    if len(names) != len(set(names)):
        raise ValueError("Topic names must be unique.")

    for topic in topics:
        if topic.exam_date < start_date:
            raise ValueError(
                f"Exam date for '{topic.name}' is before the start date."
            )

        if not 1 <= topic.difficulty <= 5:
            raise ValueError("Difficulty must be between 1 and 5.")

        if not 1 <= topic.confidence <= 5:
            raise ValueError("Confidence must be between 1 and 5.")

        if topic.estimated_hours <= 0:
            raise ValueError("Estimated study hours must be positive.")


def calculate_priority(topic: Topic, current_date: date) -> float:
    """Return a score from 0 to 1; higher means greater priority."""
    days_left = (topic.exam_date - current_date).days

    urgency = 1 / (days_left + 1)
    weakness = (5 - topic.confidence) / 4
    difficulty = (topic.difficulty - 1) / 4

    return (
        0.50 * urgency
        + 0.30 * weakness
        + 0.20 * difficulty
    )


def generate_schedule(
    topics: list[Topic],
    start_date: date,
    daily_available_hours: float,
    session_hours: float = 1.0,
) -> ScheduleResult:
    """Allocate study hours without exceeding daily capacity."""
    validate_inputs(
        topics, start_date, daily_available_hours, session_hours
    )

    remaining = {topic.name: topic.estimated_hours for topic in topics}
    topic_by_name = {topic.name: topic for topic in topics}
    sessions: list[StudySession] = []

    last_exam = max(topic.exam_date for topic in topics)
    current_date = start_date

    while current_date <= last_exam:
        capacity = daily_available_hours

        while capacity > 1e-9:
            eligible = [
                topic_by_name[name]
                for name, hours in remaining.items()
                if hours > 1e-9 and topic_by_name[name].exam_date >= current_date
            ]

            if not eligible:
                break

            # Protect earlier deadlines first. Break ties by priority score.
            eligible.sort(
                key=lambda topic: (
                    topic.exam_date,
                    -calculate_priority(topic, current_date),
                    topic.name,
                )
            )

            topic = eligible[0]
            duration = min(
                session_hours,
                remaining[topic.name],
                capacity,
            )

            sessions.append(
                StudySession(
                    date=current_date,
                    topic=topic.name,
                    duration_hours=duration,
                    priority_score=calculate_priority(topic, current_date),
                )
            )

            remaining[topic.name] -= duration
            capacity -= duration

        current_date += timedelta(days=1)

    unscheduled = {
        name: round(hours, 2)
        for name, hours in remaining.items()
        if hours > 1e-9
    }

    return ScheduleResult(
        sessions=sessions,
        unscheduled_hours=unscheduled,
    )
