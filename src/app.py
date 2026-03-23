from fastapi import FastAPI, HTTPException, Depends, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from src.auth import verify_api_key
from pydantic import BaseModel
from dotenv import load_dotenv
from collections import Counter
from pathlib import Path
import time
import json
from src.generator import generate
from src.logger import log_query
from src.cache import get_cached, set_cached
from src.validator import is_football_tactics_question


load_dotenv()

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(
    title="Football Tactics RAG",
    description="Ask about football tactics and get answers based on a RAG system.",
    version="1.0.0"
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


class QuestionRequest(BaseModel):
    question: str
    top_k: int = 5


class AnswerResponse(BaseModel):
    question: str
    answer: str
    sources: list[str]
    chunks_used: int
    latency_ms: float


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/answer", response_model=AnswerResponse)
@limiter.limit("60/minute")
def answer(request: Request, body: QuestionRequest, api_key: str = Depends(verify_api_key)):
    start = time.time()

    # Validate question is football tactics related
    if not is_football_tactics_question(body.question):
        raise HTTPException(
            status_code=400,
            detail="This service only answers questions about football tactics, formations, and managers."
        )

    # Check cache
    cached = get_cached(body.question, body.top_k)
    if cached:
        latency_ms = (time.time() - start) * 1000
        log_query(
            question=body.question,
            answer=cached["answer"],
            sources=cached["sources"],
            latency_ms=latency_ms,
            chunks_used=cached["chunks_used"],
            success=True
        )
        return AnswerResponse(
            **cached,
            latency_ms=round(latency_ms, 2)
        )

    try:
        result = generate(body.question, top_k=body.top_k)
        latency_ms = (time.time() - start) * 1000

        # Store in cache
        set_cached(body.question, body.top_k, {
            "question": result["question"],
            "answer": result["answer"],
            "sources": list(dict.fromkeys(result["sources"])),
            "chunks_used": result["chunks_used"]
        })

        log_query(
            question=body.question,
            answer=result["answer"],
            sources=result["sources"],
            latency_ms=latency_ms,
            chunks_used=result["chunks_used"],
            success=True
        )

        return AnswerResponse(
            question=result["question"],
            answer=result["answer"],
            sources=list(dict.fromkeys(result["sources"])),
            chunks_used=result["chunks_used"],
            latency_ms=round(latency_ms, 2)
        )

    except Exception as e:
        latency_ms = (time.time() - start) * 1000
        log_query(
            question=body.question,
            answer=None,
            sources=[],
            latency_ms=latency_ms,
            chunks_used=0,
            success=False,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))
    
    
@app.get("/stats")
def stats():
    log_path = Path("logs/queries.jsonl")
    if not log_path.exists():
        return {"total_queries": 0}

    entries = []
    with open(log_path) as f:
        for line in f:
            try:
                entries.append(json.loads(line))
            except Exception:
                continue

    if not entries:
        return {"total_queries": 0}

    successful = [e for e in entries if e["success"]]
    failed = [e for e in entries if not e["success"]]
    latencies = [e["latency_ms"] for e in successful]

    return {
        "total_queries": len(entries),
        "successful_queries": len(successful),
        "failed_queries": len(failed),
        "avg_latency_ms": round(sum(latencies) / len(latencies), 2) if latencies else 0,
        "max_latency_ms": round(max(latencies), 2) if latencies else 0,
        "min_latency_ms": round(min(latencies), 2) if latencies else 0,
        "most_common_sources": _top_sources(successful)
    }


def _top_sources(entries: list) -> list:
    all_sources = [s for e in entries for s in e["sources"]]
    return [
        {"source": s, "count": c}
        for s, c in Counter(all_sources).most_common(5)
    ]