# Football Tactics RAG

A retrieval-augmented generation (RAG) system for querying football tactics, formations, and manager philosophies. Ask questions in natural language and get answers grounded in real tactical documents.

## Architecture

```
Documents (Wikipedia + StatsBomb)
        ↓
Chunking (SentenceSplitter, 512 tokens)
        ↓
Embeddings (OpenAI text-embedding-3-small)
        ↓
Vector Storage (Qdrant)
        ↓
FastAPI → Retrieval → Generation (GPT-4o-mini)
```

## Tech Stack

- **FastAPI** — REST API with auto-generated OpenAPI docs
- **Qdrant** — vector database with HNSW indexing
- **LlamaIndex** — document loading and chunking
- **OpenAI** — embeddings and generation
- **Docker** — containerized deployment
- **pytest + GitHub Actions** — testing and CI/CD

## Data Sources

- Wikipedia articles on tactics, formations, and managers (~44 documents)
- StatsBomb blog archive — tactical analysis articles (~14 documents)
- Total: ~58 documents, ~950 chunks

## Getting Started

### Prerequisites

- Docker
- OpenAI API key

### Run with Docker

```bash
git clone https://github.com/yourusername/football-tactics-rag
cd football-tactics-rag
echo "OPENAI_API_KEY=your_key_here" > .env
docker-compose up
```

API available at `http://localhost:8000`  
Interactive docs at `http://localhost:8000/docs`

### Run locally

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
echo "OPENAI_API_KEY=your_key_here" > .env

# Ingest documents
python src/ingest.py

# Start API
uvicorn src.app:app --reload
```

### Re-ingest documents

```bash
# Fetch Wikipedia articles (uncomment fetch_wikipedia_articles() in ingest.py first)
python src/ingest.py

# Scrape StatsBomb articles
python src/scrape_guardian.py
```

## API Endpoints

### POST /answer

Ask a tactical question.

**Request:**
```json
{
  "question": "How does gegenpressing work?",
  "top_k": 5
}
```

**Response:**
```json
{
  "question": "How does gegenpressing work?",
  "answer": "Gegenpressing is a high-intensity pressing system...",
  "sources": ["gegenpressing.md", "statsbomb_lets-talk-about-press-baybee.md"],
  "chunks_used": 5
}
```

### GET /health

Returns service health status.

```json
{"status": "ok"}
```

## Example Questions

- *"How does tiki-taka differ from gegenpressing?"*
- *"What tactical innovations did Arrigo Sacchi bring to AC Milan?"*
- *"Explain the false 9 role and who popularized it"*
- *"How has the 4-3-3 formation evolved over time?"*
- *"What is the difference between zonal and man-to-man marking?"*

## Running Tests

```bash
python -m pytest tests/ -v
```

## Known Limitations

- Multi-topic queries tend to retrieve chunks from one dominant source — a reranker would improve retrieval diversity
- StatsBomb articles have minor encoding issues with special characters from the scraper
- No authentication on API endpoints