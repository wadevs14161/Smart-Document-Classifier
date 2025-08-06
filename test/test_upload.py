#!/usr/bin/env python3
"""
Comprehensive upload test script for Smart Document Classifier
Tests single upload, bulk upload, and model selection functionality
"""
import requests
import json
import os
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_single_upload():
    """Test single document upload functionality"""
    print("📤 Testing Single Document Upload")
    print("=" * 50)
    
    # Check if sample document exists
    sample_file = "test/sample_document.txt"
    if not os.path.exists(sample_file):
        print("❌ Sample document not found. Creating one...")
        with open(sample_file, "w") as f:
            f.write("""
Technical Documentation: FastAPI Implementation Guide

This comprehensive guide covers the implementation of a FastAPI web application 
for document classification using machine learning models.

## Architecture Overview
The system uses a modular architecture with the following components:
- FastAPI framework for REST API endpoints
- SQLAlchemy ORM for database operations  
- Pydantic models for data validation
- BART-Large-MNLI for document classification
- React frontend for user interface

## Key Features
- Zero-shot document classification
- Multi-model support (BART and mDeBERTa)
- Bulk upload processing
- Real-time analytics dashboard
- Responsive web interface

This guide provides step-by-step instructions for setup and deployment.
            """)
    
    # Test upload with BART model
    print("\n1. Testing upload with BART model...")
    try:
        with open(sample_file, "rb") as f:
            files = {"file": ("sample_document.txt", f, "text/plain")}
            data = {
                "model_key": "bart-large-mnli",
                "auto_classify": True
            }
            response = requests.post(f"{BASE_URL}/upload", files=files, data=data)
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Upload successful!")
            print(f"   Document ID: {result.get('document_id')}")
            print(f"   Classification: {result.get('classification', {}).get('predicted_category')}")
            print(f"   Confidence: {result.get('classification', {}).get('confidence_score', 0):.4f}")
            return result.get('document_id')
        else:
            print(f"   ❌ Upload failed: {response.text}")
            return None
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def test_bulk_upload():
    """Test bulk document upload functionality"""
    print("\n📦 Testing Bulk Document Upload")
    print("=" * 50)
    
    # Create test files
    test_files = []
    for i in range(3):
        filename = f"test/bulk_test_{i+1}.txt"
        content = f"""
Document {i+1}: Business Proposal

This is a sample business proposal document for testing bulk upload functionality.
It contains business-related content to test the classification accuracy.

Proposal Summary:
- Project scope and objectives
- Timeline and deliverables  
- Budget and resource allocation
- Risk assessment and mitigation
- Expected outcomes and benefits

This document should be classified as a Business Proposal.
        """
        with open(filename, "w") as f:
            f.write(content)
        test_files.append(filename)
    
    # Test bulk upload
    print(f"\n1. Testing bulk upload with {len(test_files)} files...")
    try:
        files = []
        for filename in test_files:
            files.append(("files", (os.path.basename(filename), open(filename, "rb"), "text/plain")))
        
        data = {
            "model_key": "mdeberta-v3-base",
            "auto_classify": True
        }
        
        response = requests.post(f"{BASE_URL}/bulk-upload", files=files, data=data)
        
        # Close file handles
        for _, (_, file_handle, _) in files:
            file_handle.close()
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Bulk upload successful!")
            print(f"   Total files: {result.get('total_files')}")
            print(f"   Successful: {result.get('successful_uploads')}")
            print(f"   Failed: {result.get('failed_uploads')}")
            print(f"   Processing time: {result.get('processing_time', 0):.2f}s")
            
            # Show individual results
            for file_result in result.get('results', [])[:3]:  # Show first 3
                print(f"   📄 {file_result.get('filename')}: {file_result.get('status')}")
                if file_result.get('classification'):
                    print(f"      Category: {file_result['classification']['predicted_category']}")
        else:
            print(f"   ❌ Bulk upload failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    finally:
        # Cleanup test files
        for filename in test_files:
            if os.path.exists(filename):
                os.remove(filename)

def test_document_operations(doc_id):
    """Test document retrieval and operations"""
    if not doc_id:
        print("\n⚠️  Skipping document operations - no document ID available")
        return
    
    print(f"\n🔍 Testing Document Operations (ID: {doc_id})")
    print("=" * 50)
    
    # Test get specific document
    print(f"\n1. Testing get document {doc_id}...")
    try:
        response = requests.get(f"{BASE_URL}/documents/{doc_id}")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            document = response.json()
            print("   ✅ Document retrieval successful!")
            print(f"   Filename: {document.get('original_filename')}")
            print(f"   File type: {document.get('file_type')}")
            print(f"   Classification: {document.get('predicted_category')}")
        else:
            print(f"   ❌ Document retrieval failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test re-classification
    print(f"\n2. Testing re-classification with different model...")
    try:
        data = {"model_key": "mdeberta-v3-base"}
        response = requests.post(f"{BASE_URL}/documents/{doc_id}/classify", json=data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Re-classification successful!")
            print(f"   New category: {result.get('predicted_category')}")
            print(f"   Confidence: {result.get('confidence_score', 0):.4f}")
        else:
            print(f"   ❌ Re-classification failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def main():
    """Main test function"""
    print("🧪 Smart Document Classifier - Upload Tests")
    print("=" * 60)
    
    # Test single upload
    doc_id = test_single_upload()
    
    # Test bulk upload
    test_bulk_upload()
    
    # Test document operations
    test_document_operations(doc_id)
    
    print("\n" + "=" * 60)
    print("✅ Upload tests completed!")
    print("💡 Check the web interface at http://localhost:3000 for visual testing")

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the API.")
        print("Please make sure the server is running: python run.py")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
