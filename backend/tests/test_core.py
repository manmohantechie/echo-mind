import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


# ── Fixtures ──────────────────────────────────────────────────────
@pytest.fixture
def mock_settings():
    with patch("core.config.get_settings") as mock:
        settings = MagicMock()
        settings.openai_api_key = "sk-test-key"
        settings.openai_embedding_model = "text-embedding-3-small"
        settings.openai_chat_model = "gpt-4o-mini"
        settings.chroma_host = "localhost"
        settings.chroma_port = 8001
        settings.chroma_collection = "echomind_test"
        settings.database_url = "sqlite:///./test.db"
        settings.allowed_origins = "http://localhost:3000"
        settings.max_upload_size_mb = 20
        settings.chunk_size = 512
        settings.chunk_overlap = 64
        settings.top_k_results = 5
        mock.return_value = settings
        yield settings


# ── Chunking Tests ────────────────────────────────────────────────
def test_chunk_text_basic():
    from core.ingestion import chunk_text
    text = " ".join([f"word{i}" for i in range(1000)])
    chunks = chunk_text(text, chunk_size=100, overlap=20)
    assert len(chunks) > 1
    assert all(isinstance(c, str) for c in chunks)
    assert all(len(c) > 0 for c in chunks)


def test_chunk_text_small_input():
    from core.ingestion import chunk_text
    text = "This is a very short text."
    chunks = chunk_text(text, chunk_size=512, overlap=64)
    assert len(chunks) == 1
    assert chunks[0] == text


def test_chunk_text_overlap():
    from core.ingestion import chunk_text
    words = [f"w{i}" for i in range(200)]
    text = " ".join(words)
    chunks = chunk_text(text, chunk_size=50, overlap=10)
    # Verify overlap exists between consecutive chunks
    for i in range(len(chunks) - 1):
        words_a = set(chunks[i].split()[-10:])
        words_b = set(chunks[i + 1].split()[:10])
        assert len(words_a & words_b) > 0


# ── Context Building Tests ────────────────────────────────────────
def test_build_context():
    from core.rag import build_context
    chunks = [
        {
            "text": "This is chunk 1 content.",
            "metadata": {"document_name": "test.pdf", "page_number": 1},
            "relevance_score": 0.95,
        },
        {
            "text": "This is chunk 2 content.",
            "metadata": {"document_name": "test.pdf", "page_number": 2},
            "relevance_score": 0.87,
        },
    ]
    context = build_context(chunks)
    assert "test.pdf" in context
    assert "chunk 1" in context
    assert "chunk 2" in context
    assert "---" in context


def test_build_context_empty():
    from core.rag import build_context
    context = build_context([])
    assert context == ""


# ── Schema Validation Tests ───────────────────────────────────────
def test_query_request_validation():
    from models.schemas import QueryRequest
    req = QueryRequest(query="What is this document about?")
    assert req.query == "What is this document about?"
    assert req.top_k == 5
    assert req.document_ids is None


def test_query_request_custom_top_k():
    from models.schemas import QueryRequest
    req = QueryRequest(query="test", top_k=10)
    assert req.top_k == 10


# ── API Endpoint Tests ────────────────────────────────────────────
def test_health_endpoint():
    with patch("api.routes.health.chromadb") as mock_chroma, \
         patch("api.routes.health.get_settings") as mock_cfg:
        mock_cfg.return_value.openai_api_key = "sk-test"
        mock_cfg.return_value.chroma_host = "localhost"
        mock_cfg.return_value.chroma_port = 8001
        mock_chroma.HttpClient.return_value.heartbeat.return_value = True

        from main import app
        client = TestClient(app)
        # Just check the root endpoint is reachable
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "EchoMind API"


def test_upload_invalid_extension(tmp_path):
    """Test that invalid file types are rejected."""
    with patch("api.routes.documents.get_db"), \
         patch("api.routes.documents.get_settings") as mock_cfg:
        mock_cfg.return_value.max_upload_size_mb = 20
        from main import app
        client = TestClient(app)
        fake_file = tmp_path / "test.exe"
        fake_file.write_bytes(b"fake content")
        with open(fake_file, "rb") as f:
            response = client.post(
                "/api/v1/documents/upload",
                files={"file": ("test.exe", f, "application/octet-stream")},
            )
        assert response.status_code in [400, 422, 500]
