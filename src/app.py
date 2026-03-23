from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import time
from src.generator import generate
from src.logger import log_query

load_dotenv()

app = FastAPI(
    title="Football Tactics RAG",
    description="Ask about football tactics and get answers based on a RAG system.",
    version="1.0.0"
)

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
def answer(request: QuestionRequest):
    start = time.time()
    try:
        result = generate(request.question, top_k=request.top_k)
        latency_ms = (time.time() - start) * 1000

        log_query(
            question=request.question,
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
            question=request.question,
            answer=None,
            sources=[],
            latency_ms=latency_ms,
            chunks_used=0,
            success=False,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))