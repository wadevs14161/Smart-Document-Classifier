#!/usr/bin/env python3
"""
Error handling test script for Smart Document Classifier
Tests various error scenarios to ensure robust error handling
"""
import requests
import json
import os
import tempfile
from io import BytesIO

BASE_URL = "http://localhost:8000"

def test_upload_errors():
    """Test various upload error scenarios"""
    print("🔍 Testing Upload Error Handling")
    print("=" * 50)
    
    # Test 1: Upload without file
    print("\n1. Testing upload without file...")
    try:
        response = requests.post(f"{BASE_URL}/upload")
        print(f"   Status: {response.status_code}")
        if response.status_code in [400, 422]:
            print("   ✅ Correctly rejected upload without file")
        else:
            print(f"   ❌ Unexpected response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Empty file
    print("\n2. Testing empty file upload...")
    try:
        empty_content = b""
        files = {"file": ("empty.txt", BytesIO(empty_content), "text/plain")}
        response = requests.post(f"{BASE_URL}/upload", files=files)
        print(f"   Status: {response.status_code}")
        if response.status_code == 400:
            print("   ✅ Correctly rejected empty file")
        else:
            print(f"   ❌ Unexpected response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Unsupported file type
    print("\n3. Testing unsupported file type...")
    try:
        unsupported_content = b"This is a fake executable file"
        files = {"file": ("malicious.exe", BytesIO(unsupported_content), "application/octet-stream")}
        response = requests.post(f"{BASE_URL}/upload", files=files)
        print(f"   Status: {response.status_code}")
        if response.status_code == 422:
            print("   ✅ Correctly rejected unsupported file type")
        else:
            print(f"   ❌ Unexpected response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Invalid model key
    print("\n4. Testing invalid model key...")
    try:
        valid_content = b"This is a test document for classification."
        files = {"file": ("test.txt", BytesIO(valid_content), "text/plain")}
        data = {"model_key": "invalid-model", "auto_classify": True}
        response = requests.post(f"{BASE_URL}/upload", files=files, data=data)
        print(f"   Status: {response.status_code}")
        if response.status_code in [400, 422]:
            print("   ✅ Correctly rejected invalid model key")
        else:
            print(f"   ❌ Unexpected response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_document_errors():
    """Test document-related error scenarios"""
    print("\n🔍 Testing Document Error Handling")
    print("=" * 50)
    
    # Test 1: Get non-existent document
    print("\n1. Testing get non-existent document...")
    try:
        response = requests.get(f"{BASE_URL}/documents/99999")
        print(f"   Status: {response.status_code}")
        if response.status_code == 404:
            print("   ✅ Correctly returned 404 for non-existent document")
        else:
            print(f"   ❌ Unexpected response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Delete non-existent document
    print("\n2. Testing delete non-existent document...")
    try:
        response = requests.delete(f"{BASE_URL}/documents/99999")
        print(f"   Status: {response.status_code}")
        if response.status_code == 404:
            print("   ✅ Correctly returned 404 for non-existent document")
        else:
            print(f"   ❌ Unexpected response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Classify non-existent document
    print("\n3. Testing classify non-existent document...")
    try:
        data = {"model_key": "bart-large-mnli"}
        response = requests.post(f"{BASE_URL}/documents/99999/classify", json=data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 404:
            print("   ✅ Correctly returned 404 for non-existent document")
        else:
            print(f"   ❌ Unexpected response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_bulk_upload_errors():
    """Test bulk upload error scenarios"""
    print("\n🔍 Testing Bulk Upload Error Handling")
    print("=" * 50)
    
    # Test 1: Bulk upload with no files
    print("\n1. Testing bulk upload with no files...")
    try:
        response = requests.post(f"{BASE_URL}/bulk-upload")
        print(f"   Status: {response.status_code}")
        if response.status_code in [400, 422]:
            print("   ✅ Correctly rejected bulk upload without files")
        else:
            print(f"   ❌ Unexpected response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Bulk upload with mixed valid/invalid files
    print("\n2. Testing bulk upload with mixed file types...")
    try:
        files = [
            ("files", ("valid.txt", BytesIO(b"Valid document content"), "text/plain")),
            ("files", ("invalid.exe", BytesIO(b"Invalid content"), "application/octet-stream"))
        ]
        data = {"model_key": "bart-large-mnli", "auto_classify": True}
        response = requests.post(f"{BASE_URL}/bulk-upload", files=files, data=data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Partial success: {result.get('successful_uploads')} successful, {result.get('failed_uploads')} failed")
        else:
            print(f"   ❌ Unexpected response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_api_limits():
    """Test API limits and edge cases"""
    print("\n🔍 Testing API Limits and Edge Cases")
    print("=" * 50)
    
    # Test 1: Large file (close to limit)
    print("\n1. Testing large file upload...")
    try:
        # Create a 1MB test file (well within 25MB limit)
        large_content = b"A" * (1024 * 1024)  # 1MB
        files = {"file": ("large_test.txt", BytesIO(large_content), "text/plain")}
        data = {"model_key": "bart-large-mnli", "auto_classify": False}  # Skip classification for speed
        response = requests.post(f"{BASE_URL}/upload", files=files, data=data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Large file upload successful")
        else:
            print(f"   ❌ Large file upload failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Very long filename
    print("\n2. Testing very long filename...")
    try:
        long_filename = "a" * 200 + ".txt"
        files = {"file": (long_filename, BytesIO(b"Test content"), "text/plain")}
        response = requests.post(f"{BASE_URL}/upload", files=files)
        print(f"   Status: {response.status_code}")
        if response.status_code in [200, 400]:
            print("   ✅ Long filename handled appropriately")
        else:
            print(f"   ❌ Unexpected response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def main():
    """Main error testing function"""
    print("🧪 Smart Document Classifier - Error Handling Tests")
    print("=" * 60)
    
    test_upload_errors()
    test_document_errors()
    test_bulk_upload_errors()
    test_api_limits()
    
    print("\n" + "=" * 60)
    print("✅ Error handling tests completed!")
    print("💡 All error scenarios should be handled gracefully with appropriate HTTP status codes")

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the API.")
        print("Please make sure the server is running: python run.py")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
