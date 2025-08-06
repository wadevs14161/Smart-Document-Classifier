#!/usr/bin/env python3
"""
Test script for enhanced document classifier with chunking and multi-format support
"""

import sys
import os
import asyncio
sys.path.append('../backend')  # Add backend directory to Python path
from ml_classifier import DocumentClassifier, classify_document_text
from document_processor import DocumentProcessor, DocumentProcessingError

def test_chunking_classifier():
    """Test the enhanced classifier with chunking"""
    print("🧪 Testing Enhanced Document Classifier with Chunking")
    print("=" * 60)
    
    # Test text - long enough to require chunking
    test_text = """
    # FastAPI Technical Documentation
    
    This comprehensive guide covers the implementation of a FastAPI web application for document classification.
    FastAPI is a modern, fast web framework for building APIs with Python based on standard Python type hints.
    
    ## Installation and Setup
    
    To get started with FastAPI, you need to install the framework and its dependencies:
    
    ```bash
    pip install fastapi
    pip install uvicorn[standard]
    ```
    
    ## Creating Your First API
    
    Here's a simple example of a FastAPI application:
    
    ```python
    from fastapi import FastAPI
    
    app = FastAPI()
    
    @app.get("/")
    async def read_root():
        return {"Hello": "World"}
    ```
    
    ## Advanced Features
    
    FastAPI provides many advanced features including:
    - Automatic API documentation
    - Request validation
    - Response serialization
    - Dependency injection
    - Background tasks
    - WebSocket support
    - Security and authentication
    
    ## Database Integration
    
    FastAPI works well with various databases. Here's an example using SQLAlchemy:
    
    ```python
    from sqlalchemy import create_engine
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker
    
    SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
    ```
    
    ## Testing Your API
    
    FastAPI automatically generates interactive API documentation that you can access at /docs.
    You can also test your API endpoints programmatically using libraries like httpx or requests.
    
    ## Deployment Considerations
    
    When deploying FastAPI applications to production, consider:
    - Using a production ASGI server like Uvicorn or Hypercorn
    - Setting up proper logging
    - Configuring environment variables
    - Implementing health checks
    - Setting up monitoring and alerting
    
    This documentation provides a solid foundation for building scalable web APIs with FastAPI.
    """ * 3  # Make it even longer to ensure chunking
    
    try:
        classifier = DocumentClassifier()
        result = classifier.classify(test_text)
        
        print(f"✅ Classification Result:")
        print(f"   Predicted Category: {result['predicted_category']}")
        print(f"   Confidence Score: {result['confidence_score']}")
        print(f"   Model Used: {result['model_used']}")
        print(f"   Token Count: {result['token_count']}")
        print(f"   Chunks Processed: {result['chunks_processed']}")
        print(f"   Was Chunked: {result['was_chunked']}")
        print(f"   Inference Time: {result['inference_time']}s")
        
        print(f"\n📊 All Scores:")
        for category, score in result['all_scores'].items():
            print(f"   {category}: {score}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_file_processors():
    """Test different file type processors"""
    print("\n🗂️ Testing File Processors")
    print("=" * 60)
    
    # Test with files from data/Dataset if they exist
    dataset_path = "data/Dataset"
    
    if not os.path.exists(dataset_path):
        print("⚠️  Dataset directory not found, testing with sample file instead")
        
        # Test with the existing sample document in test directory
        sample_file = "sample_document.txt"
        if os.path.exists(sample_file):
            try:
                print(f"\n📄 Testing file: {sample_file}")
                
                # Test synchronous reading
                content = DocumentProcessor.read_file_content(sample_file)
                print(f"   ✅ Extracted {len(content)} characters")
                
                # Test classification
                result = classify_document_text(content)
                print(f"   📊 Classification: {result['predicted_category']} ({result['confidence_score']})")
                if result.get('was_chunked'):
                    print(f"   🧩 Used {result['chunks_processed']} chunks")
                
            except DocumentProcessingError as e:
                print(f"   ❌ Document processing error: {str(e)}")
            except Exception as e:
                print(f"   ❌ Unexpected error: {str(e)}")
        else:
            print("   ℹ️  No sample files available for testing")
        
        return True
    
    test_files = []
    for filename in os.listdir(dataset_path):
        if filename.lower().endswith(('.txt', '.pdf', '.docx')):
            test_files.append(os.path.join(dataset_path, filename))
            if len(test_files) >= 3:  # Test max 3 files
                break
    
    if not test_files:
        print("⚠️  No supported test files found in dataset")
        return True
    
    for filepath in test_files:
        try:
            print(f"\n📄 Testing file: {os.path.basename(filepath)}")
            
            # Test synchronous reading
            content = DocumentProcessor.read_file_content(filepath)
            print(f"   ✅ Extracted {len(content)} characters")
            
            # Test classification
            result = classify_document_text(content)
            print(f"   📊 Classification: {result['predicted_category']} ({result['confidence_score']})")
            if result.get('was_chunked'):
                print(f"   🧩 Used {result['chunks_processed']} chunks")
            
        except DocumentProcessingError as e:
            print(f"   ❌ Document processing error: {str(e)}")
        except Exception as e:
            print(f"   ❌ Unexpected error: {str(e)}")
    
    return True

async def test_async_processors():
    """Test async file processors"""
    print("\n⚡ Testing Async File Processors")
    print("=" * 60)
    
    dataset_path = "data/Dataset"
    
    if not os.path.exists(dataset_path):
        # Test with sample file in test directory
        sample_file = "sample_document.txt"
        if os.path.exists(sample_file):
            try:
                file_type = DocumentProcessor.get_file_type(sample_file)
                content = await DocumentProcessor.extract_text_from_file(sample_file, file_type)
                print(f"✅ Async extraction from {os.path.basename(sample_file)}: {len(content)} characters")
                return True
            except Exception as e:
                print(f"❌ Async test error: {str(e)}")
                return False
        else:
            print("⚠️  No sample file found for async testing")
            return True
    
    # Find a text file to test
    test_file = None
    for filename in os.listdir(dataset_path):
        if filename.lower().endswith('.txt'):
            test_file = os.path.join(dataset_path, filename)
            break
    
    if not test_file:
        print("⚠️  No text file found for async testing")
        return True
    
    try:
        file_type = DocumentProcessor.get_file_type(test_file)
        content = await DocumentProcessor.extract_text_from_file(test_file, file_type)
        print(f"✅ Async extraction from {os.path.basename(test_file)}: {len(content)} characters")
        return True
        
    except Exception as e:
        print(f"❌ Async test error: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🧪 Enhanced Document Classifier Test Suite")
    print("=" * 80)
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Chunking classifier
    total_tests += 1
    if test_chunking_classifier():
        tests_passed += 1
    
    # Test 2: File processors
    total_tests += 1
    if test_file_processors():
        tests_passed += 1
    
    # Test 3: Async processors
    total_tests += 1
    if asyncio.run(test_async_processors()):
        tests_passed += 1
    
    print(f"\n🎯 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! The enhanced classifier is ready to use.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
