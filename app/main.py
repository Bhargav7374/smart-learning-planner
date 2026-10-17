
from datetime import date
from sqlalchemy.orm import Session
from app.database import engine
from app.models import Base, StudyTopic , Exam
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.scheduler import Topic, generate_schedule

app = FastAPI(
    title="Smart Learning Planner AI",
    description="API for generating personalized study schedules.",
    version="0.1.0",
)

Base.metadata.create_all(bind=engine)

class TopicInput(BaseModel):
    name: str = Field(min_length=1)
    exam_date: date
    difficulty: int = Field(ge=1, le=5)
    confidence: int = Field(ge=1, le=5)
    estimated_hours: float = Field(gt=0)


class PlanRequest(BaseModel):
    start_date: date
    daily_available_hours: float = Field(gt=0, le=24)
    session_hours: float = Field(default=1.0, gt=0)
    topics: list[TopicInput] = Field(min_length=1)

@app.get("/")
def home():
    return {
        "message": "Welcome to Smart Learning Planner AI",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
def health_check():
    return {"status": "ok", "project": "Smart Learning Planner AI"}


@app.post("/plans/generate")
def create_study_plan(request: PlanRequest):
    try:
        topics = [
            Topic(
                name=topic.name.strip(),
                exam_date=topic.exam_date,
                difficulty=topic.difficulty,
                confidence=topic.confidence,
                estimated_hours=topic.estimated_hours,
            )
            for topic in request.topics
        ]

        result = generate_schedule(
            topics=topics,
            start_date=request.start_date,
            daily_available_hours=request.daily_available_hours,
            session_hours=request.session_hours,
        )

        return {
            "sessions": [
                {
                    "date": session.date.isoformat(),
                    "topic": session.topic,
                    "duration_hours": session.duration_hours,
                    "priority_score": round(session.priority_score, 3),
                }
                for session in result.sessions
            ],
            "unscheduled_hours": result.unscheduled_hours,
        }

    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

@app.get("/topics")
def get_topics():
    with Session(engine) as session:
        topics = session.query(StudyTopic).order_by(
            StudyTopic.id
        ).all()

        return [
            {
                "id": topic.id,
                "name": topic.name,
                "exam_date": topic.exam_date.isoformat(),
                "difficulty": topic.difficulty,
                "confidence": topic.confidence,
                "estimated_hours": topic.estimated_hours,
            }
            for topic in topics
        ]


@app.post("/topics", status_code=201)
def create_topic(topic: TopicInput):
    with Session(engine) as session:
        new_topic = StudyTopic(
            name=topic.name.strip(),
            exam_date=topic.exam_date,
            difficulty=topic.difficulty,
            confidence=topic.confidence,
            estimated_hours=topic.estimated_hours,
        )

        session.add(new_topic)
        session.commit()
        session.refresh(new_topic)

        return {
            "id": new_topic.id,
            "name": new_topic.name,
            "exam_date": new_topic.exam_date.isoformat(),
            "difficulty": new_topic.difficulty,
            "confidence": new_topic.confidence,
            "estimated_hours": new_topic.estimated_hours,
        }


@app.post("/plans/generate-from-saved")
def generate_plan_from_saved_topics(
    start_date: date,
    daily_available_hours: float = 2.0,
    session_hours: float = 1.0,
):
    with Session(engine) as session:
        saved_topics = session.query(StudyTopic).order_by(
            StudyTopic.exam_date,
            StudyTopic.id,
        ).all()

        if not saved_topics:
            raise HTTPException(
                status_code=404,
                detail="No saved topics found. Add topics first.",
            )

        topics = [
            Topic(
                name=topic.name,
                exam_date=topic.exam_date,
                difficulty=topic.difficulty,
                confidence=topic.confidence,
                estimated_hours=topic.estimated_hours,
            )
            for topic in saved_topics
        ]

        try:
            result = generate_schedule(
                topics=topics,
                start_date=start_date,
                daily_available_hours=daily_available_hours,
                session_hours=session_hours,
            )
        except ValueError as error:
            raise HTTPException(
                status_code=422,
                detail=str(error),
            ) from error

        return {
            "sessions": [
                {
                    "date": item.date.isoformat(),
                    "topic": item.topic,
                    "duration_hours": item.duration_hours,
                    "priority_score": round(item.priority_score, 3),
                }
                for item in result.sessions
            ],
            "unscheduled_hours": result.unscheduled_hours,
        }
