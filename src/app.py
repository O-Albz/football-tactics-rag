from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

from src.generator import generate

load_dotenv()

app = FastAPI(
    title = "Football Tactics RAG",
    description = "Ask about football tactics and get answers based on a RAG system.",
    version = "1.0.0"
)

class QuesitionRequest(BaseModel):
    question: str
    top_k: int = 5
    
class AnswerResponse(BaseModel):
    question: str
    answer: str
    sources: list[str]
    chunks_used: int
    
@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/answer", response_model=AnswerResponse)
def answer(request: QuesitionRequest):
    result = generate(request.question, request.top_k)
    return AnswerResponse(
        question = result["question"],
        answer = result["answer"],
        sources = result["sources"],
        chunks_used = result["chunks_used"]
    )

