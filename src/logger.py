import json
import time
import logging
from pathlib import Path
from datetime import datetime, timezone

LOG_PATH = Path("logs/queries.jsonl")

def setup_logging():
    LOG_PATH.parent.mkdir(exist_ok=True)
    handler = logging.FileHandler(LOG_PATH)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger = logging.getLogger("rag")
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger

logger = setup_logging()

def log_query(
    question: str,
    answer: str,
    sources: list[str],
    latency_ms: float,
    chunks_used: int,
    success: bool,
    error: str = None
):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "question": question,
        "answer_length": len(answer) if answer else 0,
        "sources": sources,
        "latency_ms": round(latency_ms, 2),
        "chunks_used": chunks_used,
        "success": success,
        "error": error
    }
    logger.info(json.dumps(entry))