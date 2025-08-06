# Smart Document Classifier Web Application

A full-stack web application for document upload, text extraction, and AI-powered classification using multiple state-of-the-art deep learning models with bulk processing capabilities.

## 🚀 Key Features

- **Zero-Shot Document Classification**: Classify documents instantly without any custom training. The application leverages powerful pretrained models to categorize documents into predefined categories.
- **Multiple Model Support**: Choose from two robust transformer-based models:
    - **BART-Large-MNLI** (407M parameters): Ideal for fast and accurate English document classification.
    - **mDeBERTa-v3-Base-MNLI-XNLI** (279M parameters): A multilingual model capable of classifying documents in over 100 languages.
- **Statistics Dashboard**: An intuitive dashboard to visualize and analyze classification outcomes and performance metrics.

## 📄 Document Categories

The application is pre-configured to classify documents into the following categories:

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
