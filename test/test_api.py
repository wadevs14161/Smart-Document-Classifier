#!/usr/bin/env python3
"""
Test script for the Document Classifier API
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_api():
    print("🧪 Testing Document Classifier API")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test 2: Root endpoint
    print("\n2. Testing root endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Test 3: Get documents (should be empty initially)
    print("\n3. Testing get documents...")
    response = requests.get(f"{BASE_URL}/documents")
    print(f"Status: {response.status_code}")
    print(f"Documents count: {len(response.json())}")
    
    print("\n✅ Basic API tests completed!")
    print(f"📱 Visit {BASE_URL}/interface for the web interface")
    print(f"📚 Visit {BASE_URL}/docs for API documentation")

if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the API. Make sure the server is running on port 8000.")
    except Exception as e:
        print(f"❌ Error: {e}")
