# Smart Document Classifier Web Application

A full-stack web application for document upload, text extraction, and AI-powered classification using multiple state-of-the-art deep learning models with bulk processing capabilities.

## 🚀 Key Features

- **Multi-Model AI Classification**: Choose between BART-Large-MNLI (407M parameters) and mDeBERTa-v3-Base (279M parameters) for zero-shot document classification
- **Bulk Upload Processing**: Upload up to 10 files simultaneously with concurrent processing
- **Statistics Dashboard**: Comprehensive analytics with charts showing document distribution, confidence scores, and upload trends
- **Document Support**: TXT, PDF, and DOCX files up to 25MB each
- **Deep Learning Powered**: PyTorch-based transformer neural networks for intelligent document understanding
- **Modern UI**: React TypeScript frontend with responsive design and drag-and-drop interface
- **RESTful API**: FastAPI backend with comprehensive error handling

## 🤖 AI Classification

The application uses **deep learning-powered zero-shot classification** with transformer neural networks:

### Available Models:
1. **BART-Large-MNLI**: 407M parameter transformer for fast English document classification
2. **mDeBERTa-v3-Base**: 279M parameter multilingual model supporting 100+ languages

### Document Categories:
- Technical Documentation
- Business Proposal  
- Academic Paper
- Legal Document
- General Article
- Other

## �️ Tech Stack

**Frontend:** React 18, TypeScript, Vite, CSS3  
**Backend:** FastAPI, SQLAlchemy, SQLite, PyTorch  
**AI/ML:** Transformers, BART-Large-MNLI, mDeBERTa-v3-Base

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Git

### 1. Clone and Setup Backend
```bash
git clone <repository-url>
cd compu-J

# Create virtual environment
python -m venv .venv-compuj
source .venv-compuj/bin/activate

# Install dependencies and start backend
pip install -r requirements.txt
python run.py
```

### 2. Setup Frontend
```bash
cd frontend
npm install
npm run dev
```

### 3. Access Application
- **Frontend**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs

## 📊 Application Interface

The application features three main tabs:

1. **Single Upload**: Individual document upload with real-time classification
2. **Bulk Upload**: Process up to 10 files simultaneously
3. **Statistics**: Analytics dashboard with document insights and trends

## 🔮 Future Enhancements

- User authentication and document ownership
- Advanced search and filtering capabilities
- Export functionality for classification results
- Enhanced Celery integration for high-volume processing (1000+ documents)
- WebSocket support for real-time progress updates

## 📄 Project Information

This project demonstrates a complete full-stack implementation with modern technologies, showcasing:
- Deep learning integration with multiple AI models
- Concurrent processing and bulk operations
- Comprehensive analytics and data visualization
- Modern React development with TypeScript
- RESTful API design with FastAPI

Developed as part of a technical assessment for CompuJ, featuring advanced AI document classification capabilities.