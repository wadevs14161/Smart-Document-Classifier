#!/usr/bin/env python3
"""
Test the updated ML classifier with proper tokenizer-based truncation
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from backend.ml_classifier import classify_document_text

def test_truncation():
    print("🧪 Testing Updated ML Classifier with Tokenizer-Based Truncation")
    print("=" * 70)
    
    # Test with a long document that will need truncation
    long_document = """
    COMPREHENSIVE TECHNICAL DOCUMENTATION - API DEVELOPMENT GUIDE
    
    This extensive technical documentation covers the implementation of a sophisticated 
    FastAPI web application designed for intelligent document classification using 
    state-of-the-art machine learning models.
    
    ARCHITECTURE OVERVIEW:
    The system employs a modular, scalable architecture consisting of several key components:
    
    1. FastAPI Framework Integration
    - RESTful API design patterns
    - Asynchronous request handling
    - Automatic OpenAPI documentation generation
    - CORS middleware configuration
    - Request/response validation using Pydantic models
    
    2. Database Layer Implementation
    - SQLAlchemy ORM for object-relational mapping
    - SQLite database for development and testing
    - Automated schema migrations
    - Connection pooling and optimization
    - Transaction management and rollback capabilities
    
    3. Document Processing Pipeline
    - Multi-format document support (TXT, PDF, DOCX)
    - Asynchronous file processing using aiofiles
    - Text extraction and preprocessing
    - Content validation and sanitization
    - Error handling and recovery mechanisms
    
    4. Machine Learning Integration
    - Facebook BART-Large-MNLI model implementation
    - Zero-shot classification capabilities
    - Token-based text preprocessing
    - Confidence scoring and result ranking
    - Performance optimization and caching
    
    5. Security and Authentication
    - Input validation and sanitization
    - File upload security measures
    - Rate limiting and DDoS protection
    - Logging and audit trail implementation
    - Error handling without information disclosure
    
    IMPLEMENTATION DETAILS:
    The core application logic is structured around several interconnected modules
    that work together to provide seamless document classification capabilities.
    Each module is designed with separation of concerns in mind, ensuring
    maintainability, testability, and scalability.
    
    PERFORMANCE CONSIDERATIONS:
    For production deployment, several optimization strategies should be considered:
    - Model caching and singleton patterns to reduce memory overhead
    - Asynchronous processing queues for handling multiple requests
    - Database connection pooling and query optimization
    - CDN integration for static asset delivery
    - Load balancing and horizontal scaling capabilities
    
    DEPLOYMENT AND MONITORING:
    The application supports various deployment scenarios including:
    - Containerized deployment using Docker
    - Cloud platform integration (AWS, GCP, Azure)
    - Kubernetes orchestration and auto-scaling
    - Health checks and monitoring integration
    - Logging and metrics collection
    
    CONCLUSION:
    This comprehensive technical documentation provides the foundation for
    implementing a robust, scalable document classification system using
    modern web technologies and machine learning capabilities.
    """ * 3  # Make it really long to test truncation
    
    print(f"📄 Testing with document: {len(long_document)} characters")
    print("🔄 Classifying...")
    
    try:
        result = classify_document_text(long_document)
        
        print("\n✅ Classification Results:")
        print(f"   📂 Category: {result['predicted_category']}")
        print(f"   📊 Confidence: {result['confidence_score']:.4f}")
        print(f"   ⏱️  Inference Time: {result['inference_time']}s")
        print(f"   📝 Text Length (chars): {result['text_length_chars']}")
        print(f"   🔤 Text Length (tokens): {result['text_length_tokens']}")
        print(f"   ✂️  Was Truncated: {result['was_truncated']}")
        
        if 'original_token_count' in result:
            print(f"   📏 Original Token Count: {result['original_token_count']}")
        
        print(f"\n📈 All Category Scores:")
        for category, score in result['all_scores'].items():
            print(f"      {category}: {score:.4f}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_truncation()
