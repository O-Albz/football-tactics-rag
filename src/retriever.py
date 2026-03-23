from dotenv import load_dotenv
from llama_index.embeddings.openai import OpenAIEmbedding
from qdrant_client import QdrantClient
import os

load_dotenv()
    
COLLECTION_NAME = "football_tactics"
import os
QDRANT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "qdrant_db")

def get_retriever():
    # Qdrant embedded mode uses an on-disk directory; in this repo the actual
    # storage lives under `data/qdrant_db/qdrant_db/`.
    return QdrantClient(path=QDRANT_PATH)

def retrieve(query: str, top_k: int = 5) -> list[dict]:
    client = get_retriever()
    embedder = OpenAIEmbedding(model="text-embedding-3-small")

    query_embedding = embedder.get_text_embedding(query)

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        limit=top_k
    ).points
    
    print(f"Raw results count: {len(results)}")

    return [
        {
            "text": r.payload["text"],
            "source": r.payload["source"],
            "score": r.score
        }
        for r in results
    ]

if __name__ == "__main__":
    results = retrieve("How does gegenpressing work?")
    print(f"Got {len(results)} results\n")
    for i, r in enumerate(results):
        print(f"--- Result {i+1} (score: {r['score']:.3f}) ---")
        print(f"Source: {r['source']}")
        # encode safely to avoid terminal crashes on special chars
        safe_text = r["text"][:300].encode("ascii", errors="replace").decode("ascii")
        print(safe_text)
        print()