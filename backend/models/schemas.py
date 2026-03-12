from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# ── Document Schemas ──────────────────────────────────────────────
class DocumentUploadResponse(BaseModel):
    id: str
    filename: str
    original_name: str
    file_size: int
    status: str
    chunk_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    documents: List[DocumentUploadResponse]
    total: int


# ── Query Schemas ─────────────────────────────────────────────────
class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5
    document_ids: Optional[List[str]] = None  # filter by specific docs


class SourceCitation(BaseModel):
    document_id: str
    document_name: str
    chunk_text: str
    relevance_score: float
    page_number: Optional[int] = None


class QueryResponse(BaseModel):
    query: str
    answer: str
    sources: List[SourceCitation]
    model_used: str
    tokens_used: int
    latency_ms: float


# ── Health Schema ─────────────────────────────────────────────────
class HealthResponse(BaseModel):
    status: str
    version: str
    services: dict
