from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import uuid
import os

app = FastAPI(title="Document Agent API")

# In-memory document index store (for demo; use persistent store in prod)
document_indexes: Dict[str, dict] = {}

class DocumentIndex(BaseModel):
    doc_id: str
    filename: str
    title: str
    summary: str
    outline: List[str]
    tags: List[str] = []

@app.get("/health")
def health_check():
    return {"status": "ok", "agent": "document"}

@app.post("/upload", response_model=DocumentIndex)
def upload_document(file: UploadFile = File(...)):
    """Accept a document upload, generate an organizational index, and store it."""
    # Read file content
    content = file.file.read().decode(errors="ignore")
    # For demo: Use simple heuristics for title/summary/outline
    title = file.filename
    summary = content[:300] if len(content) > 300 else content
    outline = [line.strip() for line in content.splitlines() if line.strip()][:10]  # First 10 non-empty lines
    doc_id = str(uuid.uuid4())
    index = DocumentIndex(
        doc_id=doc_id,
        filename=file.filename,
        title=title,
        summary=summary,
        outline=outline,
        tags=[]
    )
    document_indexes[doc_id] = index.dict()
    return index

@app.get("/index/{doc_id}", response_model=DocumentIndex)
def get_document_index(doc_id: str):
    """Retrieve the organizational index for a document by ID."""
    index = document_indexes.get(doc_id)
    if not index:
        raise HTTPException(status_code=404, detail="Document index not found.")
    return index

@app.get("/indexes", response_model=List[DocumentIndex])
def list_document_indexes():
    """List all available document indexes."""
    return list(document_indexes.values())
