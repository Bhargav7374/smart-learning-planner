
# Smart Learning Planner AI

An adaptive study-planning application that helps students prioritize
topics, schedule study sessions, and prepare for exams.

## Current features

- Topic priority calculation
- Exam-deadline-aware scheduling
- Daily study-hour limits
- Difficulty and confidence tracking
- Reporting of study hours that cannot fit
- Automated tests using pytest

## Tech stack

- Python
- pytest
- Planned: FastAPI, PostgreSQL, Streamlit and an LLM API

## Run locally

Create and activate a virtual environment, then install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Run the tests:

```bash
python -m pytest -v
```

## Project status

Phase 1: Core scheduling engine and automated tests.
