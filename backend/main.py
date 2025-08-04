from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn
import os
import uuid
import aiofiles
from datetime import datetime

# Import our modules
from .database import get_db, create_tables, Document
from .schemas import DocumentResponse, DocumentListResponse, UploadResponse, ErrorResponse
from .document_processor import DocumentProcessor
from .ml_classifier import classify_document_text, cleanup_ml_resources

# Create FastAPI instance
app = FastAPI(
    title="Smart Document Classifier API",
    description="A FastAPI application for document upload and classification",
    version="1.0.0"
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

@app.on_event("startup")
async def startup_event():
    create_tables()

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown"""
    print("🔄 Shutting down application...")
    cleanup_ml_resources()
    print("✅ Application shutdown complete")

# Root endpoint
@app.get("/")
async def read_root():
    return {
        "message": "Smart Document Classifier API", 
        "project": "CompuJ Document Classification System",
        "version": "1.0.0",
        "endpoints": {
            "upload": "/upload",
            "documents": "/documents",
            "document_by_id": "/documents/{id}",
            "health": "/health"
        }
    }

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
            upload_timestamp=datetime.utcnow()
        )
        
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        
        # Perform automatic classification if text is available
        classification_result = None
        if extracted_text:
            try:
                classification_result = classify_document_text(extracted_text)
                if "error" not in classification_result:
                    db_document.predicted_category = classification_result["predicted_category"]
                    db_document.confidence_score = classification_result["confidence_score"]
                    db_document.is_classified = True
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
    """
    try:
        documents = db.query(Document).offset(skip).limit(limit).all()
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
        classification_result = classify_document_text(document.content_text)
        
        if "error" in classification_result:
            raise HTTPException(
                status_code=500, 
                detail=f"Classification failed: {classification_result['error']}"
            )
        
        # Update document with classification results
        document.predicted_category = classification_result["predicted_category"]
        document.confidence_score = classification_result["confidence_score"]
        document.is_classified = True
        
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

# Serve a simple HTML interface for testing
@app.get("/interface", response_class=HTMLResponse)
async def document_interface():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Document Classifier</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .upload-area { border: 2px dashed #ccc; padding: 20px; text-align: center; margin: 20px 0; }
            .document-list { margin-top: 30px; }
            .document-item { background: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 5px; }
        </style>
    </head>
    <body>
        <h1>Smart Document Classifier</h1>
        
        <div class="upload-area">
            <h3>Upload Document</h3>
            <input type="file" id="fileInput" accept=".txt,.pdf,.docx">
            <button onclick="uploadFile()">Upload & Classify</button>
            <div style="margin-top: 10px;">
                <label>
                    <input type="checkbox" id="autoClassify" checked> 
                    Auto-classify on upload
                </label>
            </div>
        </div>
        
        <div id="result"></div>
        
        <div class="document-list">
            <h3>Uploaded Documents</h3>
            <button onclick="loadDocuments()">Refresh List</button>
            <div id="documents"></div>
        </div>

        <script>
            async function uploadFile() {
                const fileInput = document.getElementById('fileInput');
                const file = fileInput.files[0];
                
                if (!file) {
                    alert('Please select a file');
                    return;
                }
                
                const formData = new FormData();
                formData.append('file', file);
                
                try {
                    const response = await fetch('/upload', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok) {
                        let resultHtml = `<div style="color: green;">Upload successful! Document ID: ${result.document_id}</div>`;
                        
                        if (result.classification) {
                            resultHtml += `
                                <div style="margin-top: 10px; padding: 10px; background: #f0f8ff; border-radius: 5px;">
                                    <strong>🤖 Auto-Classification Result:</strong><br>
                                    <strong>Category:</strong> ${result.classification.predicted_category}<br>
                                    <strong>Confidence:</strong> ${(result.classification.confidence_score * 100).toFixed(1)}%
                                </div>
                            `;
                        }
                        
                        document.getElementById('result').innerHTML = resultHtml;
                        loadDocuments();
                    } else {
                        document.getElementById('result').innerHTML = 
                            `<div style="color: red;">Error: ${result.detail}</div>`;
                    }
                } catch (error) {
                    document.getElementById('result').innerHTML = 
                        `<div style="color: red;">Error: ${error.message}</div>`;
                }
            }
            
            async function loadDocuments() {
                try {
                    const response = await fetch('/documents');
                    const documents = await response.json();
                    
                    const documentsDiv = document.getElementById('documents');
                    documentsDiv.innerHTML = documents.map(doc => `
                        <div class="document-item">
                            <strong>${doc.original_filename}</strong> (${doc.file_type.toUpperCase()})
                            <br>Size: ${doc.file_size} bytes
                            <br>Uploaded: ${new Date(doc.upload_timestamp).toLocaleString()}
                            <br>
                            ${doc.is_classified ? 
                                `<span style="color: green;">✅ <strong>${doc.predicted_category}</strong> (${(doc.confidence_score * 100).toFixed(1)}% confidence)</span>` :
                                `<span style="color: orange;">⏳ Not classified</span> 
                                 <button onclick="classifyDocument(${doc.id})" style="margin-left: 10px;">Classify Now</button>`
                            }
                        </div>
                    `).join('');
                } catch (error) {
                    console.error('Error loading documents:', error);
                }
            }
            
            async function classifyDocument(docId) {
                try {
                    const response = await fetch(`/documents/${docId}/classify`, {
                        method: 'POST'
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok) {
                        alert(`Classification successful!\\nCategory: ${result.classification_result.predicted_category}\\nConfidence: ${(result.classification_result.confidence_score * 100).toFixed(1)}%`);
                        loadDocuments();
                    } else {
                        alert(`Classification failed: ${result.detail}`);
                    }
                } catch (error) {
                    alert(`Error: ${error.message}`);
                }
            }
            
            // Load documents on page load
            loadDocuments();
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
