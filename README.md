# Smart Document Classifier Web Application

A FastAPI-based web application for document upload, text extraction, and classification (ML classification to be implemented).

## 🚀 Features

### ✅ Currently Implemented
- **Document Upload**: Support for TXT, PDF, and DOCX files
- **Text Extraction**: Automatic text extraction from uploaded documents
- **Database Storage**: SQLite database with SQLAlchemy ORM
- **RESTful API**: Clean and well-documented API endpoints
- **Web Interface**: Simple HTML interface for testing
- **File Management**: Upload, retrieve, list, and delete documents

### 🔄 To Be Implemented
- **Machine Learning Classification**: Document categorization using ML models
- **Advanced Frontend**: React/Vue.js frontend with drag-and-drop
- **User Authentication**: User management and document ownership
- **Advanced Search**: Full-text search capabilities

## 🛠️ Tech Stack

**Backend:**
- FastAPI (Python web framework)
- SQLAlchemy (ORM)
- SQLite (Database)
- PyPDF2 (PDF text extraction)
- python-docx (DOCX text extraction)
- aiofiles (Async file operations)

## 📁 Project Structure

```
compu-J/
├── backend/                 # Backend application
│   ├── uploads/            # Document storage (managed by backend)
│   ├── __init__.py         # Package initialization
│   ├── main.py             # FastAPI application
│   ├── database.py         # Database models and setup
│   ├── schemas.py          # Pydantic models for API
│   └── document_processor.py # Text extraction utilities
├── test/                   # Test scripts and sample files
│   ├── test_api.py         # API test script
│   ├── test_upload.py      # Upload test script
│   └── sample_document.txt # Sample test document
├── ml/                     # Machine learning dataset (future use)
│   └── Dataset/            # Document dataset for ML training
├── documents.db           # SQLite database (created automatically)
├── requirements.txt       # Python dependencies
├── run.py                 # Easy run script
├── .gitignore            # Git ignore file
└── README.md             # Project documentation
```

## 🚀 Quick Start

### 1. Setup Virtual Environment
```bash
python -m venv .venv-compuj
source .venv-compuj/bin/activate  # On macOS/Linux
# or
.venv-compuj\Scripts\activate     # On Windows
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application

**Option A: Using the run script (recommended)**
```bash
python run.py
```

**Option B: Using uvicorn directly**
```bash
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Access the Application
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Web Interface**: http://localhost:8000/interface
- **Health Check**: http://localhost:8000/health

## 📊 API Endpoints

### Document Management
- `POST /upload` - Upload a document
- `GET /documents` - Get list of all documents
- `GET /documents/{id}` - Get specific document details
- `DELETE /documents/{id}` - Delete a document
- `POST /documents/{id}/classify` - Classify document (placeholder)

### System
- `GET /` - API information
- `GET /health` - Health check
- `GET /interface` - Web testing interface

## 🧪 Testing

### Run API Tests
```bash
cd test
python test_api.py
```

### Test Document Upload
```bash
cd test
python test_upload.py
```

## 📝 API Usage Examples

### Upload a Document
```bash
curl -X POST "http://localhost:8000/upload" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@sample_document.txt"
```

### Get All Documents
```bash
curl -X GET "http://localhost:8000/documents" \
     -H "accept: application/json"
```

### Get Specific Document
```bash
curl -X GET "http://localhost:8000/documents/1" \
     -H "accept: application/json"
```

## 📋 Supported File Types

- **TXT**: Plain text files
- **PDF**: Portable Document Format
- **DOCX**: Microsoft Word documents

## 🔮 Future Enhancements

1. **Machine Learning Integration**
   - Document classification using pre-trained models
   - Confidence scoring
   - Category prediction

2. **Enhanced Frontend**
   - React/Vue.js single-page application
   - Drag-and-drop file upload
   - Real-time classification results
   - Document preview

3. **Advanced Features**
   - User authentication and authorization
   - Document search and filtering
   - Batch processing
   - Export functionality
   - API rate limiting

4. **Deployment**
   - Docker containerization
   - Production deployment setup
   - Environment configuration
   - Monitoring and logging

## 🤝 Contributing

This project is part of the CompuJ technical assessment. The ML classification component will be integrated in the next phase.

## 📄 License

This project is developed as part of a technical assessment for CompuJ.
