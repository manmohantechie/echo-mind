import os
import shutil
import logging
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from models.database import get_db, Document
from models.schemas import DocumentUploadResponse, DocumentListResponse
from core.ingestion import ingest_document, delete_document_chunks
from core.config import get_settings

router = APIRouter(prefix="/documents", tags=["documents"])
logger = logging.getLogger(__name__)
settings = get_settings()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md"}


def process_document_background(file_path: str, doc_id: str, original_name: str, db: Session):
    """Background task: run ingestion pipeline and update DB status."""
    try:
        chunk_count = ingest_document(file_path, doc_id, original_name)
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if doc:
            doc.status = "ready"
            doc.chunk_count = chunk_count
            db.commit()
    except Exception as e:
        logger.error(f"Ingestion failed for {doc_id}: {e}")
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if doc:
            doc.status = "error"
            doc.error_message = str(e)
            db.commit()


@router.post("/upload", response_model=DocumentUploadResponse, status_code=201)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload and process a document into the knowledge base."""
    # Validate extension
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Validate size
    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > settings.max_upload_size_mb:
        raise HTTPException(
            status_code=413,
            detail=f"File too large ({size_mb:.1f} MB). Max allowed: {settings.max_upload_size_mb} MB",
        )

    # Save to disk
    import uuid
    doc_id = str(uuid.uuid4())
    save_path = UPLOAD_DIR / f"{doc_id}{ext}"
    with open(save_path, "wb") as f:
        f.write(contents)

    # Create DB record
    doc = Document(
        id=doc_id,
        filename=str(save_path),
        original_name=file.filename,
        file_size=len(contents),
        status="processing",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # Kick off background ingestion
    background_tasks.add_task(
        process_document_background, str(save_path), doc_id, file.filename, db
    )

    return doc


@router.get("/", response_model=DocumentListResponse)
def list_documents(db: Session = Depends(get_db)):
    """List all uploaded documents."""
    docs = db.query(Document).order_by(Document.created_at.desc()).all()
    return DocumentListResponse(documents=docs, total=len(docs))


@router.get("/{doc_id}", response_model=DocumentUploadResponse)
def get_document(doc_id: str, db: Session = Depends(get_db)):
    """Get a single document by ID."""
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.delete("/{doc_id}", status_code=204)
def delete_document(doc_id: str, db: Session = Depends(get_db)):
    """Delete a document and all its vector chunks."""
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete from ChromaDB
    delete_document_chunks(doc_id)

    # Delete file from disk
    try:
        if os.path.exists(doc.filename):
            os.remove(doc.filename)
    except Exception as e:
        logger.warning(f"Could not delete file {doc.filename}: {e}")

    # Delete from DB
    db.delete(doc)
    db.commit()
