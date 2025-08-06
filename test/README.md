# Test Suite - Smart Document Classifier

This directory contains comprehensive test scripts for the Smart Document Classifier application.

## 🧪 Available Tests

### **test_api.py**
- Tests all API endpoints (/health, /models, /documents, /docs)
- Validates server connectivity and basic functionality
- Quick smoke test to verify the application is working

### **test_upload.py**
- Tests single document upload functionality
- Tests bulk upload processing (up to 10 files)
- Tests both BART and mDeBERTa model selection
- Validates classification results and confidence scores
- Tests document retrieval and re-classification

### **test_error_handling.py**
- Tests various error scenarios and edge cases
- Validates proper HTTP status codes for different errors
- Tests file type validation, size limits, and invalid inputs
- Ensures robust error handling across all endpoints

### **run_all_tests.py**
- Comprehensive test runner that executes all test scripts
- Provides detailed summary report with pass/fail statistics
- Checks server status before running tests
- Generates recommendations based on test results

## 🚀 How to Run Tests

### Prerequisites
Make sure the backend server is running:
```bash
python run.py
```

### Run All Tests
```bash
python test/run_all_tests.py
```

### Run Individual Tests
```bash
# Test API endpoints
python test/test_api.py

# Test upload functionality
python test/test_upload.py

# Test error handling
python test/test_error_handling.py
```

## 📁 Test Files

### **sample_document.txt**
- Sample document used for upload testing
- Contains technical documentation content
- Automatically created if missing

### **Temporary Files**
- Test scripts may create temporary files during bulk upload tests
- These are automatically cleaned up after test completion

## ✅ Expected Results

When all tests pass, you should see:
- ✅ API endpoints responding correctly
- ✅ Document uploads working with both models
- ✅ Bulk upload processing multiple files
- ✅ Proper classification results with confidence scores
- ✅ Robust error handling for invalid inputs
- ✅ Appropriate HTTP status codes for all scenarios

## 🔧 Troubleshooting

### Server Not Running
If tests fail with connection errors:
```bash
# Start the backend server
python run.py

# Then run tests
python test/run_all_tests.py
```

### Missing Dependencies
If import errors occur:
```bash
# Activate virtual environment
source .venv-compuj/bin/activate

# Install requirements
pip install -r requirements.txt
```

### Individual Test Failures
- Check the specific error messages in test output
- Verify API endpoints are working via browser: http://localhost:8000/docs
- Test manually via web interface: http://localhost:3000

## 📊 Test Coverage

The test suite covers:
- ✅ All API endpoints
- ✅ Single and bulk file uploads
- ✅ Both AI models (BART and mDeBERTa)
- ✅ Document operations (retrieve, delete, re-classify)
- ✅ Error scenarios and edge cases
- ✅ File type validation and size limits
- ✅ Model selection and classification accuracy

## 🔮 Future Enhancements

Potential additional tests:
- Performance testing with large files
- Concurrent upload stress testing
- Authentication and authorization tests
- Database integrity and migration tests
- Frontend integration tests
