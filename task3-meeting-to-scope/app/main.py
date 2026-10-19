
from uuid import uuid4

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="AI Tech Consultant - Meeting to Scope")

# Demo storage: data is lost when the server restarts.
scope_records = {}

KNOWLEDGE_API = "http://127.0.0.1:8000/ask"


class MeetingRequest(BaseModel):
    customer_name: str = Field(min_length=1)
    meeting_notes: str = Field(min_length=10)


class ApprovalRequest(BaseModel):
    action: str
    edited_scope: str | None = None


@app.get("/")
def home():
    return {"message": "Meeting to Scope is running in free mode."}


@app.get("/health")
def health():
    return {"status": "healthy", "mode": "free"}


@app.post("/analyze")
def analyze_meeting(request: MeetingRequest):
    notes = request.meeting_notes.strip()

    if not notes:
        raise HTTPException(status_code=400, detail="Meeting notes cannot be empty")

    # Simple demo extraction. This is not an LLM-generated summary.
    lines = [
        line.strip("- •\t ")
        for line in notes.splitlines()
        if line.strip("- •\t ")
    ]

    requirements = lines[:10]

    # Look for missing information.
    lower_notes = notes.lower()
    questions = []

    if not any(word in lower_notes for word in ["budget", "$", "₹"]):
        questions.append("What is the project budget?")

    if not any(word in lower_notes for word in ["deadline", "due date", "by " ]):
        questions.append("What is the target deadline?")

    if not any(word in lower_notes for word in ["login", "sign in", "account"]):
        questions.append("Does the project need user login or accounts?")

    # Check the Task 1 Knowledge Brain API.
    knowledge_check = {
        "status": "unavailable",
        "message": "Knowledge Brain was not reachable.",
        "sources": [],
        "needs_human": True
    }

    try:
        response = httpx.post(
            KNOWLEDGE_API,
            json={"question": "How do I customize colors and fonts on my website?"},
            timeout=10.0
        )
        response.raise_for_status()
        knowledge_check = response.json()
    except (httpx.HTTPError, ValueError):
        pass

    tasks = [
        {
            "task": requirement,
            "estimated_hours": 4,
            "estimate_type": "rough placeholder; confirm with a developer"
        }
        for requirement in requirements
    ]

    total_hours = sum(task["estimated_hours"] for task in tasks)

    record_id = str(uuid4())
    scope_records[record_id] = {
        "customer_name": request.customer_name.strip(),
        "requirements": requirements,
        "tasks": tasks,
        "estimated_total_hours": total_hours,
        "open_questions": questions,
        "out_of_scope": [],
        "knowledge_check": knowledge_check,
        "status": "pending_human_approval",
        "approved_scope": None
    }

    return {
        "scope_id": record_id,
        **scope_records[record_id],
        "proposal": (
            f"Draft proposal for {request.customer_name.strip()}: "
            f"{len(requirements)} requirements recorded, with a preliminary "
            f"placeholder estimate of {total_hours} hours. "
            "Confirm requirements, feature availability, and estimates before quoting."
        )
    }


@app.get("/scopes")
def list_scopes():
    return {"scopes": [
        {"scope_id": scope_id, **record}
        for scope_id, record in scope_records.items()
    ]}


@app.post("/scopes/{scope_id}/review")
def review_scope(scope_id: str, request: ApprovalRequest):
    record = scope_records.get(scope_id)

    if record is None:
        raise HTTPException(status_code=404, detail="Scope not found")

    if record["status"] != "pending_human_approval":
        raise HTTPException(status_code=409, detail="Scope has already been reviewed")

    action = request.action.strip().lower()

    if action == "edit":
        if not request.edited_scope or not request.edited_scope.strip():
            raise HTTPException(status_code=400, detail="Please provide the edited scope")

        record["approved_scope"] = request.edited_scope.strip()
        return {
            "scope_id": scope_id,
            "status": "pending_human_approval",
            "approved_scope": record["approved_scope"],
            "message": "Scope updated; human approval is still required."
        }

    if action == "approve":
        record["status"] = "approved"
        record["approved_scope"] = (
            record["approved_scope"]
            or "\n".join(record["requirements"])
        )
        return {
            "scope_id": scope_id,
            "status": "approved",
            "approved_scope": record["approved_scope"],
            "message": "Scope approved by the reviewer."
        }

    if action == "reject":
        record["status"] = "rejected"
        return {
            "scope_id": scope_id,
            "status": "rejected",
            "message": "Scope rejected by the reviewer."
        }

    raise HTTPException(
        status_code=400,
        detail="Action must be approve, edit, or reject"
    )
