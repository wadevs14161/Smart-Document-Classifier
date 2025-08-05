#!/usr/bin/env python3
"""
Comprehensive error handling test script for Smart Document Classifier
Tests various error scenarios to ensure robust error handling
"""

import requests
import json
import os
import tempfile
from io import BytesIO

API_BASE_URL = "http://localhost:8000"

def test_upload_errors():
    """Test various upload error scenarios"""
    print("🔍 Testing Upload Error Handling...")
    
    # Test 1: No file provided
    print("\n1. Testing empty upload...")
    try:
        response = requests.post(f"{API_BASE_URL}/upload")
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Error: {response.json()}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Test 2: Empty file
    print("\n2. Testing empty file...")
    try:
        empty_file = BytesIO(b"")
        files = {'file': ('empty.txt', empty_file, 'text/plain')}
        response = requests.post(f"{API_BASE_URL}/upload", files=files)
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Error: {response.json()}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Test 3: Unsupported file type
    print("\n3. Testing unsupported file type...")
    try:
        fake_image = BytesIO(b"fake image content")
        files = {'file': ('test.jpg', fake_image, 'image/jpeg')}
        response = requests.post(f"{API_BASE_URL}/upload", files=files)
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Error: {response.json()}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Test 4: Large file (> 10MB)
    print("\n4. Testing oversized file...")
    try:
        large_content = b"x" * (11 * 1024 * 1024)  # 11MB
        large_file = BytesIO(large_content)
        files = {'file': ('large.txt', large_file, 'text/plain')}
        response = requests.post(f"{API_BASE_URL}/upload", files=files)
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Error: {response.json()}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Test 5: Corrupted PDF
    print("\n5. Testing corrupted PDF...")
    try:
        fake_pdf = BytesIO(b"This is not a real PDF file")
        files = {'file': ('corrupted.pdf', fake_pdf, 'application/pdf')}
        response = requests.post(f"{API_BASE_URL}/upload", files=files)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Test 6: File with no readable content
    print("\n6. Testing file with only whitespace...")
    try:
        whitespace_file = BytesIO(b"   \n\n\t\t   \n   ")
        files = {'file': ('whitespace.txt', whitespace_file, 'text/plain')}
        response = requests.post(f"{API_BASE_URL}/upload", files=files)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Exception: {e}")

def test_api_errors():
    """Test API endpoint error scenarios"""
    print("\n🔍 Testing API Error Handling...")
    
    # Test 1: Non-existent document
    print("\n1. Testing non-existent document...")
    try:
        response = requests.get(f"{API_BASE_URL}/documents/99999")
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Error: {response.json()}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Test 2: Invalid document ID
    print("\n2. Testing invalid document ID...")
    try:
        response = requests.get(f"{API_BASE_URL}/documents/-1")
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Error: {response.json()}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Test 3: Invalid pagination parameters
    print("\n3. Testing invalid pagination...")
    try:
        response = requests.get(f"{API_BASE_URL}/documents?skip=-1&limit=0")
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Error: {response.json()}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Test 4: Delete non-existent document
    print("\n4. Testing delete non-existent document...")
    try:
        response = requests.delete(f"{API_BASE_URL}/documents/99999")
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Error: {response.json()}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Test 5: Classify non-existent document
    print("\n5. Testing classify non-existent document...")
    try:
        response = requests.post(f"{API_BASE_URL}/documents/99999/classify")
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Error: {response.json()}")
    except Exception as e:
        print(f"   Exception: {e}")

def test_health_check():
    """Test health check endpoint"""
    print("\n🔍 Testing Health Check...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Exception: {e}")

def test_successful_upload():
    """Test a successful upload to ensure system is working"""
    print("\n✅ Testing Successful Upload...")
    try:
        test_content = "This is a test document for classification testing."
        test_file = BytesIO(test_content.encode())
        files = {'file': ('test_success.txt', test_file, 'text/plain')}
        response = requests.post(f"{API_BASE_URL}/upload", files=files)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Success: {result['message']}")
            if 'classification' in result:
                print(f"   Classification: {result['classification']['predicted_category']}")
                print(f"   Confidence: {result['classification']['confidence_score']:.3f}")
            if 'warnings' in result:
                print(f"   Warnings: {result['warnings']}")
        else:
            print(f"   Error: {response.json()}")
    except Exception as e:
        print(f"   Exception: {e}")

def main():
    """Run all error handling tests"""
    print("🚀 Starting Error Handling Test Suite")
    print("=" * 50)
    
    # Check if API is running
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print(f"❌ API health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to API at {API_BASE_URL}")
        print(f"   Make sure the backend server is running")
        print(f"   Error: {e}")
        return
    
    print("✅ API is running")
    
    # Run tests
    test_health_check()
    test_upload_errors()
    test_api_errors()
    test_successful_upload()
    
    print("\n" + "=" * 50)
    print("🏁 Error Handling Test Suite Complete")

if __name__ == "__main__":
    main()
