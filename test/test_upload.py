#!/usr/bin/env python3
"""
Test document upload functionality
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_upload():
    print("📤 Testing Document Upload")
    print("=" * 40)
    
    # Test upload with sample document
    print("\n1. Uploading sample document...")
    
    with open("sample_document.txt", "rb") as f:
        files = {"file": ("sample_document.txt", f, "text/plain")}
        response = requests.post(f"{BASE_URL}/upload", files=files)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Upload successful!")
        print(f"Document ID: {result['document_id']}")
        print(f"File size: {result['file_size']} bytes")
        print(f"Content preview: {result['content_preview'][:100]}...")
        
        # Test getting the uploaded document
        doc_id = result['document_id']
        print(f"\n2. Retrieving document {doc_id}...")
        response = requests.get(f"{BASE_URL}/documents/{doc_id}")
        if response.status_code == 200:
            doc = response.json()
            print(f"✅ Document retrieved successfully!")
            print(f"Original filename: {doc['original_filename']}")
            print(f"File type: {doc['file_type']}")
            print(f"Upload time: {doc['upload_timestamp']}")
        else:
            print(f"❌ Error retrieving document: {response.status_code}")
    else:
        print(f"❌ Upload failed: {response.status_code}")
        print(f"Error: {response.json()}")
    
    # Test getting all documents
    print(f"\n3. Getting all documents...")
    response = requests.get(f"{BASE_URL}/documents")
    if response.status_code == 200:
        documents = response.json()
        print(f"✅ Found {len(documents)} documents")
        for doc in documents:
            print(f"  - {doc['original_filename']} ({doc['file_type']}) - {doc['file_size']} bytes")
    else:
        print(f"❌ Error getting documents: {response.status_code}")

if __name__ == "__main__":
    try:
        test_upload()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the API. Make sure the server is running on port 8000.")
    except FileNotFoundError:
        print("❌ Error: sample_document.txt not found. Make sure it exists in the current directory.")
    except Exception as e:
        print(f"❌ Error: {e}")
