# Error Handling Documentation

## Overview

The Smart Document Classifier implements comprehensive error handling across all layers of the application to provide a robust user experience. This document outlines the error handling strategies and implementations.

## Error Handling Layers

### 1. Frontend Validation (First Line of Defense)

#### File Type Validation
- **HTML `accept` attribute**: Browser-level filtering in file picker
- **JavaScript validation**: Multi-layered file type checking
- **Drag & drop validation**: Validates files dropped into upload area
- **Upload safety check**: Final validation before API call

#### Client-Side Error Display
- **Immediate feedback**: Real-time validation messages
- **User-friendly messages**: Clear, actionable error descriptions
- **Visual indicators**: Color-coded status messages (success/warning/error)

### 2. Backend API Error Handling

#### Request Validation
```python
# File size validation
if file_size > max_size:
    raise HTTPException(status_code=413, detail="File too large...")

# File type validation  
if not DocumentProcessor.is_supported_file_type(file_type):
    raise HTTPException(status_code=422, detail={
        "error": "Unsupported file type",
        "message": "File type 'xyz' is not supported...",
        "supported_types": ["txt", "pdf", "docx", "doc"]
    })
```

#### Document Processing Errors
- **File integrity validation**: Checks file existence, size, and format
- **Encoding detection**: Multiple encoding attempts for text files
- **Corruption handling**: Graceful handling of corrupted PDFs/DOCX files
- **Content extraction**: Fallback mechanisms for text extraction failures

#### Database Error Handling
- **Transaction rollback**: Automatic cleanup on database failures
- **File cleanup**: Removes uploaded files if database save fails
- **Connection errors**: Proper SQLAlchemy error handling

#### Classification Error Handling
- **ML model failures**: Non-blocking classification errors
- **Timeout handling**: Graceful handling of long-running operations
- **Memory management**: Proper resource cleanup

### 3. Error Response Structure

#### Successful Upload with Warnings
```json
{
  "message": "Document uploaded successfully",
  "document_id": 123,
  "filename": "document.pdf",
  "file_size": 1024,
  "warnings": [
    "No readable text content found in the document",
    "Classification failed: insufficient content"
  ],
  "classification": null
}
```

#### Error Response Format
```json
{
  "detail": {
    "error": "Unsupported file type",
    "message": "File type 'jpg' is not supported. Please upload TXT, PDF, or DOCX files.",
    "supported_types": ["txt", "pdf", "docx", "doc"]
  }
}
```

## HTTP Status Codes

| Code | Meaning | Use Case |
|------|---------|----------|
| 200 | Success | Successful operations (may include warnings) |
| 400 | Bad Request | Invalid parameters, empty files, invalid IDs |
| 404 | Not Found | Document not found, endpoint not found |
| 413 | Payload Too Large | File exceeds maximum size limit (10MB) |
| 422 | Unprocessable Entity | Unsupported file types, validation failures |
| 500 | Internal Server Error | Unexpected server errors, database failures |

## Frontend Error Handling

### Upload Component Error States
```typescript
// Network error handling
if (error.code === 'NETWORK_ERROR' || !error.response) {
  errorMessage += 'Network error. Please check your connection.';
}

// Status-specific error handling
if (error.response?.status === 413) {
  errorMessage += 'File too large. Maximum size allowed is 10MB.';
} else if (error.response?.status === 422) {
  // Handle validation errors with detailed messages
}
```

### Document List Error States
- **Loading states**: Visual feedback during data fetching
- **Error boundaries**: Graceful fallback for component failures
- **Retry mechanisms**: User-initiated retry buttons
- **Optimistic updates**: UI updates with rollback on failure

## Error Logging

### Backend Logging
```python
# Structured logging with different levels
logger.info("Document uploaded successfully")
logger.warning("Classification failed but upload succeeded")
logger.error("Database error occurred", exc_info=True)
```

### Frontend Logging
```typescript
// Console logging for debugging
console.error('Upload failed:', error);
console.warn('Upload warnings:', warningMessages);
```

## Error Recovery Strategies

### Automatic Recovery
- **File cleanup**: Removes partial uploads on failure
- **Database rollback**: Maintains data consistency
- **Resource cleanup**: Frees memory and file handles

### User-Initiated Recovery
- **Retry buttons**: Allow users to retry failed operations
- **Refresh mechanisms**: Reload data on network failures
- **Clear error states**: Reset UI to initial state

### Graceful Degradation
- **Classification failures**: Upload succeeds even if classification fails
- **Partial content**: Extract available text even from problematic files
- **Warning system**: Inform users of issues without blocking workflow

## Testing Error Scenarios

The application includes comprehensive error testing:

```bash
# Run error handling test suite
python test/test_error_handling.py
```

### Test Coverage
- Empty file uploads
- Oversized files (>10MB)
- Unsupported file types
- Corrupted files
- Network failures
- Database errors
- Invalid API parameters
- Non-existent resources

## Best Practices

### For Developers
1. **Always validate input**: Check parameters before processing
2. **Use specific HTTP status codes**: Match the error type appropriately
3. **Provide actionable messages**: Tell users what went wrong and how to fix it
4. **Log errors properly**: Include context and stack traces
5. **Clean up resources**: Ensure no resource leaks on errors
6. **Test error paths**: Verify error handling works as expected

### For Users
1. **Check file types**: Only upload TXT, PDF, or DOCX files
2. **Verify file size**: Keep files under 10MB
3. **Monitor status messages**: Read upload feedback carefully
4. **Use retry buttons**: Try again if temporary errors occur
5. **Check network connection**: Ensure stable internet connectivity

## Error Monitoring

### Application Metrics
- Upload success/failure rates
- Classification error frequency
- Response time distributions
- Error type categorization

### Alerting
- High error rates
- Database connection failures
- Disk space issues
- Memory usage spikes

This comprehensive error handling ensures users have a smooth experience even when things go wrong, with clear feedback and recovery options at every step.
