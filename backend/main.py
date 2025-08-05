from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List
from contextlib import asynccontextmanager
import uvicorn
import os
import uuid
import aiofiles
from datetime import datetime, timezone

# Import our modules
from .database import get_db, create_tables, Document
from .schemas import DocumentResponse, DocumentListResponse, UploadResponse, ErrorResponse
from .document_processor import DocumentProcessor
from .ml_classifier import classify_document_text, cleanup_ml_resources

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_tables()
    yield
    # Shutdown
    print("🔄 Shutting down application...")
    cleanup_ml_resources()
    print("✅ Application shutdown complete")

# Create FastAPI instance
app = FastAPI(
    title="Smart Document Classifier API",
    description="A FastAPI application for document upload and classification",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory and database tables on startup
UPLOAD_DIR = "backend/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Mount static files (for CSS, JS, images if needed)
# app.mount("/static", StaticFiles(directory="static"), name="static")

# Root endpoint - serve the HTML interface
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Document Classifier API is running successfully"}

# Document Upload Endpoint
@app.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a document for classification.
    Supports: TXT, PDF, DOCX files
    """
    try:
        # Validate file type
        file_type = DocumentProcessor.get_file_type(file.filename)
        if not DocumentProcessor.is_supported_file_type(file_type):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file_type}. Supported types: txt, pdf, docx"
            )
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        safe_filename = f"{file_id}.{file_type}"
        file_path = os.path.join(UPLOAD_DIR, safe_filename)
        
        # Save file to disk
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        file_size = len(content)
        
        # Extract text content
        extracted_text = await DocumentProcessor.extract_text_from_file(file_path, file_type)
        
        # Save document info to database
        db_document = Document(
            filename=safe_filename,
            original_filename=file.filename,
            file_path=file_path,
            file_size=file_size,
            content_text=extracted_text,
            file_type=file_type,
            uploaded_at=datetime.now(timezone.utc)
        )
        
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        
        # Perform automatic classification if text is available
        classification_result = None
        if extracted_text:
            try:
                classification_start = datetime.now(timezone.utc)
                classification_result = classify_document_text(extracted_text)
                if "error" not in classification_result:
                    db_document.predicted_category = classification_result["predicted_category"]
                    db_document.confidence_score = classification_result["confidence_score"]
                    db_document.is_classified = True
                    db_document.classification_time = classification_start
                    db_document.inference_time = classification_result.get("inference_time", 0.0)
                    db_document.updated_at = datetime.now(timezone.utc)
                    db.commit()
            except Exception as e:
                # Don't fail upload if classification fails
                print(f"Classification failed during upload: {str(e)}")
        
        # Prepare response
        content_preview = DocumentProcessor.get_content_preview(extracted_text) if extracted_text else None
        
        response_data = {
            "message": "Document uploaded successfully",
            "document_id": db_document.id,
            "filename": file.filename,
            "file_size": file_size,
            "content_preview": content_preview
        }
        
        # Include classification results if available
        if classification_result and "error" not in classification_result:
            response_data["classification"] = {
                "predicted_category": classification_result["predicted_category"],
                "confidence_score": classification_result["confidence_score"],
                "auto_classified": True
            }
        
        return UploadResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading document: {str(e)}"
        )

# Get all documents
@app.get("/documents", response_model=List[DocumentListResponse])
async def get_all_documents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get list of all uploaded documents with their classification status
    Ordered by newest first (updated_at, then uploaded_at)
    """
    try:
        documents = db.query(Document)\
            .order_by(Document.updated_at.desc(), Document.uploaded_at.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()
        return documents
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving documents: {str(e)}"
        )

# Get specific document by ID
@app.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: int, db: Session = Depends(get_db)):
    """
    Get detailed information about a specific document
    """
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(
                status_code=404,
                detail="Document not found"
            )
        return document
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving document: {str(e)}"
        )

# Delete document
@app.delete("/documents/{document_id}")
async def delete_document(document_id: int, db: Session = Depends(get_db)):
    """
    Delete a document from the system
    """
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(
                status_code=404,
                detail="Document not found"
            )
        
        # Delete file from disk
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
        
        # Delete from database
        db.delete(document)
        db.commit()
        
        return {"message": f"Document {document.original_filename} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting document: {str(e)}"
        )

# Classify document using ML model
@app.post("/documents/{document_id}/classify")
async def classify_document(document_id: int, db: Session = Depends(get_db)):
    """
    Classify a document using BART-Large-MNLI model
    """
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        if not document.content_text:
            raise HTTPException(
                status_code=400, 
                detail="Document has no text content to classify"
            )
        
        # Perform ML classification
        classification_start = datetime.utcnow()
        classification_result = classify_document_text(document.content_text)
        
        if "error" in classification_result:
            raise HTTPException(
                status_code=500, 
                detail=f"Classification failed: {classification_result['error']}"
            )
        
        # Update document with classification results and timing
        document.predicted_category = classification_result["predicted_category"]
        document.confidence_score = classification_result["confidence_score"]
        document.is_classified = True
        document.classification_time = classification_start
        document.inference_time = classification_result.get("inference_time", 0.0)
        document.updated_at = datetime.now(timezone.utc)
        
        db.commit()
        db.refresh(document)
        
        return {
            "message": "Document classified successfully",
            "document_id": document_id,
            "classification_result": classification_result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error classifying document: {str(e)}"
        )


if __name__ == "__main__":
    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
