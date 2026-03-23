from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_ask_returns_answer():
    response = client.post("/answer", json={"question": "What is gegenpressing?"})
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert len(data["answer"]) > 50

def test_ask_returns_sources():
    response = client.post("/answer", json={"question": "What is tiki-taka?"})
    assert response.status_code == 200
    data = response.json()
    assert "sources" in data
    assert len(data["sources"]) > 0

def test_ask_respects_top_k():
    response = client.post("/answer", json={"question": "pressing systems", "top_k": 3})
    assert response.status_code == 200
    data = response.json()
    assert data["chunks_used"] == 3