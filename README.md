# Smart Document Classifier Web Application

A full-stack web application for document upload, text extraction, and AI-powered classification using multiple state-of-the-art language models with bulk processing capabilities.

## 🚀 Features

### ✅ Currently Implemented
- **Multi-Model AI Support**:### Total processing time**: Optimized for under 10 seconds for typical batches

## 📊 Analytics Dashboard

The application includes a comprehensive **Statistics Dashboard** providing insights into document processing:

### Dashboard Features:
- **Document Distribution**: Visual breakdown of document types (PDF, TXT, DOCX)
- **Classification Confidence Analysis**: Distribution of high/medium/low confidence scores
- **Model Usage Statistics**: Comparison of BART vs mDeBERTa model usage
- **Upload Trends**: Activity tracking (today, this week, this month)
- **Recent Activity**: Latest documents with classification details
- **Interactive Charts**: Responsive visualizations with progress bars and color coding
- **Real-time Data**: Live updates based on current database content

### Analytics Insights:
- Track which document types are most commonly uploaded
- Monitor classification model performance and confidence patterns
- Analyze upload activity trends over time
- Identify popular AI model preferences
- Review recent classification results

## 🛡️ Error Handlingoose between BART-Large-MNLI and mDeBERTa-v3-Base models
- **Document Upload**: Support for TXT, PDF, and DOCX files with drag-and-drop interface (up to 25MB)
- **Bulk Upload Processing**: Upload up to 10 files simultaneously with concurrent processing
- **AI Classification**: Real-time document classification with confidence scoring
- **Statistics Dashboard**: Comprehensive analytics with charts and metrics
- **Text Extraction**: Automatic text extraction from uploaded documents
- **Full Classification Results**: View all category confidence scores ranked from highest to lowest
- **Modern React Frontend**: TypeScript-based React application with Vite build system
- **Responsive Design**: Mobile-friendly interface that adapts to all screen sizes
- **Database Storage**: SQLite database with SQLAlchemy ORM
- **RESTful API**: Clean and well-documented FastAPI endpoints
- **File Management**: Upload, retrieve, list, delete, and re-classify documents
- **Real-time Processing**: Live classification with processing time tracking

### 🔄 Future Enhancements
- **User Authentication**: User management and document ownership
- **Advanced Search**: Full-text search capabilities
- **Export Functionality**: Export classification results
- **Enhanced Celery Integration**: For high-volume bulk processing (1000+ documents)
- **WebSocket Support**: Real-time upload progress for large batches

## 🛠️ Tech Stack

**Frontend:**
- React 18 (UI library)  
- TypeScript (Type safety)
- Vite (Build tool and dev server)
- CSS3 (Modern styling with responsive design)

**Backend:**
- FastAPI (Python web framework)
- SQLAlchemy (ORM)
- SQLite (Database)
- PyPDF2 (PDF text extraction)
- python-docx (DOCX text extraction)
- aiofiles (Async file operations)

**AI/ML:**
- Transformers (Hugging Face)
- BART-Large-MNLI (Zero-shot classification model)
- mDeBERTa-v3-Base-MNLI-XNLI (Multilingual classification model)
- PyTorch (Deep learning framework)

## 📁 Project Structure

```
compu-J/
├── backend/                 # Backend FastAPI application
│   ├── uploads/            # Document storage (managed by backend)
│   ├── __init__.py         # Package initialization
│   ├── main.py             # FastAPI application and endpoints
│   ├── database.py         # Database models and setup
│   ├── schemas.py          # Pydantic models for API
│   ├── document_processor.py # Text extraction utilities
│   ├── ml_classifier.py    # BART-Large-MNLI classification
│   ├── classifier.ipynb    # ML model development notebook
│   └── migrate_db.py       # Database migration scripts
├── frontend/               # React TypeScript application
│   ├── src/
│   │   ├── components/     # React components
│   │   │   ├── DocumentList.tsx     # Document display component
│   │   │   ├── DocumentUpload.tsx   # Single file upload interface
│   │   │   ├── BulkUpload.tsx       # Bulk file upload interface
│   │   │   ├── StatisticsDashboard.tsx # Analytics dashboard
│   │   │   └── *.css               # Component styling
│   │   ├── services/       # API integration
│   │   │   └── api.ts      # API client and types
│   │   ├── App.tsx         # Main application component
│   │   ├── App.css         # Global styles
│   │   ├── main.tsx        # Application entry point
│   │   └── index.css       # Base styles
│   ├── public/             # Static assets
│   ├── package.json        # Node.js dependencies
│   ├── tsconfig.json       # TypeScript configuration
│   ├── vite.config.ts      # Vite configuration
│   └── eslint.config.js    # ESLint configuration
├── data/                   # ML training dataset
│   └── Dataset/            # Document dataset for ML training
├── test/                   # Test scripts and sample files
│   ├── test_api.py         # API test script
│   ├── test_upload.py      # Upload test script
│   └── sample_document.txt # Sample test document
├── documents.db           # SQLite database (created automatically)
├── requirements.txt       # Python dependencies
├── run.py                 # Easy backend run script
├── .gitignore            # Git ignore file
└── README.md             # Project documentation
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ 
- Node.js 16+ and npm
- Git

### 1. Clone the Repository
```bash
git clone <repository-url>
cd compu-J
```

### 2. Backend Setup

#### Setup Python Virtual Environment
```bash
python -m venv .venv-compuj
source .venv-compuj/bin/activate  # On macOS/Linux
# or
.venv-compuj\Scripts\activate     # On Windows
```

#### Install Python Dependencies
```bash
pip install -r requirements.txt
```

#### Start Backend Server
```bash
# Option A: Using the run script (recommended)
python run.py

# Option B: Using uvicorn directly
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup

#### Install Node.js Dependencies
```bash
cd frontend
npm install
```

#### Start Frontend Development Server
```bash
npm run dev
```

### 4. Access the Application
- **Frontend Application**: http://localhost:3000
  - **Single Upload Tab**: Individual document upload with real-time classification
  - **Bulk Upload Tab**: Upload up to 10 files simultaneously
  - **Statistics Tab**: Analytics dashboard with document insights
- **Backend API Documentation**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc  
- **Health Check**: http://localhost:8000/health

## 📊 API Endpoints

### Document Management
- `POST /upload` - Upload and optionally auto-classify a single document
- `POST /bulk-upload` - Upload and process multiple documents (max 10 files)
- `GET /documents` - Get list of all documents with classification results
- `GET /documents/{id}` - Get specific document details
- `DELETE /documents/{id}` - Delete a document
- `POST /documents/{id}/classify` - Classify document using selected model

### Model Management
- `GET /models` - Get available AI models (BART, mDeBERTa)

### System
- `GET /` - API information
- `GET /health` - Health check

## 🤖 AI Classification

The application supports **multiple AI models** for document classification:

### Available Models:
1. **BART-Large-MNLI** (facebook/bart-large-mnli)
   - Fast inference and reliable classification
   - Optimized for English documents
   - Good general-purpose performance

2. **mDeBERTa-v3-Base** (MoritzLaurer/mDeBERTa-v3-base-mnli-xnli)  
   - Multilingual support (cross-lingual classification)
   - Higher accuracy on complex documents
   - Supports multiple languages

### Document Categories:
- **Technical Documentation**: Manuals, guides, API docs
- **Business Proposal**: Business plans, proposals, pitches  
- **Academic Paper**: Research papers, studies, theses
- **Legal Document**: Contracts, agreements, legal texts
- **General Article**: News, blogs, general content
- **Other**: Documents that don't fit other categories

### Classification Features:
- **Model Selection**: Choose between available AI models
- **Confidence Scores**: Shows confidence percentage for all categories
- **Ranking Display**: Categories ranked from highest to lowest confidence
- **Processing Time**: Tracks inference duration for performance analysis
- **Automatic Classification**: Option to classify during upload
- **Re-classification**: Ability to re-classify existing documents with different models
- **Bulk Processing**: Concurrent classification of multiple documents

## 🧪 Testing

### Bulk Upload Testing
Test the new bulk upload functionality:
```bash
# Create test files
mkdir test_bulk_files
echo "AI and machine learning content..." > test_bulk_files/test1.txt
echo "Financial market analysis..." > test_bulk_files/test2.txt
echo "Sports championship report..." > test_bulk_files/test3.txt

# Test bulk upload API
curl -X POST http://localhost:8000/bulk-upload \
  -F "files=@test_bulk_files/test1.txt" \
  -F "files=@test_bulk_files/test2.txt" \
  -F "files=@test_bulk_files/test3.txt" \
  -F "model_key=bart-large-mnli" \
  -F "auto_classify=true"
```

### Frontend Testing
The React application includes:
- Real-time file upload with drag-and-drop (single and bulk)
- Live classification results display
- Statistics dashboard with interactive charts
- Model selection interface
- Responsive design testing across devices
- TypeScript type safety

### Backend API Testing
```bash
cd test
python test_api.py
```

### Test Document Upload via API
```bash
cd test
python test_upload.py
```

## 📝 API Usage Examples

### Upload and Auto-Classify a Single Document
```bash
curl -X POST "http://localhost:8000/upload" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@sample_document.txt" \
     -F "model_key=bart-large-mnli" \
     -F "auto_classify=true"
```

### Bulk Upload Multiple Documents
```bash
curl -X POST "http://localhost:8000/bulk-upload" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "files=@doc1.txt" \
     -F "files=@doc2.pdf" \
     -F "files=@doc3.docx" \
     -F "model_key=mdeberta-v3-base" \
     -F "auto_classify=true"
```

### Get Available Models
```bash
curl -X GET "http://localhost:8000/models" \
     -H "accept: application/json"
```

### Classify an Existing Document
```bash
curl -X POST "http://localhost:8000/documents/1/classify" \
     -H "accept: application/json" \
     -H "Content-Type: application/json" \
     -d '{"model_key": "mdeberta-v3-base"}'
```

### Get All Documents with Classifications
```bash
curl -X GET "http://localhost:8000/documents" \
     -H "accept: application/json"
```

## 📋 Supported File Types

- **TXT**: Plain text files (up to 25MB)
- **PDF**: Portable Document Format (up to 25MB)
- **DOCX**: Microsoft Word documents (up to 25MB)

### Bulk Upload Limits:
- **Maximum files per batch**: 10 files
- **Concurrent processing**: Up to 3 files simultaneously
- **File size limit**: 25MB per file
- **Total processing time**: Optimized for under 10 seconds for typical batches

## 🛡️ Error Handling

The application implements **comprehensive error handling** across all layers for robust operation:

### **Frontend (React/TypeScript)**
- **Multi-layer validation**: HTML accept attributes + JavaScript validation + API safety checks
- **Real-time feedback**: Immediate error messages with visual indicators (✅ ❌ ⚠️)
- **User-friendly messages**: Clear, actionable error descriptions for all scenarios
- **Network resilience**: Proper handling of connection issues, timeouts, and server errors
- **File validation**: Client-side size and type checking before upload
- **Bulk upload errors**: Per-file error reporting without stopping other uploads

### **Backend (FastAPI/Python)**
- **Structured error responses**: Consistent JSON error format with appropriate HTTP codes
- **File processing resilience**: Handles corrupted files, encoding issues, extraction failures
- **Database safety**: Transaction rollback and automatic file cleanup on failures
- **ML model errors**: Graceful fallback when classification fails
- **Resource management**: Proper cleanup of temporary files and database connections
- **Concurrent processing**: Individual file error handling in bulk operations

### **Error Categories**
- **400 Bad Request**: Invalid file types, missing data, malformed requests
- **413 Payload Too Large**: Files exceeding 25MB limit
- **422 Unprocessable Entity**: Unsupported file formats, processing failures
- **500 Internal Server Error**: Database issues, ML model failures, unexpected errors

### **Recovery Features**
- **Retry mechanisms**: User-initiated retry for failed operations
- **Partial success handling**: Bulk uploads continue despite individual file failures
- **Warning system**: Non-fatal issues displayed alongside successful operations
- **Automatic cleanup**: Failed uploads don't leave orphaned files or database entries

## 🔮 Future Enhancements

1. **Advanced AI Features**
   - Custom model training with user data
   - Multi-language support (building on mDeBERTa multilingual capabilities)
   - Document similarity search
   - Automated tagging and metadata extraction
   - Confidence threshold settings for auto-classification

2. **Enhanced User Experience**
   - Dark/light theme toggle
   - Advanced filtering and sorting in document list
   - Document preview functionality
   - Batch operations (delete, re-classify multiple documents)
   - Export functionality (CSV, JSON, PDF reports)

3. **Bulk Processing Enhancements**
   - **Celery Integration**: For processing 1000+ documents
   - **WebSocket Support**: Real-time progress updates for large batches  
   - **Queue Management**: Priority-based document processing
   - **Resume Capability**: Continue interrupted bulk uploads

4. **Enterprise Features**
   - User authentication and authorization
   - Role-based access control
   - API rate limiting and quotas
   - Audit logging and activity tracking
   - Multi-tenant support

5. **Deployment & Scaling**
   - Docker containerization
   - Kubernetes deployment configurations
   - Cloud storage integration (AWS S3, Google Cloud)
   - Horizontal scaling with Redis caching
   - Load balancing for concurrent processing

6. **Data Management**
   - Database migrations and versioning
   - Automated backup and restore functionality
   - Data export/import features
   - Performance monitoring and metrics
   - Database optimization for large datasets

## 🤝 Contributing

This project demonstrates a complete full-stack implementation with modern technologies and advanced features:

### Recent Updates (August 2025):
- ✅ **Multi-Model AI Support**: Added mDeBERTa-v3-Base alongside BART-Large-MNLI
- ✅ **Bulk Upload Processing**: Concurrent processing of up to 10 files
- ✅ **Statistics Dashboard**: Comprehensive analytics with interactive charts
- ✅ **Enhanced Database Schema**: Model tracking and metadata support
- ✅ **Responsive UI**: Mobile-optimized design with navigation tabs
- ✅ **Improved Error Handling**: Per-file error reporting in bulk uploads

### Technology Stack:
- **Frontend**: React 18 + TypeScript + Vite
- **Backend**: FastAPI + SQLAlchemy + AsyncIO
- **AI/ML**: Transformers + Multi-Model Support (BART + mDeBERTa)
- **Database**: SQLite with potential for PostgreSQL migration
- **Processing**: Concurrent async processing with semaphore control

## 📄 License

This project is developed as part of a technical assessment for CompuJ, showcasing full-stack development with AI integration.
