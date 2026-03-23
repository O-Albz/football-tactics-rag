import wikipediaapi
from pathlib import Path
from dotenv import load_dotenv
from llama_index.core import SimpleDirectoryReader, Settings
from llama_index.core.node_parser import MarkdownNodeParser, SentenceSplitter
from llama_index.embeddings.openai import OpenAIEmbedding
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import uuid
import os

load_dotenv()

COLLECTION_NAME = "football_tactics"
EMBED_DIM = 1536

import os
QDRANT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "qdrant_db")


TACTICS_PAGES = [
    # Formations
    "4-4-2",
    "4-3-3",
    "4-2-3-1",
    "3-5-2",
    "3-4-3",
    "4-5-1",
    "5-3-2",
    "4-4-1-1",

    # Tactical systems
    "Tiki-taka",
    "Gegenpressing",
    "Catenaccio",
    "Total_Football",
    "High_press_(association_football)",
    "Pressing_(association_football)",
    "Offside_trap",
    "Zonal_marking",
    "Counter-attacking",
    "Park_the_bus_(association_football)",

    # Positions and roles
    "False_9",
    "Libero_(football)",
    "Sweeper_(football)",
    "Mezzala",
    "Inverted_winger",
    "Target_man",
    "Defensive_midfielder",
    "Attacking_midfielder",
    "Wing-back",

    # Managers — modern
    "Pep_Guardiola",
    "Jürgen_Klopp",
    "José_Mourinho",
    "Carlo_Ancelotti",
    "Marcelo_Bielsa",
    "Thomas_Tuchel",
    "Julian_Nagelsmann",
    "Arsène_Wenger",
    "Louis_van_Gaal",

    # Managers — historic
    "Rinus_Michels",
    "Arrigo_Sacchi",
    "Johan_Cruyff",
    "Ernst_Happel",
    "Helenio_Herrera",
    "Béla_Guttmann",
    "Valeriy_Lobanovskyi",
    "Bill_Shankly",
    "Brian_Clough",
    "Helmut_Schön",

    # Concepts
    "Pressing_(association_football)",
    "Set_piece_(association_football)",
    "Transition_(association_football)",
    "Gegenpressing",
    "Association_football_tactics_and_skills",
    "History_of_association_football",
]

def fetch_wikipedia_articles(output_dir: str = "./data/documents"):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    wiki = wikipediaapi.Wikipedia(
        language="en",
        user_agent="football-tactics-rag/1.0"
    )

    for page_name in TACTICS_PAGES:
        page = wiki.page(page_name)
        
        if not page.exists():
            print(f"Page not found: {page_name}")
            continue

        # Save as markdown with title as header
        content = f"# {page.title}\n\n{page.text}"
        filename = page_name.lower().replace(" ", "_") + ".md"
        filepath = Path(output_dir) / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        print(f"Saved: {filename} ({len(page.text)} chars)")





def get_qdrant_client():
    # Keep ingestion/retrieval consistent with the embedded on-disk layout.
    if os.getenv("QDRANT_URL") and os.getenv("QDRANT_API_KEY"):
        return QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"))
    else:
        return QdrantClient(path=QDRANT_PATH)

def setup_collection(client: QdrantClient):
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME not in existing:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=EMBED_DIM, distance=Distance.COSINE)
        )
        print(f"Created collection: {COLLECTION_NAME}")

def embed_and_store(docs_path: str = "./data/documents"):
    client = get_qdrant_client()
    setup_collection(client)

    reader = SimpleDirectoryReader(docs_path)
    documents = reader.load_data()
    print(f"Loaded {len(documents)} documents")

    parser = SentenceSplitter(
        chunk_size=512,
        chunk_overlap=64,
    )
    nodes = parser.get_nodes_from_documents(documents)
    print(f"Created {len(nodes)} chunks")

    embedder = OpenAIEmbedding(model="text-embedding-3-small")
    points = []

    for i, node in enumerate(nodes):
        text = node.get_content()
        if not text.strip():
            continue

        embedding = embedder.get_text_embedding(text)
        points.append(PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={
                "text": text,
                "doc_id": node.node_id,
                "source": node.metadata.get("file_name", "unknown")
            }
        ))

        if (i + 1) % 20 == 0:
            print(f"Embedded {i + 1}/{len(nodes)} chunks...")

    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"Done — stored {len(points)} chunks in Qdrant")

if __name__ == "__main__":
    # fetch_wikipedia_articles()
    embed_and_store()
