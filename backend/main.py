from fastapi import FastAPI, File, UploadFile, Form, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Dict, Any
from contextlib import asynccontextmanager
import uvicorn
import os
import uuid
import aiofiles
from datetime import datetime, timezone
import logging
import traceback
import asyncio

# Import our modules
from .database import get_db, create_tables, Document
from .schemas import DocumentResponse, DocumentListResponse, UploadResponse, BulkUploadResponse, BulkUploadFileResult, ErrorResponse, AvailableModelsResponse, ModelInfo, ClassificationRequest
from .document_processor import DocumentProcessor, DocumentProcessingError
from .ml_classifier import classify_document_text, cleanup_ml_resources, get_available_models

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

# Get available models
@app.get("/models", response_model=AvailableModelsResponse)
async def get_models():
    """
    Get list of available classification models
    """
    try:
        models_data = get_available_models()
        models = {
            key: ModelInfo(
                key=key,
                name=info["name"],
                model_id=info["model_id"],
                description=info["description"]
            )
            for key, info in models_data.items()
        }
        return AvailableModelsResponse(models=models)
    except Exception as e:
        logger.error(f"Error retrieving models: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve available models"
        )

# Document Upload Endpoint
@app.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    model_key: str = Form("bart-large-mnli"),
    auto_classify: bool = Form(True),
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
        
        # Check file size (max 25MB)
        content = await file.read()
        file_size = len(content)
        max_size = 25 * 1024 * 1024  # 25MB
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
        
        # Perform automatic classification if text is available and auto_classify is enabled
        classification_result = None
        classification_error = None
        
        if auto_classify and extracted_text and extracted_text.strip():
            try:
                logger.info(f"Starting classification for document {db_document.id} using model: {model_key}")
                classification_start = datetime.now(timezone.utc)
                # Use provided model for auto-classification
                classification_result = classify_document_text(extracted_text, model_key=model_key)
                
                if classification_result and "error" not in classification_result:
                    try:
                        db_document.predicted_category = classification_result["predicted_category"]
                        db_document.confidence_score = classification_result["confidence_score"]
                        db_document.all_scores = classification_result.get("all_scores", {})
                        db_document.model_used = classification_result.get("model_used")
                        db_document.model_key = classification_result.get("model_key")
                        db_document.model_id = classification_result.get("model_id")
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
        elif not auto_classify:
            classification_error = None  # No error when auto-classification is disabled
            logger.info(f"Auto-classification disabled for document {db_document.id}")
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

# Bulk Document Upload Endpoint
@app.post("/bulk-upload", response_model=BulkUploadResponse)
async def bulk_upload_documents(
    files: List[UploadFile] = File(...),
    model_key: str = Form("bart-large-mnli"),
    auto_classify: bool = Form(True),
    db: Session = Depends(get_db)
):
    """
    Upload multiple documents for classification.
    Supports: TXT, PDF, DOCX files
    Max: 10 files at once
    """
    start_time = datetime.now()
    
    # Validate number of files
    if not files or len(files) == 0:
        raise HTTPException(
            status_code=400,
            detail="No files provided"
        )
    
    if len(files) > 10:
        raise HTTPException(
            status_code=400,
            detail="Maximum 10 files allowed per bulk upload"
        )
    
    # Process files concurrently with limited concurrency
    semaphore = asyncio.Semaphore(3)  # Process max 3 files simultaneously
    
    async def process_single_file(file: UploadFile) -> BulkUploadFileResult:
        async with semaphore:
            return await process_uploaded_file(file, model_key, auto_classify, db)
    
    # Create tasks for all files
    tasks = [process_single_file(file) for file in files]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process results and handle exceptions
    processed_results = []
    successful_uploads = 0
    failed_uploads = 0
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            # Handle exceptions
            error_result = BulkUploadFileResult(
                filename=files[i].filename or f"file_{i+1}",
                status="error",
                error=str(result)
            )
            processed_results.append(error_result)
            failed_uploads += 1
        else:
            processed_results.append(result)
            if result.status == "success":
                successful_uploads += 1
            else:
                failed_uploads += 1
    
    processing_time = (datetime.now() - start_time).total_seconds()
    
    return BulkUploadResponse(
        message=f"Processed {len(files)} files: {successful_uploads} successful, {failed_uploads} failed",
        total_files=len(files),
        successful_uploads=successful_uploads,
        failed_uploads=failed_uploads,
        results=processed_results,
        processing_time=processing_time
    )


async def process_uploaded_file(
    file: UploadFile, 
    model_key: str, 
    auto_classify: bool, 
    db: Session
) -> BulkUploadFileResult:
    """
    Process a single uploaded file for bulk upload.
    Returns BulkUploadFileResult with success/error status.
    """
    file_path = None
    try:
        # Validate file exists and has content
        if not file or not file.filename:
            return BulkUploadFileResult(
                filename=file.filename if file else "unknown",
                status="error",
                error="No file provided or filename is empty"
            )
        
        # Check file size (max 25MB)
        content = await file.read()
        file_size = len(content)
        max_size = 25 * 1024 * 1024  # 25MB
        if file_size > max_size:
            return BulkUploadFileResult(
                filename=file.filename,
                status="error",
                error=f"File too large. Maximum size allowed: {max_size // (1024*1024)}MB"
            )
        
        if file_size == 0:
            return BulkUploadFileResult(
                filename=file.filename,
                status="error",
                error="File is empty"
            )
        
        # Validate file type
        file_type = DocumentProcessor.get_file_type(file.filename)
        if not DocumentProcessor.is_supported_file_type(file_type):
            return BulkUploadFileResult(
                filename=file.filename,
                status="error",
                error=f"File type '{file_type}' is not supported. Please upload TXT, PDF, or DOCX files."
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
        except Exception as e:
            return BulkUploadFileResult(
                filename=file.filename,
                status="error",
                error="Failed to save uploaded file"
            )
        
        # Extract text content
        try:
            extracted_text = await DocumentProcessor.extract_text_from_file(file_path, file_type)
            warnings = []
            if not extracted_text or extracted_text.strip() == "":
                warnings.append("No readable text content found in the document")
                extracted_text = None
                
        except DocumentProcessingError as e:
            return BulkUploadFileResult(
                filename=file.filename,
                status="error",
                error=f"Failed to extract text: {str(e)}"
            )
        
        # Create document record in database
        try:
            document = Document(
                filename=safe_filename,
                original_filename=file.filename,
                file_path=file_path,
                file_size=file_size,
                file_type=file_type,
                content_text=extracted_text,
                uploaded_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            
            db.add(document)
            db.commit()
            db.refresh(document)
            
        except SQLAlchemyError as e:
            # Clean up file
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass
            return BulkUploadFileResult(
                filename=file.filename,
                status="error",
                error="Failed to save document to database"
            )
        
        # Auto-classify if requested and text is available
        classification_result = None
        if auto_classify and extracted_text and extracted_text.strip():
            try:
                prediction_result = classify_document_text(extracted_text, model_key)
                
                # Update document with classification
                document.predicted_category = prediction_result['predicted_category']
                document.confidence_score = prediction_result['confidence_score']
                document.all_scores = prediction_result['all_scores']
                document.is_classified = True
                document.classification_time = datetime.now(timezone.utc)
                document.inference_time = prediction_result.get('inference_time')
                document.model_used = prediction_result.get('model_name')
                document.model_key = model_key
                document.model_id = prediction_result.get('model_id')
                document.updated_at = datetime.now(timezone.utc)
                
                db.commit()
                db.refresh(document)
                
                classification_result = {
                    'predicted_category': prediction_result['predicted_category'],
                    'confidence_score': prediction_result['confidence_score'],
                    'inference_time': prediction_result.get('inference_time'),
                    'model_used': prediction_result.get('model_name')
                }
                
            except Exception as e:
                warnings = warnings or []
                warnings.append(f"Classification failed: {str(e)}")
        
        # Prepare content preview
        content_preview = None
        if extracted_text:
            content_preview = extracted_text[:200] + "..." if len(extracted_text) > 200 else extracted_text
        
        return BulkUploadFileResult(
            filename=file.filename,
            status="success",
            document_id=document.id,
            file_size=file_size,
            content_preview=content_preview,
            warnings=warnings if warnings else None,
            classification=classification_result
        )
        
    except Exception as e:
        # Clean up file if something goes wrong
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass
        
        return BulkUploadFileResult(
            filename=file.filename if file else "unknown",
            status="error",
            error=str(e)
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
async def classify_document(
    document_id: int, 
    request: ClassificationRequest = ClassificationRequest(),
    db: Session = Depends(get_db)
):
    """
    Classify a document using selected ML model
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
        
        # Perform ML classification with selected model
        classification_start = datetime.utcnow()
        classification_result = classify_document_text(
            document.content_text, 
            model_key=request.model_key
        )
        
        if "error" in classification_result:
            raise HTTPException(
                status_code=500, 
                detail=f"Classification failed: {classification_result['error']}"
            )
        
        # Update document with classification results and timing
        document.predicted_category = classification_result["predicted_category"]
        document.confidence_score = classification_result["confidence_score"]
        document.all_scores = classification_result.get("all_scores", {})
        document.model_used = classification_result.get("model_used")
        document.model_key = classification_result.get("model_key")
        document.model_id = classification_result.get("model_id")
        document.is_classified = True
        document.classification_time = classification_start
        document.inference_time = classification_result.get("inference_time", 0.0)
        document.updated_at = datetime.now(timezone.utc)
        
        db.commit()
        db.refresh(document)
        
        return {
            "message": "Document classified successfully",
            "document_id": document_id,
            "model_used": classification_result.get("model_used"),
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
