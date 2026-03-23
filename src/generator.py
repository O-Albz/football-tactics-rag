from openai import OpenAI
from dotenv import load_dotenv
from src.retriever import retrieve

load_dotenv()

client = OpenAI()

SYSTEM_PROMPT = """You are an expert football tactics analyst with deep knowledge of 
football history, formations, playing styles, and coaching philosophies.

Answer questions using the provided context from tactical documents and articles.
Be specific, insightful, and reference the sources when relevant.
If the context doesn't contain enough information, say so honestly rather than making things up."""

def generate(query: str, top_k: int = 5) -> dict:
    # Retrieve relevant chunks
    chunks = retrieve(query, top_k=top_k)

    # Build context string
    context = "\n\n---\n\n".join(
        f"Source: {c['source']}\n{c['text']}"
        for c in chunks
    )

    # Call OpenAI
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
        ],
        temperature=0.3
    )

    answer = response.choices[0].message.content

    return {
        "question": query,
        "answer": answer,
        "sources": list(dict.fromkeys([c["source"] for c in chunks])),
        "chunks_used": len(chunks)
    }

if __name__ == "__main__":
    result = generate("How does gegenpressing work and who popularized it?")
    print(f"Q: {result['question']}\n")
    print(f"A: {result['answer']}\n")
    print(f"Sources: {result['sources']}")