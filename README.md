# Smart Learning Planner AI

🚀 **Live Demo:** [Open Smart Learning Planner](https://smart-learning-planner-ai.streamlit.app)

**An adaptive study-planning application built to help students organise their preparation, prioritise subjects, and plan study sessions around exam deadlines.**

Smart Learning Planner AI combines a rule-based scheduling engine with a web interface and a PostgreSQL database. Students can manage their subjects, track confidence and difficulty, and generate study schedules based on their available time.

---

## Overview

Preparing for multiple exams can make it difficult to decide what to study first and how to allocate time effectively. Smart Learning Planner AI addresses this problem by organising study topics according to exam deadlines, topic difficulty, and confidence levels.

The project is being developed as a modular application with a Python scheduling engine, FastAPI endpoints, PostgreSQL persistence, and a Streamlit interface.

## Features

### Study Planning
- Exam-deadline-aware scheduling
- Topic prioritisation using difficulty and confidence
- Configurable daily study-hour limits
- Customisable study-session duration
- Reporting of study hours that could not be scheduled
- Downloadable study schedules in CSV format

### Subject Management
- Add and save study subjects
- Store exam dates, difficulty, confidence, and estimated study hours
- Automatically display the day of the week for each exam date
- Delete subjects with confirmation
- Persist subject data in PostgreSQL

### Application Interface
- Professional, responsive-style Streamlit layout
- Overview dashboard with upcoming exams and study priorities
- Dedicated subject-management and study-schedule pages

### Backend and Testing
- FastAPI endpoints for health checks, topic management, and schedule generation
- PostgreSQL database integration using SQLAlchemy
- Automated scheduling tests using pytest

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application logic and scheduling engine |
| Streamlit | Interactive web interface |
| FastAPI | REST API |
| PostgreSQL | Persistent data storage |
| SQLAlchemy | Database access and ORM |
| pytest | Automated testing |
| Git and GitHub | Version control and project hosting |

## Application Architecture

```text
                 Student
                    |
                    v
            Streamlit Interface
              (app/ui.py)
                    |
          +---------+---------+
          |                   |
          v                   v
   Subject Management   Study Scheduler
          |                   |
          +---------+---------+
                    |
                    v
              PostgreSQL
             (SQLAlchemy)

        FastAPI REST API
             (app/main.py)
```

The scheduling engine is kept separate from the interface so that planning logic can be tested and improved independently.

## Project Structure

```text
smart-learning-planner/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── scheduler.py
│   └── ui.py
├── tests/
│   ├── __init__.py
│   └── test_scheduler.py
├── .streamlit/
│   └── config.toml
├── .gitignore
├── README.md
└── requirements.txt
```

## Getting Started

### Prerequisites

- Python installed on your system
- PostgreSQL installed and running
- Git
- A terminal and code editor

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd smart-learning-planner
```

Replace the placeholder with your actual GitHub repository URL.

### 2. Create and activate a virtual environment

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows**

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure PostgreSQL

Create a PostgreSQL database and a dedicated database user. Configure the connection in a local `.env` file in the project root:

```dotenv
DATABASE_URL=postgresql+psycopg://YOUR_USER:YOUR_PASSWORD@localhost:5432/YOUR_DATABASE
```

Replace the placeholders with your local database credentials. Do not commit `.env` or expose database passwords.

### 5. Start the Streamlit application

```bash
python -m streamlit run app/ui.py
```

Open the local URL displayed in the terminal, usually:

`http://localhost:8501`

### 6. Start the FastAPI service

In a separate terminal, with the virtual environment activated:

```bash
python -m uvicorn app.main:app --reload
```

Interactive API documentation is available at:

`http://127.0.0.1:8000/docs`

## Running Tests

Run the automated scheduling tests with:

```bash
python -m pytest -v
```

The current scheduler test suite contains eight tests covering schedule generation, daily study-hour limits, exam-deadline prioritisation, unallocated hours, input validation, and duplicate topic names.

## Current Status

**Implemented**
- Core scheduling engine and automated tests
- FastAPI service
- PostgreSQL connection and subject persistence
- Streamlit interface
- Subject creation and deletion
- Exam-day display and schedule export

**Planned improvements**
- Adaptive replanning based on completed or missed sessions
- Quiz-based progress tracking
- Weekly learning analytics
- AI-assisted explanations and practice questions
- Study streaks and revision recommendations

These improvements will be introduced and tested incrementally.

## Design Principles

- Keep scheduling logic deterministic and testable.
- Use stored data rather than fabricated progress metrics.
- Separate the interface, API, database, and planning logic.
- Protect credentials and configuration secrets.
- Validate scheduling behaviour with automated tests.

## Contributing

This is an evolving portfolio project. Suggestions, issue reports, and constructive feedback are welcome.

## License

A license has not yet been selected. Add a `LICENSE` file before distributing the project under an open-source license.
