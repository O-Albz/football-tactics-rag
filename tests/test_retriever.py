import pytest
from src.retriever import retrieve

def test_retrieve_returns_results():
    results = retrieve("What is gegenpressing?")
    assert len(results) > 0

def test_retrieve_has_correct_keys():
    results = retrieve("tiki-taka")
    for r in results:
        assert "text" in r
        assert "source" in r
        assert "score" in r

def test_retrieve_scores_between_zero_and_one():
    results = retrieve("pressing in football")
    for r in results:
        assert 0 <= r["score"] <= 1

def test_retrieve_top_k_respected():
    results = retrieve("formations", top_k=3)
    assert len(results) == 3