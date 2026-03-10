import logging
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import json

from models.database import get_db, QueryLog
from models.schemas import QueryRequest, QueryResponse
from core.rag import answer_query

router = APIRouter(prefix="/query", tags=["query"])
logger = logging.getLogger(__name__)


@router.post("/", response_model=QueryResponse)
def query_knowledge_base(request: QueryRequest, db: Session = Depends(get_db)):
    """Query the knowledge base using RAG pipeline."""
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    if len(request.query) > 2000:
        raise HTTPException(status_code=400, detail="Query too long (max 2000 characters)")

    try:
        result = answer_query(
            query=request.query,
            top_k=request.top_k,
            document_ids=request.document_ids,
        )

        # Log query to DB
        log = QueryLog(
            query=request.query,
            answer=result.answer,
            sources=json.dumps([s.dict() for s in result.sources]),
            model_used=result.model_used,
            tokens_used=result.tokens_used,
            latency_ms=result.latency_ms,
        )
        db.add(log)
        db.commit()

        return result

    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")


@router.get("/history")
def get_query_history(limit: int = 20, db: Session = Depends(get_db)):
    """Get recent query history."""
    logs = db.query(QueryLog).order_by(QueryLog.created_at.desc()).limit(limit).all()
    return {
        "queries": [
            {
                "id": log.id,
                "query": log.query,
                "answer": log.answer[:200] + "..." if log.answer and len(log.answer) > 200 else log.answer,
                "tokens_used": log.tokens_used,
                "latency_ms": log.latency_ms,
                "created_at": log.created_at,
            }
            for log in logs
        ]
    }
