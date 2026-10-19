
import importlib.util
from pathlib import Path

from fastapi.testclient import TestClient


# Load Task 1 directly to avoid conflicts with other app/main.py files.
TASK1_DIR = Path(__file__).resolve().parents[1]
MAIN_FILE = TASK1_DIR / "app" / "main.py"

spec = importlib.util.spec_from_file_location(
    "task1_main_module",
    MAIN_FILE,
)
task1_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(task1_module)

app = task1_module.app
client = TestClient(app)


def test_home():
    response = client.get("/")

    assert response.status_code == 200
    assert "Knowledge Brain is running" in response.json()["message"]


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["mode"] == "free"


def test_ask_relevant_question():
    response = client.post(
        "/ask",
        json={
            "question": "How do I customize colors and fonts on my website?"
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert "answer" in data
    assert "sources" in data
    assert "needs_human" in data

    if data["sources"]:
        source = data["sources"][0]
        assert "title" in source
        assert "url" in source
        assert "evidence" in source


def test_ask_unrelated_question():
    response = client.post(
        "/ask",
        json={
            "question": "How do I play FIFA football?"
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["needs_human"] is True
    assert data["sources"] == []


def test_ask_empty_question():
    response = client.post(
        "/ask",
        json={"question": ""},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["answer"] == "Please enter a question."
    assert data["sources"] == []
    assert data["needs_human"] is False
