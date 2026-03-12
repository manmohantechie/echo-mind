import time
import logging
from typing import List, Optional
from openai import OpenAI

from core.config import get_settings
from core.ingestion import get_chroma_client, get_or_create_collection, embed_texts
from models.schemas import SourceCitation, QueryResponse

logger = logging.getLogger(__name__)
settings = get_settings()

SYSTEM_PROMPT = """You are EchoMind, an intelligent knowledge assistant.
You answer questions ONLY based on the provided context chunks from the user's documents.

Rules:
- Base your answer strictly on the provided context. Do not hallucinate.
- If the context doesn't contain enough information, say so clearly.
- Always be concise and precise.
- Cite which document/page your answer comes from when possible.
- If the user's question is unrelated to the documents, politely redirect them.
"""


def retrieve_chunks(
    query: str,
    top_k: int = None,
    document_ids: Optional[List[str]] = None,
) -> List[dict]:
    """Embed query and retrieve top-k relevant chunks from ChromaDB."""
    top_k = top_k or settings.top_k_results

    # Embed the query
    embeddings = embed_texts([query])
    query_embedding = embeddings[0]

    chroma_client = get_chroma_client()
    collection = get_or_create_collection(chroma_client)

    # Build where filter for specific documents
    where = None
    if document_ids and len(document_ids) == 1:
        where = {"document_id": document_ids[0]}
    elif document_ids and len(document_ids) > 1:
        where = {"document_id": {"$in": document_ids}}

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, collection.count() or 1),
        where=where,
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    if results["ids"] and results["ids"][0]:
        for i, doc_id in enumerate(results["ids"][0]):
            chunks.append({
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i],
                "relevance_score": round(1 - results["distances"][0][i], 4),
            })

    return chunks


def build_context(chunks: List[dict]) -> str:
    """Format retrieved chunks into a context string for the LLM."""
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        meta = chunk["metadata"]
        source_label = f"[Source {i}: {meta.get('document_name', 'Unknown')} — Page {meta.get('page_number', '?')}]"
        context_parts.append(f"{source_label}\n{chunk['text']}")
    return "\n\n---\n\n".join(context_parts)


def answer_query(
    query: str,
    top_k: int = None,
    document_ids: Optional[List[str]] = None,
) -> QueryResponse:
    """
    Full RAG pipeline:
    1. Retrieve relevant chunks
    2. Build context
    3. Generate answer via LLM
    4. Return answer with citations
    """
    start_time = time.time()

    # Step 1: Retrieve
    chunks = retrieve_chunks(query, top_k=top_k, document_ids=document_ids)

    if not chunks:
        return QueryResponse(
            query=query,
            answer="I couldn't find any relevant information in your documents. Please upload some documents first, or try rephrasing your question.",
            sources=[],
            model_used=settings.openai_chat_model,
            tokens_used=0,
            latency_ms=round((time.time() - start_time) * 1000, 2),
        )

    # Step 2: Build context
    context = build_context(chunks)

    # Step 3: Generate answer
    client = OpenAI(api_key=settings.openai_api_key)

    user_message = f"""Context from documents:
{context}

---

Question: {query}

Please answer the question based only on the context above. Cite the sources."""

    response = client.chat.completions.create(
        model=settings.openai_chat_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.2,
        max_tokens=1024,
    )

    answer = response.choices[0].message.content
    tokens_used = response.usage.total_tokens
    latency_ms = round((time.time() - start_time) * 1000, 2)

    # Step 4: Build citations
    sources = [
        SourceCitation(
            document_id=chunk["metadata"].get("document_id", ""),
            document_name=chunk["metadata"].get("document_name", "Unknown"),
            chunk_text=chunk["text"][:300] + "..." if len(chunk["text"]) > 300 else chunk["text"],
            relevance_score=chunk["relevance_score"],
            page_number=chunk["metadata"].get("page_number"),
        )
        for chunk in chunks
    ]

    return QueryResponse(
        query=query,
        answer=answer,
        sources=sources,
        model_used=settings.openai_chat_model,
        tokens_used=tokens_used,
        latency_ms=latency_ms,
    )
