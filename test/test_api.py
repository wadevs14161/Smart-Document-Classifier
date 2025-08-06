#!/usr/bin/env python3
"""
Comprehensive API test script for Smart Document Classifier
Tests all current API endpoints with proper error handling
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_api():
    print("🧪 Testing Smart Document Classifier API")
    print("=" * 60)
    
    # Test 1: Health check
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
            print("   ✅ Health check passed")
        else:
            print("   ❌ Health check failed")
    except requests.exceptions.ConnectionError:
        print("   ❌ Server not running. Please start with: python run.py")
        return False
    
    # Test 2: Get available models
    print("\n2. Testing available models...")
    try:
        response = requests.get(f"{BASE_URL}/models")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            models = response.json()
            print(f"   Available models: {list(models['models'].keys())}")
            print("   ✅ Models endpoint working")
        else:
            print("   ❌ Models endpoint failed")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Get documents (should work even if empty)
    print("\n3. Testing get documents...")
    try:
        response = requests.get(f"{BASE_URL}/documents")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            documents = response.json()
            print(f"   Documents count: {len(documents)}")
            print("   ✅ Documents endpoint working")
        else:
            print("   ❌ Documents endpoint failed")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: API Documentation accessibility
    print("\n4. Testing API documentation...")
    try:
        response = requests.get(f"{BASE_URL}/docs")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ API documentation accessible")
        else:
            print("   ❌ API documentation not accessible")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Basic API tests completed!")
    print(f"🌐 Web Application: http://localhost:3000")
    print(f"📚 API Documentation: {BASE_URL}/docs")
    print(f"🔍 Alternative Docs: {BASE_URL}/redoc")
    return True

if __name__ == "__main__":
    test_api()
