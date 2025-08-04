#!/usr/bin/env python3
"""
ML Document Classification System - Complete Demo
This script demonstrates the full functionality of the BART-Large-MNLI classification system
"""
import requests
import json
import os
from pathlib import Path

BASE_URL = "http://localhost:8000"
DATASET_PATH = "/Users/wenshinluo/Documents/Projects/compu-J/ml/Dataset"

def demo_classification_system():
    print("🚀 FastAPI + BART-Large-MNLI Document Classification Demo")
    print("=" * 70)
    
    # Show system info
    print("\n📋 System Information:")
    print("   🤖 Model: facebook/bart-large-mnli")
    print("   📂 Categories: Technical Documentation, Business Proposal,")
    print("                 Legal Document, Academic Paper, General Article, Other")
    print("   🔄 Auto-classification: Enabled on upload")
    print("   🌐 Web Interface: http://localhost:8000/interface")
    print("   📚 API Docs: http://localhost:8000/docs")
    
    # Get current document count
    response = requests.get(f"{BASE_URL}/documents")
    if response.status_code == 200:
        docs = response.json()
        classified_docs = [d for d in docs if d['is_classified']]
        print(f"\n📊 Current Status:")
        print(f"   📄 Total Documents: {len(docs)}")
        print(f"   ✅ Classified: {len(classified_docs)}")
        print(f"   ❌ Unclassified: {len(docs) - len(classified_docs)}")
        
        if classified_docs:
            print(f"\n🎯 Classification Results:")
            category_counts = {}
            for doc in classified_docs:
                cat = doc['predicted_category']
                category_counts[cat] = category_counts.get(cat, 0) + 1
            
            for category, count in sorted(category_counts.items()):
                print(f"   📁 {category}: {count} document(s)")
    
    # Test classification accuracy with sample documents
    print(f"\n🧪 Testing Classification Accuracy:")
    print("-" * 50)
    
    test_cases = [
        {
            "content": """# API Documentation
            
This is a comprehensive guide for the REST API endpoints:

GET /api/users - Retrieve all users
POST /api/users - Create new user
PUT /api/users/{id} - Update user
DELETE /api/users/{id} - Delete user

Authentication: Bearer token required
Rate limiting: 100 requests per minute""",
            "expected": "Technical Documentation",
            "filename": "api_guide.txt"
        },
        {
            "content": """TERMS OF SERVICE AGREEMENT

1. ACCEPTANCE OF TERMS
By accessing this service, you agree to be bound by these terms.

2. USE LICENSE
Permission is granted to temporarily download one copy of the materials.

3. DISCLAIMER
The materials are provided on an 'as is' basis without warranties.

4. LIMITATIONS
In no event shall the company be liable for any damages.""",
            "expected": "Legal Document",
            "filename": "terms_of_service.txt"
        },
        {
            "content": """Business Proposal: AI-Powered Customer Service Solution

Executive Summary:
We propose implementing an AI chatbot system to improve customer satisfaction and reduce operational costs by 40%.

Market Analysis:
- Customer service inquiries increased 150% last year
- Average response time: 4 hours
- Customer satisfaction: 67%

Proposed Solution:
- 24/7 automated support
- Natural language processing
- Integration with existing CRM

Financial Projections:
- Initial investment: $250,000
- ROI expected within 18 months
- Annual savings: $400,000""",
            "expected": "Business Proposal",
            "filename": "ai_chatbot_proposal.txt"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test_case['filename']}")
        print(f"   Expected: {test_case['expected']}")
        
        # Create temp file and upload
        temp_path = f"/tmp/{test_case['filename']}"
        with open(temp_path, 'w') as f:
            f.write(test_case['content'])
        
        try:
            with open(temp_path, 'rb') as f:
                files = {"file": (test_case['filename'], f, "text/plain")}
                response = requests.post(f"{BASE_URL}/upload", files=files)
            
            if response.status_code == 200:
                result = response.json()
                predicted = result['classification']['predicted_category']
                confidence = result['classification']['confidence_score']
                
                is_correct = predicted == test_case['expected']
                status = "✅ CORRECT" if is_correct else "❌ INCORRECT"
                
                print(f"   Predicted: {predicted} ({confidence:.4f})")
                print(f"   Result: {status}")
            else:
                print(f"   ❌ Upload failed: {response.status_code}")
                
            # Clean up temp file
            os.remove(temp_path)
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n🎉 Demo completed! Visit {BASE_URL}/interface to see all documents.")
    print(f"📖 API documentation available at {BASE_URL}/docs")

def show_available_datasets():
    """Show available test documents in the dataset"""
    print(f"\n📁 Available Test Documents in ml/Dataset/:")
    print("-" * 50)
    
    if os.path.exists(DATASET_PATH):
        files = os.listdir(DATASET_PATH)
        for i, filename in enumerate(sorted(files), 1):
            if filename.endswith('.txt'):
                file_path = os.path.join(DATASET_PATH, filename)
                size = os.path.getsize(file_path)
                print(f"{i:2d}. {filename[:60]}... ({size} bytes)")
    else:
        print("Dataset directory not found!")

if __name__ == "__main__":
    try:
        demo_classification_system()
        show_available_datasets()
        
        print(f"\n💡 Pro Tips:")
        print(f"   • Upload documents via: curl -X POST '{BASE_URL}/upload' -F 'file=@filename.txt'")
        print(f"   • Classify existing document: curl -X POST '{BASE_URL}/documents/{{id}}/classify'")
        print(f"   • Use the web interface for easy document management")
        print(f"   • Check {BASE_URL}/docs for complete API reference")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: API server not running. Start with: uvicorn backend.main:app --reload")
    except Exception as e:
        print(f"❌ Error: {e}")
