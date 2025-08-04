#!/usr/bin/env python3
"""
Test script for ML Classification functionality
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_classification():
    print("🧠 Testing ML Document Classification")
    print("=" * 50)
    
    # Test 1: Get all documents
    print("\n1. Getting all documents...")
    response = requests.get(f"{BASE_URL}/documents")
    if response.status_code == 200:
        documents = response.json()
        print(f"✅ Found {len(documents)} documents")
        
        if documents:
            # Test 2: Classify a document
            doc = documents[-1]  # Get the latest document
            doc_id = doc['id']
            
            print(f"\n2. Testing classification on document {doc_id}: {doc['original_filename']}")
            print(f"   Current classification status: {doc['is_classified']}")
            
            if not doc['is_classified']:
                print("   🔄 Classifying document...")
                response = requests.post(f"{BASE_URL}/documents/{doc_id}/classify")
                
                if response.status_code == 200:
                    result = response.json()
                    print("   ✅ Classification successful!")
                    print(f"   📂 Category: {result['classification_result']['predicted_category']}")
                    print(f"   📊 Confidence: {result['classification_result']['confidence_score']:.4f}")
                    print(f"   ⏱️ Inference Time: {result['classification_result']['inference_time']}s")
                    print(f"   🤖 Model: {result['classification_result']['model_used']}")
                    
                    # Show all category scores
                    print("\n   📈 All Category Scores:")
                    for category, score in result['classification_result']['all_scores'].items():
                        print(f"      {category}: {score:.4f}")
                        
                else:
                    print(f"   ❌ Classification failed: {response.status_code}")
                    print(f"   Error: {response.json()}")
            else:
                print(f"   ✅ Already classified as: {doc['predicted_category']} ({doc['confidence_score']:.4f})")
    else:
        print(f"❌ Failed to get documents: {response.status_code}")
    
    # Test 3: Upload with auto-classification
    print(f"\n3. Testing upload with auto-classification...")
    
    # Create a test document with clear technical content
    test_content = """
# FastAPI Application Architecture

This document describes the technical architecture of a FastAPI web application
for document classification. The system uses:

1. FastAPI framework for REST API endpoints
2. SQLAlchemy ORM for database operations
3. Pydantic for data validation and serialization
4. BART-Large-MNLI model for zero-shot classification
5. Uvicorn ASGI server for deployment

## Technical Components

### Backend Architecture
- Python 3.12+ environment
- Async/await pattern for non-blocking operations
- Database migrations and schema management
- File upload handling with multiple format support

### Machine Learning Pipeline
- Transformers library integration
- Token-based text processing
- Confidence scoring and multi-class classification
- Performance optimization for production use
    """
    
    with open('/tmp/test_technical_doc.txt', 'w') as f:
        f.write(test_content)
    
    with open('/tmp/test_technical_doc.txt', 'rb') as f:
        files = {"file": ("technical_architecture.txt", f, "text/plain")}
        response = requests.post(f"{BASE_URL}/upload", files=files)
    
    if response.status_code == 200:
        result = response.json()
        print("   ✅ Upload successful!")
        print(f"   📄 Document ID: {result['document_id']}")
        
        if 'classification' in result:
            print("   🤖 Auto-Classification Results:")
            print(f"      📂 Category: {result['classification']['predicted_category']}")
            print(f"      📊 Confidence: {result['classification']['confidence_score']:.4f}")
        else:
            print("   ⚠️ No auto-classification performed")
    else:
        print(f"   ❌ Upload failed: {response.status_code}")
        print(f"   Error: {response.json()}")
    
    print(f"\n4. Testing API endpoints summary...")
    print(f"   📱 Web Interface: {BASE_URL}/interface")
    print(f"   📚 API Docs: {BASE_URL}/docs")
    
    print(f"\n✅ ML Classification testing completed!")

if __name__ == "__main__":
    try:
        test_classification()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the API. Make sure the server is running on port 8000.")
    except Exception as e:
        print(f"❌ Error: {e}")
