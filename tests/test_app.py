from fastapi.testclient import TestClient
from src.app import app
import json
from pathlib import Path
import time

client = TestClient(app)

VALID_KEY = "tactics-rag-secret-key-123"

def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_answer_without_api_key_returns_401():
    response = client.post("/answer", json={"question": "What is pressing?"})
    assert response.status_code == 401

def test_answer_with_wrong_api_key_returns_401():
    response = client.post(
        "/answer",
        json={"question": "What is pressing?"},
        headers={"X-API-Key": "wrong-key"}
    )
    assert response.status_code == 401

def test_answer_with_valid_api_key_returns_200():
    response = client.post(
        "/answer",
        json={"question": "What is gegenpressing?"},
        headers={"X-API-Key": VALID_KEY}
    )
    assert response.status_code == 200

def test_answer_returns_correct_fields():
    response = client.post(
        "/answer",
        json={"question": "What is tiki-taka?"},
        headers={"X-API-Key": VALID_KEY}
    )
    data = response.json()
    assert "answer" in data
    assert "sources" in data
    assert "latency_ms" in data
    assert "chunks_used" in data
    assert data["latency_ms"] > 0

def test_answer_logs_query():
    log_path = Path("logs/queries.jsonl")
    initial_count = 0
    if log_path.exists():
        with open(log_path) as f:
            initial_count = sum(1 for line in f if line.strip())

    client.post(
        "/answer",
        json={"question": "What is catenaccio?"},
        headers={"X-API-Key": VALID_KEY}
    )

    with open(log_path) as f:
        new_count = sum(1 for line in f if line.strip())

    assert new_count == initial_count + 1

def test_answer_log_has_correct_structure():
    client.post(
        "/answer",
        json={"question": "Explain the offside trap"},
        headers={"X-API-Key": VALID_KEY}
    )

    log_path = Path("logs/queries.jsonl")
    with open(log_path) as f:
        lines = [l for l in f if l.strip()]
        last_entry = json.loads(lines[-1])

    assert "timestamp" in last_entry
    assert "question" in last_entry
    assert "latency_ms" in last_entry
    assert "sources" in last_entry
    assert "success" in last_entry
    assert last_entry["success"] is True

def test_stats_endpoint_returns_data():
    response = client.get("/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_queries" in data
    assert data["total_queries"] >= 0
    
    
def test_non_football_question_returns_400():
    response = client.post(
        "/answer",
        json={"question": "What is the capital of France?"},
        headers={"X-API-Key": VALID_KEY}
    )
    assert response.status_code == 400
    assert "football tactics" in response.json()["detail"].lower()

def test_non_football_question_recipe_returns_400():
    response = client.post(
        "/answer",
        json={"question": "How do I make pasta carbonara?"},
        headers={"X-API-Key": VALID_KEY}
    )
    assert response.status_code == 400

def test_cached_response_is_faster():
    question = "What is the offside trap?"

    start1 = time.time()
    client.post("/answer", json={"question": question}, headers={"X-API-Key": VALID_KEY})
    first_latency = time.time() - start1

    start2 = time.time()
    client.post("/answer", json={"question": question}, headers={"X-API-Key": VALID_KEY})
    second_latency = time.time() - start2

    assert second_latency < first_latency

def test_cached_response_same_answer():
    question = "What is zonal marking?"

    r1 = client.post("/answer", json={"question": question}, headers={"X-API-Key": VALID_KEY})
    r2 = client.post("/answer", json={"question": question}, headers={"X-API-Key": VALID_KEY})

    assert r1.json()["answer"] == r2.json()["answer"]