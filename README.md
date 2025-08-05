# Smart Document Classifier Web Application

A full-stack web application for document upload, text extraction, and AI-powered classification using BART-Large-MNLI model.

## 🚀 Features

### ✅ Currently Implemented
- **Document Upload**: Support for TXT, PDF, and DOCX files with drag-and-drop interface
- **AI Classification**: Real-time document classification using BART-Large-MNLI model
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
- **Batch Processing**: Multiple document upload and classification
- **Export Functionality**: Export classification results

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
│   │   │   ├── DocumentList.tsx    # Document display component
│   │   │   ├── DocumentUpload.tsx  # Upload interface
│   │   │   └── *.css              # Component styling
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
- **Backend API Documentation**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc  
- **Health Check**: http://localhost:8000/health

## 📊 API Endpoints

### Document Management
- `POST /upload` - Upload and optionally auto-classify a document
- `GET /documents` - Get list of all documents with classification results
- `GET /documents/{id}` - Get specific document details
- `DELETE /documents/{id}` - Delete a document
- `POST /documents/{id}/classify` - Classify document using BART-Large-MNLI

### System
- `GET /` - API information
- `GET /health` - Health check

## 🤖 AI Classification

The application uses **BART-Large-MNLI** (facebook/bart-large-mnli) for zero-shot document classification with the following categories:

- **Technical Documentation**: Manuals, guides, API docs
- **Business Proposal**: Business plans, proposals, pitches  
- **Academic Paper**: Research papers, studies, theses
- **Legal Document**: Contracts, agreements, legal texts
- **General Article**: News, blogs, general content
- **Other**: Documents that don't fit other categories

### Classification Features:
- **Confidence Scores**: Shows confidence percentage for all categories
- **Ranking Display**: Categories ranked from highest to lowest confidence
- **Processing Time**: Tracks inference duration
- **Automatic Classification**: Option to classify during upload
- **Re-classification**: Ability to re-classify existing documents

## 🧪 Testing

### Frontend Testing
The React application includes:
- Real-time file upload with drag-and-drop
- Live classification results display
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

### Upload and Auto-Classify a Document
```bash
curl -X POST "http://localhost:8000/upload" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@sample_document.txt"
```

### Classify an Existing Document
```bash
curl -X POST "http://localhost:8000/documents/1/classify" \
     -H "accept: application/json"
```

### Get All Documents with Classifications
```bash
curl -X GET "http://localhost:8000/documents" \
     -H "accept: application/json"
```

## 📋 Supported File Types

- **TXT**: Plain text files
- **PDF**: Portable Document Format  
- **DOCX**: Microsoft Word documents

## 🛡️ Error Handling

The application implements comprehensive error handling across all layers:

- **Frontend Validation**: Multi-layered file type checking and user-friendly error messages
- **Backend Processing**: Robust error handling for file corruption, encoding issues, and processing failures
- **API Layer**: Structured error responses with appropriate HTTP status codes
- **Database Operations**: Transaction rollback and resource cleanup on failures

For detailed error handling documentation, see [`docs/ERROR_HANDLING.md`](docs/ERROR_HANDLING.md).

### Error Testing
```bash
# Run comprehensive error handling tests
cd /path/to/compu-J
python test/test_error_handling.py
```

## 🔮 Future Enhancements

1. **Advanced AI Features**
   - Custom model training with user data
   - Multi-language support
   - Document similarity search
   - Automated tagging and metadata extraction

2. **Enhanced User Experience**
   - Dark/light theme toggle
   - Advanced filtering and sorting
   - Document preview functionality
   - Batch operations

3. **Enterprise Features**
   - User authentication and authorization
   - Role-based access control
   - API rate limiting and quotas
   - Audit logging

4. **Deployment & Scaling**
   - Docker containerization
   - Kubernetes deployment
   - Cloud storage integration (AWS S3, etc.)
   - Horizontal scaling with Redis caching

5. **Data Management**
   - Database migrations
   - Backup and restore functionality
   - Data export/import features
   - Performance monitoring

## 🤝 Contributing

This project demonstrates a complete full-stack implementation with modern technologies:

- **Frontend**: React 18 + TypeScript + Vite
- **Backend**: FastAPI + SQLAlchemy
- **AI/ML**: Transformers + BART-Large-MNLI
- **Database**: SQLite with potential for PostgreSQL migration

## 📄 License

This project is developed as part of a technical assessment for CompuJ, showcasing full-stack development with AI integration.
