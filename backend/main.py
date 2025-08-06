from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List
from contextlib import asynccontextmanager
import uvicorn
import os
import uuid
import aiofiles
from datetime import datetime, timezone
import logging
import traceback

# Import our modules
from .database import get_db, create_tables, Document
from .schemas import DocumentResponse, DocumentListResponse, UploadResponse, ErrorResponse
from .document_processor import DocumentProcessor, DocumentProcessingError
from .ml_classifier import classify_document_text, cleanup_ml_resources

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Custom exception handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        create_tables()
        logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Failed to create database tables: {str(e)}")
        raise
    yield
    # Shutdown
    logger.info("🔄 Shutting down application...")
    try:
        cleanup_ml_resources()
        logger.info("✅ Application shutdown complete")
    except Exception as e:
        logger.error(f"❌ Error during shutdown: {str(e)}")

# Global exception handler
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {str(exc)}\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Please try again later.",
            "details": str(exc) if os.getenv("DEBUG") else None
        }
    )

# Create FastAPI instance
app = FastAPI(
    title="Smart Document Classifier API",
    description="A FastAPI application for document upload and classification",
    version="1.0.0",
    lifespan=lifespan
)

# Add global exception handler
app.add_exception_handler(Exception, global_exception_handler)

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
    file_path = None
    try:
        # Validate file exists and has content
        if not file or not file.filename:
            raise HTTPException(
                status_code=400,
                detail="No file provided or filename is empty"
            )
        
        # Check file size (max 10MB)
        content = await file.read()
        file_size = len(content)
        max_size = 10 * 1024 * 1024  # 10MB
        if file_size > max_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size allowed: {max_size // (1024*1024)}MB"
            )
        
        if file_size == 0:
            raise HTTPException(
                status_code=400,
                detail="File is empty"
            )
        
        # Validate file type
        file_type = DocumentProcessor.get_file_type(file.filename)
        if not DocumentProcessor.is_supported_file_type(file_type):
            raise HTTPException(
                status_code=422,
                detail={
                    "error": "Unsupported file type",
                    "message": f"File type '{file_type}' is not supported. Please upload TXT, PDF, or DOCX files.",
                    "supported_types": ["txt", "pdf", "docx", "doc"]
                }
            )
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        safe_filename = f"{file_id}.{file_type}"
        file_path = os.path.join(UPLOAD_DIR, safe_filename)
        
        # Ensure upload directory exists
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        
        # Save file to disk
        try:
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(content)
            logger.info(f"File saved successfully: {safe_filename}")
        except Exception as e:
            logger.error(f"Failed to save file {safe_filename}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to save uploaded file. Please try again."
            )
        
        # Extract text content
        try:
            extracted_text = await DocumentProcessor.extract_text_from_file(file_path, file_type)
            if not extracted_text or extracted_text.strip() == "":
                logger.warning(f"No text content extracted from {file.filename}")
                text_warning = "No readable text content found in the document"
            else:
                text_warning = None
                logger.info(f"Text extracted successfully from {file.filename} ({len(extracted_text)} characters)")
        except DocumentProcessingError as e:
            logger.error(f"Document processing error for {file.filename}: {str(e)}")
            extracted_text = None
            text_warning = str(e)
        except Exception as e:
            logger.error(f"Unexpected text extraction error for {file.filename}: {str(e)}")
            extracted_text = None
            text_warning = f"Text extraction failed: {str(e)}"
        
        # Save document info to database
        try:
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
            logger.info(f"Document saved to database with ID: {db_document.id}")
        except SQLAlchemyError as e:
            logger.error(f"Database error while saving document: {str(e)}")
            # Clean up file if database save fails
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception:
                    pass
            raise HTTPException(
                status_code=500,
                detail="Failed to save document information. Please try again."
            )
        
        # Perform automatic classification if text is available
        classification_result = None
        classification_error = None
        
        if extracted_text and extracted_text.strip():
            try:
                logger.info(f"Starting classification for document {db_document.id}")
                classification_start = datetime.now(timezone.utc)
                classification_result = classify_document_text(extracted_text)
                
                if classification_result and "error" not in classification_result:
                    try:
                        db_document.predicted_category = classification_result["predicted_category"]
                        db_document.confidence_score = classification_result["confidence_score"]
                        db_document.all_scores = classification_result.get("all_scores", {})
                        db_document.is_classified = True
                        db_document.classification_time = classification_start
                        db_document.inference_time = classification_result.get("inference_time", 0.0)
                        db_document.updated_at = datetime.now(timezone.utc)
                        db.commit()
                        logger.info(f"Classification completed for document {db_document.id}: {classification_result['predicted_category']}")
                    except SQLAlchemyError as e:
                        logger.error(f"Failed to save classification results: {str(e)}")
                        classification_error = "Classification completed but failed to save results"
                else:
                    classification_error = classification_result.get("error", "Classification failed")
                    logger.warning(f"Classification failed for document {db_document.id}: {classification_error}")
                    
            except Exception as e:
                classification_error = f"Classification error: {str(e)}"
                logger.error(f"Classification exception for document {db_document.id}: {str(e)}")
        else:
            classification_error = "No text content available for classification"
        
        # Prepare response
        content_preview = DocumentProcessor.get_content_preview(extracted_text) if extracted_text else None
        
        response_data = {
            "message": "Document uploaded successfully",
            "document_id": db_document.id,
            "filename": file.filename,
            "file_size": file_size,
            "content_preview": content_preview
        }
        
        # Add warnings if any
        warnings = []
        if text_warning:
            warnings.append(text_warning)
        if classification_error:
            warnings.append(classification_error)
        if warnings:
            response_data["warnings"] = warnings
        
        # Include classification results if available
        if classification_result and "error" not in classification_result:
            response_data["classification"] = {
                "predicted_category": classification_result["predicted_category"],
                "confidence_score": classification_result["confidence_score"],
                "all_scores": classification_result.get("all_scores", {}),
                "inference_time": classification_result.get("inference_time", 0.0)
            }
        
        return UploadResponse(**response_data)
        
    except HTTPException:
        # Re-raise HTTP exceptions (these are expected)
        raise
    except Exception as e:
        # Clean up file if something goes wrong
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"Cleaned up file after error: {file_path}")
            except Exception as cleanup_error:
                logger.error(f"Failed to clean up file {file_path}: {str(cleanup_error)}")
        
        logger.error(f"Unexpected error in upload_document: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Upload failed",
                "message": "An unexpected error occurred during file upload. Please try again.",
                "details": str(e) if os.getenv("DEBUG") else None
            }
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
        if skip < 0:
            raise HTTPException(status_code=400, detail="Skip parameter must be non-negative")
        if limit <= 0 or limit > 1000:
            raise HTTPException(status_code=400, detail="Limit must be between 1 and 1000")
            
        documents = db.query(Document)\
            .order_by(Document.updated_at.desc(), Document.uploaded_at.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()
        
        logger.info(f"Retrieved {len(documents)} documents (skip: {skip}, limit: {limit})")
        return documents
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving documents: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Database error occurred while retrieving documents"
        )
    except Exception as e:
        logger.error(f"Unexpected error retrieving documents: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while retrieving documents"
        )

# Get specific document by ID
@app.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: int, db: Session = Depends(get_db)):
    """
    Get detailed information about a specific document
    """
    try:
        if document_id <= 0:
            raise HTTPException(status_code=400, detail="Document ID must be positive")
            
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(
                status_code=404,
                detail=f"Document with ID {document_id} not found"
            )
        
        logger.info(f"Retrieved document {document_id}: {document.original_filename}")
        return document
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving document {document_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Database error occurred while retrieving document"
        )
    except Exception as e:
        logger.error(f"Unexpected error retrieving document {document_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while retrieving document"
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
        document.all_scores = classification_result.get("all_scores", {})
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
