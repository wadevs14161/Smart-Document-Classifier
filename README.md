# Smart Document Classifier Web Application

A full-stack web application for intelligent document classification using deep learning models. The system automatically categorizes uploaded documents (TXT, PDF, DOCX) using zero-shot classification with transformer neural networks.

## 📋 Table of Contents
- [Features](#-features)
- [AI Model Selection & Comparison](#-ai-model-selection--comparison)
- [Architecture Overview](#-architecture-overview)
- [Quick Start with Docker](#-quick-start-with-docker-recommended)
- [Setup and Installation](#-setup-and-installation)
- [Running the Application](#-running-the-application)
- [Usage Guide](#-usage-guide)
- [Technical Implementation](#-technical-implementation)
- [Future Improvements](#-future-improvements)
- [Challenges Encountered](#-challenges-encountered)

---

## ✨ Features

### Core Functionality
- **Zero-Shot Document Classification**: Classify documents without custom training using pre-trained transformer models
- **Multi-Model Support**: Choose between BART-Large-MNLI (407M parameters) and mDeBERTa-v3-Base (279M parameters)
- **Bulk Upload Processing**: Upload and process up to 10 files simultaneously with concurrent processing
- **Real-time Analytics**: Statistics dashboard with document distribution, confidence scores, and usage metrics
- **File Format Support**: TXT, PDF, and DOCX files up to 25MB each
- **Responsive Web Interface**: Modern React frontend with drag-and-drop functionality

### Document Classification Categories
- Technical Documentation
- Business Proposal  
- Academic Paper
- Legal Document
- General Article
- Other

---

## 🤖 AI Model Selection & Comparison

The Smart Document Classifier integrates two state-of-the-art transformer models, each optimized for different use cases and performance requirements.

### **Available Models**

#### **BART-Large-MNLI (Recommended for English)**
- **Model ID**: `facebook/bart-large-mnli`
- **Parameters**: 407 million
- **Training**: Fine-tuned on Multi-Genre Natural Language Inference (MNLI)
- **Memory Usage**: ~1.6 GB RAM
- **Language Support**: English (optimized)
- **Best For**: English business documents, academic papers, technical documentation

#### **mDeBERTa-v3-Base-MNLI-XNLI (Recommended for Multilingual)**
- **Model ID**: `MoritzLaurer/mDeBERTa-v3-base-mnli-xnli`
- **Parameters**: 279 million
- **Training**: Fine-tuned on MNLI + XNLI (cross-lingual)
- **Memory Usage**: ~1.2 GB RAM
- **Language Support**: 100+ languages
- **Best For**: International documents, multilingual content, diverse language requirements

### **Model Performance Comparison**

Below is a comprehensive comparison of classification results across four different AI models using the same set of test documents:

> **Legend**: 🟢 = Academic Paper | 🔵 = Legal Document | 🟡 = Technical Documentation | ⚫ = Business Proposal | 🟣 = General Article | ⚪ = Not classified

| Document | Gemini 2.5 Flash | Grok 3 | BART-Large-MNLI | mDeBERTa-v3-Base | Agreement |
|---|---|---|---|---|---|
| **Agreement-Regarding-Quantum-Leap.txt** | 🔵 **Legal Document** | 🔵 **Legal Document** | 🔵 **Legal Document** (45.1%) | 🔵 **Legal Document** (29.5%) |  **Match** |
| **Grundfosliterature-5615985.pdf** | 🟡 **Technical Documentation** | 🟡 **Technical Documentation** | 🟣 **General Article** (30.6%) | 🔵 **Legal Document** (28.7%) |  **No Match** |
| **How I use LLMs as a staff engineer.txt** | 🟣 **General Article** | 🟣 **General Article** | ⚫ **Business Proposal** (22.7%) | 🔵 **Legal Document** (27.0%) | ❌ **No Match** |
| **Lightweight Authenticated Cryptography...txt** | 🟢 **Academic Paper** | 🟢 **Academic Paper** | 🟣 **General Article** | 🟢 **Academic Paper** |  **Partial match** |
| **Proposal for the Implementation of DAO...txt** | ⚫ **Business Proposal** | ⚫ **Business Proposal** | 🔵 **Legal Document** (25.9%) | 🔵 **Legal Document** (31.9%) |  **No Match** |
| **Stock Movement and Volatility Prediction...pdf** | 🟢 **Academic Paper** | 🟢 **Academic Paper** | 🟢 **Academic Paper** (23.5%) | 🟢 **Academic Paper** (25.8%) | ✅**Match** |
| **Why Is This C.E.O. Bragging About...pdf** | 🟣 **General Article** | 🟣 **General Article** | 🟣 **General Article** (38.7%) | 🟣 **General Article** (22.8%) |  **Match** |

### **Model Agreement Analysis**

| Model Pair | Agreement Rate | Status | Notes |
|------------|----------------|--------|-------|
| **Gemini 2.5 Flash vs Grok 3** | 7/7 (100%) | **Excellent** | Perfect agreement on all classified documents |
| **BART vs mDeBERTa** | 3/7 (43%) | **Low** | Agreement on: Legal Document, Academic Paper, General Article |
| **Gemini/Grok vs BART** | 3/7 (43%) | **Low** | Agreement on: Legal Document, Academic Paper, General Article |
| **Gemini/Grok vs mDeBERTa** | 3/7 (43%) | **Low** | Agreement on: Legal Document, Academic Paper (×2) |

### **Classification Confidence Analysis**

| Model | Avg Confidence | Performance | Confidence Range |
|-------|----------------|-------------|------------------|
| **Gemini 2.5 Flash** | N/A | **High Accuracy** | External API (no scores) |
| **Grok 3** | N/A | **High Accuracy** | External API (no scores) |
| **BART-Large-MNLI** | ~30.8% | **Low Confidence** | 22.7% - 45.1% |
| **mDeBERTa-v3-Base** | ~27.6% | **Low Confidence** | 22.8% - 31.9% |

### **Key Observations**

1. **Confidence Scores**: All local model classifications show relatively low confidence (22-45%), suggesting potential classification uncertainty
2. **Model Consistency**: Gemini 2.5 Flash and Grok 3 show remarkable consistency, agreeing on all test documents
3. **Local Model Behavior**: BART and mDeBERTa tend to over-classify documents as "Legal Document" with lower confidence
4. **Category Distribution**: External models (Gemini/Grok) provide more diverse category assignments compared to local models

### **Performance Insights**

- **Gemini 2.5 Flash & Grok 3**: Demonstrate strong classification consistency and appear well-calibrated for document type recognition
- **BART-Large-MNLI**: Shows bias toward certain categories but maintains reasonable performance on clear-cut cases
- **mDeBERTa-v3-Base**: Similar patterns to BART with slightly different confidence distributions
- **Confidence Calibration**: Local models may benefit from threshold tuning or ensemble approaches

---

## 🏗️ Architecture Overview

### System Design Decisions

#### **1. Frontend Architecture (React + TypeScript)**
- **Choice**: React 18 with TypeScript and Vite
- **Rationale**: 
  - Type safety prevents runtime errors in complex state management
  - Component-based architecture enables reusable UI elements
  - Vite provides fast development builds and hot module replacement
- **Key Components**:
  - `DocumentUpload`: Single file upload with real-time classification
  - `BulkUpload`: Multi-file upload with concurrent processing visualization
  - `StatisticsDashboard`: Analytics with interactive charts and metrics

#### **2. Backend Architecture (FastAPI + SQLAlchemy)**
- **Choice**: FastAPI with SQLAlchemy ORM and SQLite database
- **Rationale**:
  - FastAPI provides automatic OpenAPI documentation and async support
  - SQLAlchemy ORM enables database-agnostic operations
  - SQLite offers simplicity for development with easy PostgreSQL migration path
- **Key Design Patterns**:
  - Repository pattern for database operations
  - Dependency injection for ML model management
  - Async/await for concurrent file processing

#### **3. ML Model Integration**
- **Choice**: Multiple transformer models via Hugging Face Transformers library
- **Models Selected**:
  - **BART-Large-MNLI**: Fast English classification, optimized for speed
  - **mDeBERTa-v3-Base**: Multilingual support with enhanced accuracy
- **Rationale**:
  - Zero-shot classification eliminates need for custom training data
  - Multiple models provide flexibility for different use cases
  - PyTorch backend ensures GPU acceleration capability

#### **4. Concurrent Processing Strategy**
- **Implementation**: Asyncio with semaphore-controlled concurrency
- **Configuration**: Maximum 3 simultaneous file processes
- **Rationale**: 
  - Prevents memory overflow from large ML model instances
  - Maintains responsiveness while processing multiple documents
  - Balances throughput with system resource constraints

---

## 🛠️ Setup and Installation

### Prerequisites
- **Python 3.8+** (3.9+ recommended for optimal performance)
- **Node.js 16+** and npm
- **Git** for version control
- **Minimum 4GB RAM** (8GB recommended for smooth ML model loading)

### 🐳 Quick Start with Docker (Recommended)

The fastest way to get the application running is using Docker. All dependencies and configurations are handled automatically.

#### Prerequisites for Docker
- **Docker** and **Docker Compose** installed
- **Minimum 4GB RAM** available

#### Start Application
```bash
# Clone repository
git clone https://github.com/wadevs14161/Smart-Document-Classifier.git
cd Smart-Document-Classifier

# Start development environment
cd docker
./docker-helper.sh dev-up

# Alternative: Direct docker-compose command
docker-compose up --build
```

#### Access Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

#### Management Commands
```bash
# Stop all services
./docker-helper.sh dev-down

# View logs
./docker-helper.sh logs

# Production deployment
./docker-helper.sh prod-up
```

### 1. Manual Environment Setup (Alternative)

#### Clone Repository
```bash
git clone https://github.com/wadevs14161/Smart-Document-Classifier.git
cd Smart-Document-Classifier
```

#### Backend Setup
```bash
# Create isolated Python environment
python -m venv .venv-compuj

# Activate virtual environment
# On macOS/Linux:
source .venv-compuj/bin/activate
# On Windows:
.venv-compuj\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

#### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Return to root directory
cd ..
```

### 2. Database Initialization
The SQLite database will be created automatically on first run. For custom setup:
```bash
# Optional: Run database migrations manually
python -c "from backend.database import init_db; init_db()"
```

## 🚀 Running the Application

### Development Mode

#### Start Backend Server
```bash
# Method 1: Using run script (recommended)
python run.py

# Method 2: Direct uvicorn command
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

#### Start Frontend Development Server
```bash
# In a new terminal window
cd frontend
npm run dev
```

### Access Points
- **Web Application**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## 📖 Usage Guide

### 1. Single Document Upload
1. Navigate to "Single Upload" tab
2. Select AI model (BART or mDeBERTa)
3. Drag and drop or click to select file
4. Enable "Auto-classify" for immediate processing
5. View classification results with confidence scores

### 2. Bulk Document Processing
1. Navigate to "Bulk Upload" tab
2. Select AI model for batch processing
3. Upload multiple files (max 10)
4. Monitor individual file progress
5. Review results for each processed document

### 3. Analytics Dashboard
1. Access "Statistics" tab
2. View document type distribution
3. Analyze confidence score patterns
4. Track upload trends and model usage
5. Export data for further analysis

## 🔧 Technical Implementation

### API Endpoints
```
POST /upload          # Single file upload and classification
POST /bulk-upload     # Bulk file processing
GET  /documents       # List all documents
GET  /documents/{id}  # Get specific document
DELETE /documents/{id} # Delete document
POST /documents/{id}/classify # Re-classify with different model
GET  /models          # Available AI models
GET  /health          # System health check
```

### Database Schema
```sql
-- Documents table
CREATE TABLE documents (
    id INTEGER PRIMARY KEY,
    filename VARCHAR(255),
    original_filename VARCHAR(255),
    file_size INTEGER,
    file_type VARCHAR(10),
    upload_date DATETIME,
    extracted_text TEXT,
    classification_result TEXT,
    confidence_score REAL,
    processing_time REAL,
    model_used VARCHAR(100),
    model_key VARCHAR(50),
    model_id VARCHAR(100)
);
```

### File Processing Pipeline
1. **Upload Validation**: File type, size, and format verification
2. **Text Extraction**: 
   - TXT: Direct reading with encoding detection
   - PDF: PyPDF2 extraction with error handling
   - DOCX: python-docx parsing
3. **ML Classification**: Zero-shot classification with selected model
4. **Result Storage**: Database persistence with metadata
5. **Response Generation**: Structured JSON response with confidence scores

---

## 🔮 Future Improvements

### Short-term Enhancements
1. **Enhanced File Support**
   - RTF, ODT document formats
   - Image-based PDF OCR integration
   - Excel/CSV structured data classification

2. **User Experience**
   - Dark/light theme toggle
   - Document preview functionality
   - Advanced filtering and search
   - Export capabilities (CSV, JSON, PDF reports)

3. **Performance Optimization**
   - Redis caching for frequently accessed documents
   - Model warm-up to reduce first-request latency
   - Compressed response payloads

### Medium-term Features
1. **Authentication & Authorization**
   - User registration and login system
   - Role-based access control
   - Document ownership and sharing permissions

2. **Advanced ML Capabilities**
   - Custom category definition
   - Confidence threshold configuration
   - Model fine-tuning interface
   - Document similarity search

3. **Enterprise Features**
   - API rate limiting and quotas
   - Audit logging and compliance tracking
   - Multi-tenant architecture
   - Batch job scheduling with Celery

### Long-term Vision
1. **Scalability Improvements**
   - Kubernetes deployment configuration
   - Horizontal scaling with load balancers
   - Cloud storage integration (AWS S3, Google Cloud)
   - PostgreSQL migration with connection pooling

2. **Advanced Analytics**
   - Machine learning model performance tracking
   - A/B testing framework for model comparison
   - Custom dashboard creation
   - Real-time monitoring and alerting

---

## ⚠️ Challenges Encountered

### 1. **Memory Management with Large ML Models**
**Challenge**: BART-Large-MNLI (407M parameters) caused memory issues during concurrent processing.
**Solution**: Implemented semaphore-controlled concurrency (max 3 simultaneous processes) and proper model cleanup.
**Learning**: Large transformer models require careful resource management in production environments.

### 2. **File Size and Processing Limits**
**Challenge**: Initial 10MB limit caused classification failures for legitimate documents.
**Solution**: Increased limit to 25MB and implemented proper error handling for oversized files.
**Impact**: Improved user experience while maintaining system stability.

### 3. **Database Schema Evolution**
**Challenge**: Adding multi-model support required database migrations without losing existing data.
**Solution**: Created migration scripts with backward compatibility and default values.
**Learning**: Plan database schema changes early to avoid complex migrations.

### 4. **Frontend State Management Complexity**
**Challenge**: Managing upload progress, error states, and real-time updates across multiple components.
**Solution**: Implemented centralized state management with clear data flow patterns.
**Improvement**: Consider Redux or Zustand for more complex state scenarios.

### 5. **Error Handling Consistency**
**Challenge**: Different error types (network, validation, processing) needed unified handling approach.
**Solution**: Standardized error response format across API and implemented comprehensive frontend error boundaries.
**Result**: Improved user experience with clear, actionable error messages.

### 6. **Model Loading Performance**
**Challenge**: Cold start latency when loading transformer models for first classification.
**Solution**: Implemented model pre-loading during application startup.
**Trade-off**: Increased startup time but faster first-request response.
