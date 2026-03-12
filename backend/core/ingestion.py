import fitz  # PyMuPDF
import chromadb
import uuid
import logging
from typing import List, Dict
from openai import OpenAI
from pathlib import Path

from core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def get_chroma_client() -> chromadb.HttpClient:
    """Return a ChromaDB HTTP client. Inside Docker, ChromaDB runs on its
    internal port 8000. We read CHROMA_PORT from env which should be 8000
    when set via docker-compose environment block."""
    return chromadb.HttpClient(
        host=settings.chroma_host,
        port=settings.chroma_port,
    )


def get_or_create_collection(client: chromadb.HttpClient):
    return client.get_or_create_collection(
        name=settings.chroma_collection,
        metadata={"hnsw:space": "cosine"},
    )


def extract_text_from_pdf(file_path: str) -> List[Dict]:
    doc = fitz.open(file_path)
    pages = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text").strip()
        if text:
            pages.append({"text": text, "page": page_num + 1})
    doc.close()
    return pages


def extract_text_from_txt(file_path: str) -> List[Dict]:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read().strip()
    return [{"text": content, "page": 1}]


def chunk_text(text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
    chunk_size = chunk_size or settings.chunk_size
    overlap = overlap or settings.chunk_overlap
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        if chunk.strip():
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


def embed_texts(texts: List[str]) -> List[List[float]]:
    client = OpenAI(api_key=settings.openai_api_key)
    all_embeddings = []
    batch_size = 100
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        response = client.embeddings.create(
            model=settings.openai_embedding_model,
            input=batch,
        )
        all_embeddings.extend([item.embedding for item in response.data])
    return all_embeddings


def ingest_document(file_path: str, document_id: str, original_name: str) -> int:
    ext = Path(file_path).suffix.lower()

    if ext == ".pdf":
        pages = extract_text_from_pdf(file_path)
    elif ext in [".txt", ".md"]:
        pages = extract_text_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    if not pages:
        raise ValueError("No text content found in document")

    all_chunks = []
    for page_data in pages:
        for chunk in chunk_text(page_data["text"]):
            all_chunks.append({
                "text": chunk,
                "page": page_data["page"],
                "document_id": document_id,
                "document_name": original_name,
            })

    if not all_chunks:
        raise ValueError("No chunks generated from document")

    texts = [c["text"] for c in all_chunks]
    logger.info(f"Embedding {len(texts)} chunks...")
    embeddings = embed_texts(texts)

    chroma_client = get_chroma_client()
    collection = get_or_create_collection(chroma_client)

    collection.add(
        ids=[str(uuid.uuid4()) for _ in all_chunks],
        embeddings=embeddings,
        documents=texts,
        metadatas=[
            {
                "document_id": c["document_id"],
                "document_name": c["document_name"],
                "page_number": c["page"],
                "chunk_index": i,
            }
            for i, c in enumerate(all_chunks)
        ],
    )

    logger.info(f"Stored {len(all_chunks)} chunks for document {document_id}")
    return len(all_chunks)


def delete_document_chunks(document_id: str):
    try:
        chroma_client = get_chroma_client()
        collection = get_or_create_collection(chroma_client)
        results = collection.get(where={"document_id": document_id})
        if results["ids"]:
            collection.delete(ids=results["ids"])
    except Exception as e:
        logger.error(f"Error deleting chunks for {document_id}: {e}")
