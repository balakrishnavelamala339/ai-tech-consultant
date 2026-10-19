# AI Tech Consultant

## Overview

AI Tech Consultant is a three-part support automation project designed to answer customer questions, prepare email replies for human review, and convert meeting notes into project scopes and task estimates.

## Tasks

- **Task 1 – Knowledge Brain:** Crawls support documentation, indexes articles using embeddings and ChromaDB, retrieves relevant evidence, provides source links, and escalates questions when sufficient evidence is unavailable.
- **Task 2 – Inbox Agent:** Classifies customer emails, checks the Knowledge Brain API, prepares reply drafts, and supports human editing, approval, or rejection. It does not send emails automatically.
- **Task 3 – Meeting to Scope:** Processes customer meeting notes, identifies requirements and missing information, creates preliminary tasks and estimates, and supports human review.

## Technology Stack

Python, FastAPI, Pydantic, ChromaDB, Sentence Transformers, HTTPX, pytest, and a local embedding model.

## Project Structure

- `task1-knowledge-brain/` – Documentation ingestion, retrieval, API, and tests.
- `task2-inbox-agent/` – Email classification, reply drafts, review workflow, and tests.
- `task3-meeting-to-scope/` – Meeting analysis, scope drafts, approval workflow, and tests.
- `evaluations/` – Evaluation data and results.
- `DESIGN.md` – System architecture and design decisions.
- `EVALS.md` – Evaluation methodology and findings.
- `AI_LOG.md` – AI-assisted development log.

## Setup

1. Install Python and Git.
2. Open a terminal in the project root.
3. Create and activate a virtual environment if needed.
4. Install dependencies using the project's requirements files.
5. Start the APIs using the commands below.

## Run the APIs

Run each command in a separate terminal from the project root.

**Task 1 – Knowledge Brain**
```bash
python -m uvicorn app.main:app --reload --port 8000 --app-dir task1-knowledge-brain
```

**Task 2 – Inbox Agent**
```bash
python -m uvicorn app.main:app --reload --port 8001 --app-dir task2-inbox-agent
```

**Task 3 – Meeting to Scope**
```bash
python -m uvicorn app.main:app --reload --port 8002 --app-dir task3-meeting-to-scope
```

Start Task 1 before Task 2 and Task 3.

### Interactive API Documentation

- Task 1: http://127.0.0.1:8000/docs
- Task 2: http://127.0.0.1:8001/docs
- Task 3: http://127.0.0.1:8002/docs

## Run Tests

From the project root, run:

```bash
python -m pytest -v
```

**Latest local test result:** 23 tests passed.

## Limitations

The current implementation uses local retrieval, keyword-based email classification, fixed reply templates, and preliminary scope estimates. It does not send emails automatically or guarantee accurate project estimates. Any AI model comparisons should be reported only after they have been measured.

## Human Review and Safety

Email drafts and project scopes require human review. Questions without sufficient supporting evidence should be escalated instead of answered with unsupported instructions. Keep API keys in environment variables and never commit secrets to Git.