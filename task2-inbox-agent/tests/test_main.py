
import sys
from pathlib import Path

from fastapi.testclient import TestClient

# Add Task 2 folder to Python's import path.
TASK2_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TASK2_DIR))

from app.main import app

client = TestClient(app)


def test_home():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == (
        "Inbox Agent is running in free mode."
    )


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_billing_classification():
    response = client.post(
        "/classify",
        json={
            "subject": "Payment refund request",
            "body": "I was charged twice. Please help me get a refund.",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "billing"
    assert data["status"] == "pending_human_approval"
    assert data["auto_send"] is False


def test_technical_support_classification():
    response = client.post(
        "/classify",
        json={
            "subject": "Login error",
            "body": "I cannot log in. The website shows an error.",
        },
    )

    assert response.status_code == 200
    assert response.json()["category"] == "technical_support"


def test_list_drafts():
    response = client.get("/drafts")

    assert response.status_code == 200
    assert "drafts" in response.json()


def test_approve_draft():
    create_response = client.post(
        "/classify",
        json={
            "subject": "Billing question",
            "body": "I have a question about my invoice.",
        },
    )

    assert create_response.status_code == 200
    draft_id = create_response.json()["draft_id"]

    review_response = client.post(
        f"/drafts/{draft_id}/review",
        json={"action": "approve"},
    )

    assert review_response.status_code == 200
    data = review_response.json()
    assert data["status"] == "approved"
    assert data["auto_send"] is False


def test_reject_draft():
    create_response = client.post(
        "/classify",
        json={
            "subject": "New feature",
            "body": "Please add a new feature to the website.",
        },
    )

    draft_id = create_response.json()["draft_id"]

    review_response = client.post(
        f"/drafts/{draft_id}/review",
        json={"action": "reject"},
    )

    assert review_response.status_code == 200
    assert review_response.json()["status"] == "rejected"


def test_edit_draft():
    create_response = client.post(
        "/classify",
        json={
            "subject": "Login issue",
            "body": "I cannot log in to my account.",
        },
    )

    draft_id = create_response.json()["draft_id"]
    edited_text = "Please share the exact login error message."

    review_response = client.post(
        f"/drafts/{draft_id}/review",
        json={
            "action": "edit",
            "edited_reply": edited_text,
        },
    )

    assert review_response.status_code == 200
    assert review_response.json()["draft_reply"] == edited_text
    assert review_response.json()["status"] == "pending_human_approval"


def test_invalid_review_action():
    create_response = client.post(
        "/classify",
        json={
            "subject": "General question",
            "body": "I have a question for your support team.",
        },
    )

    draft_id = create_response.json()["draft_id"]

    response = client.post(
        f"/drafts/{draft_id}/review",
        json={"action": "send"},
    )

    assert response.status_code == 400

def test_website_design_classification():
    response = client.post(
        "/classify",
        json={
            "subject": "How do I change website fonts?",
            "body": "I want to customize the fonts on my website.",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "website_design"
    assert data["status"] == "pending_human_approval"
    assert data["auto_send"] is False
    assert "knowledge_check" in data
