from fastapi import APIRouter
import chromadb
from openai import OpenAI

from core.config import get_settings
from models.schemas import HealthResponse

router = APIRouter(tags=["health"])
settings = get_settings()


@router.get("/health", response_model=HealthResponse)
def health_check():
    """Check health of all services."""
    services = {}

    # Check ChromaDB
    try:
        client = chromadb.HttpClient(host=settings.chroma_host, port=settings.chroma_port)
        client.heartbeat()
        services["chromadb"] = "ok"
    except Exception as e:
        services["chromadb"] = f"error: {str(e)}"

    # Check OpenAI (just validate key format, don't make a real call)
    try:
        if settings.openai_api_key and settings.openai_api_key.startswith("sk-"):
            services["openai"] = "configured"
        else:
            services["openai"] = "not configured"
    except Exception:
        services["openai"] = "error"

    overall = "ok" if all(v in ["ok", "configured"] for v in services.values()) else "degraded"

    return HealthResponse(
        status=overall,
        version="1.0.0",
        services=services,
    )


@router.get("/")
def root():
    return {
        "name": "EchoMind API",
        "version": "1.0.0",
        "description": "AI-powered knowledge assistant — turn your documents into a conversation.",
        "docs": "/docs",
    }
