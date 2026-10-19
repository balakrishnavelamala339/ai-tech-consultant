
import importlib.util
from pathlib import Path

from fastapi.testclient import TestClient

TASK3_DIR = Path(__file__).resolve().parents[1]
MAIN_FILE = TASK3_DIR / "app" / "main.py"

# Load Task 3's main.py directly, avoiding Task 2's app module.
spec = importlib.util.spec_from_file_location(
    "task3_main_module",
    MAIN_FILE,
)
task3_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(task3_module)

app = task3_module.app
client = TestClient(app)


def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == (
        "Meeting to Scope is running in free mode."
    )


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_analyze_meeting():
    response = client.post(
        "/analyze",
        json={
            "customer_name": "Test Customer",
            "meeting_notes": (
                "Build a website with login and a contact form.\n"
                "The deadline is next month."
            ),
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["customer_name"] == "Test Customer"
    assert len(data["requirements"]) > 0
    assert data["status"] == "pending_human_approval"
    assert data["scope_id"]
    assert data["estimated_total_hours"] > 0
    assert "proposal" in data


def test_invalid_meeting():
    response = client.post(
        "/analyze",
        json={
            "customer_name": "Test Customer",
            "meeting_notes": "Short",
        },
    )
    assert response.status_code == 422


def test_missing_customer_name():
    response = client.post(
        "/analyze",
        json={
            "meeting_notes": "Build a website with login and a contact form.",
        },
    )
    assert response.status_code == 422


def test_list_scopes():
    response = client.get("/scopes")
    assert response.status_code == 200
    assert "scopes" in response.json()


def test_scope_approval():
    create_response = client.post(
        "/analyze",
        json={
            "customer_name": "Approval Test Customer",
            "meeting_notes": "Build a website with login and a contact form.",
        },
    )
    assert create_response.status_code == 200

    scope_id = create_response.json()["scope_id"]

    response = client.post(
        f"/scopes/{scope_id}/review",
        json={"action": "approve"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "approved"


def test_scope_rejection():
    create_response = client.post(
        "/analyze",
        json={
            "customer_name": "Rejection Test Customer",
            "meeting_notes": "Build a website with login and a contact form.",
        },
    )
    assert create_response.status_code == 200

    scope_id = create_response.json()["scope_id"]

    response = client.post(
        f"/scopes/{scope_id}/review",
        json={"action": "reject"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "rejected"
