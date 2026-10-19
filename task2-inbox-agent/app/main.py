
from uuid import uuid4

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="AI Tech Consultant - Inbox Agent")

# Demo storage: drafts are kept only while the server is running.
drafts = {}

KNOWLEDGE_BRAIN_URL = "http://127.0.0.1:8000/ask"


class EmailRequest(BaseModel):
    subject: str = Field(min_length=1)
    body: str = Field(min_length=1)


class ReviewRequest(BaseModel):
    action: str
    edited_reply: str | None = None


def check_knowledge_brain(subject: str, body: str) -> dict:
    """Retrieve potentially relevant evidence from Task 1."""
    question = (
        f"Customer issue: {subject}\n{body}\n"
        "Find support documentation relevant to this issue."
    )

    try:
        response = httpx.post(
            KNOWLEDGE_BRAIN_URL,
            json={"question": question},
            timeout=10.0,
        )
        response.raise_for_status()
        data = response.json()

        return {
            "status": (
                "needs_human"
                if data.get("needs_human", True)
                else "evidence_found"
            ),
            "answer": data.get("answer", ""),
            "sources": data.get("sources", []),
            "needs_human": data.get("needs_human", True),
        }

    except (httpx.HTTPError, ValueError):
        return {
            "status": "unavailable",
            "answer": (
                "The Knowledge Brain is unavailable. "
                "Please verify the issue manually."
            ),
            "sources": [],
            "needs_human": True,
        }


def classify_category(subject: str, body: str) -> str:
    """Classify customer emails using keyword matching."""
    text = f"{subject} {body}".lower()

    categories = {
        "billing": [
            "invoice", "payment", "refund", "billing",
            "charge", "charged", "price", "subscription",
        ],
        "technical_support": [
            "error", "bug", "not working", "broken",
            "issue", "login", "crash", "failed",
            "doesn't work", "does not work",
        ],
        "account": [
            "account", "password", "username",
            "sign in", "profile", "reset password",
        ],
        "feature_request": [
            "feature", "suggestion", "would like",
            "please add", "improvement", "new functionality",
        ],
        "website_design": [
            "font", "fonts", "color", "colors",
            "colour", "colours", "design", "theme",
            "website layout", "customize", "customise",
            "customization", "customisation",
            "background", "homepage", "website appearance",
        ],
    }

    matches = {
        category: sum(keyword in text for keyword in keywords)
        for category, keywords in categories.items()
    }

    best_category = max(matches, key=matches.get)

    if matches[best_category] == 0:
        return "general"

    return best_category


def create_draft_reply(category: str, knowledge_check: dict) -> str:
    """Create a safe template draft; this is not an LLM-generated reply."""
    drafts_by_category = {
        "billing": (
            "Thank you for contacting us about billing. "
            "Our team will review your request and follow up."
        ),
        "technical_support": (
            "Thank you for reporting this issue. "
            "Please share the error message and the steps to reproduce "
            "the issue so our support team can investigate."
        ),
        "account": (
            "Thank you for contacting us about your account. "
            "Our support team will help you with this request."
        ),
        "feature_request": (
            "Thank you for sharing your suggestion. "
            "We appreciate your feedback and will pass it to our team."
        ),
        "website_design": (
            "Thank you for contacting us about your website design. "
            "Our team will review your question and help you find "
            "the appropriate design settings."
        ),
        "general": (
            "Thank you for contacting us. "
            "Our support team will review your message and respond."
        ),
    }

    reply = drafts_by_category[category]

    if knowledge_check["status"] != "evidence_found":
        reply += (
            " We need to verify the relevant support documentation "
            "before confirming specific instructions."
        )

    return reply


@app.get("/")
def home():
    return {"message": "Inbox Agent is running in free mode."}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/classify")
def classify_email(email: EmailRequest):
    category = classify_category(email.subject, email.body)

    # Query Task 1 before creating the email draft.
    knowledge_check = check_knowledge_brain(
        email.subject,
        email.body,
    )

    draft_id = str(uuid4())

    drafts[draft_id] = {
        "subject": email.subject,
        "body": email.body,
        "category": category,
        "draft_reply": create_draft_reply(
            category,
            knowledge_check,
        ),
        "knowledge_check": knowledge_check,
        "status": "pending_human_approval",
    }

    return {
        "draft_id": draft_id,
        **drafts[draft_id],
        "auto_send": False,
    }


@app.get("/drafts")
def list_drafts():
    return {
        "drafts": [
            {"draft_id": draft_id, **draft}
            for draft_id, draft in drafts.items()
        ]
    }


@app.post("/drafts/{draft_id}/review")
def review_draft(draft_id: str, request: ReviewRequest):
    draft = drafts.get(draft_id)

    if draft is None:
        raise HTTPException(
            status_code=404,
            detail="Draft not found",
        )

    if draft["status"] != "pending_human_approval":
        raise HTTPException(
            status_code=409,
            detail="This draft has already been reviewed",
        )

    action = request.action.strip().lower()

    if action == "edit":
        if not request.edited_reply or not request.edited_reply.strip():
            raise HTTPException(
                status_code=400,
                detail="Please provide an edited reply",
            )

        draft["draft_reply"] = request.edited_reply.strip()

        return {
            "draft_id": draft_id,
            "status": "pending_human_approval",
            "draft_reply": draft["draft_reply"],
            "message": "Draft edited. Human approval is still required.",
        }

    if action == "approve":
        draft["status"] = "approved"

        return {
            "draft_id": draft_id,
            "status": "approved",
            "draft_reply": draft["draft_reply"],
            "auto_send": False,
            "message": "Draft approved. No email was sent.",
        }

    if action == "reject":
        draft["status"] = "rejected"

        return {
            "draft_id": draft_id,
            "status": "rejected",
            "message": "Draft rejected. No email was sent.",
        }

    raise HTTPException(
        status_code=400,
        detail="Action must be approve, edit, or reject",
    )
