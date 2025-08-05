import React, { useState } from 'react';
import { documentAPI } from '../services/api';
import type { UploadResponse } from '../services/api';
import './DocumentUpload.css';

interface DocumentUploadProps {
  onUploadSuccess: (result: UploadResponse) => void;
}

const DocumentUpload: React.FC<DocumentUploadProps> = ({ onUploadSuccess }) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<string>('');
  const [dragActive, setDragActive] = useState(false);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setUploadStatus('');
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setSelectedFile(e.dataTransfer.files[0]);
      setUploadStatus('');
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadStatus('Please select a file first');
      return;
    }

    setIsUploading(true);
    setUploadStatus('Uploading and classifying...');

    try {
      const result = await documentAPI.uploadDocument(selectedFile);
      const category = result.classification?.predicted_category || 'Pending classification';
      const topConfidence = result.classification?.confidence_score 
        ? (result.classification.confidence_score * 100).toFixed(1) + '%'
        : 'N/A';
      
      setUploadStatus(`✅ Upload successfully! Classified as: ${category} ${topConfidence}`);
      onUploadSuccess(result);
      setSelectedFile(null);
      
      // Reset file input
      const fileInput = document.getElementById('file-input') as HTMLInputElement;
      if (fileInput) fileInput.value = '';
      
    } catch (error: any) {
      console.error('Upload failed:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Unknown error';
      setUploadStatus(`❌ Upload failed: ${errorMessage}`);
    } finally {
      setIsUploading(false);
    }
  };

  const formatFileSize = (bytes: number) => {
    return (bytes / 1024).toFixed(2) + ' KB';
  };

  return (
    <div className="upload-section">
      <div className="upload-card">
        <h2>📄 Upload Document</h2>
        <p className="upload-description">
          Upload documents for AI-powered classification using BART-Large-MNLI
        </p>
        
        <div 
          className={`upload-area ${dragActive ? 'drag-active' : ''}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <input
            id="file-input"
            type="file"
            accept=".txt,.pdf,.docx,.doc"
            onChange={handleFileSelect}
            disabled={isUploading}
            className="file-input"
          />
          <label htmlFor="file-input" className="file-input-label">
            {selectedFile ? (
              <div className="file-selected">
                <span className="file-icon">📄</span>
                <span className="file-name">{selectedFile.name}</span>
              </div>
            ) : (
              <div className="file-placeholder">
                <span className="upload-icon">📁</span>
                <span className="upload-text">Choose file or drag & drop</span>
                <span className="upload-subtext">Supports: TXT, PDF, DOCX</span>
              </div>
            )}
          </label>
        </div>
        
        {selectedFile && (
          <div className="file-info">
            <div className="file-details">
              <p><strong>File:</strong> {selectedFile.name}</p>
              <p><strong>Size:</strong> {formatFileSize(selectedFile.size)}</p>
              <p><strong>Type:</strong> {selectedFile.type || 'Unknown'}</p>
            </div>
          </div>
        )}

        <button
          onClick={handleUpload}
          disabled={!selectedFile || isUploading}
          className={`upload-btn ${isUploading ? 'loading' : ''}`}
        >
          {isUploading ? (
            <>
              <span className="spinner"></span>
              Processing...
            </>
          ) : (
            <>
              <span className="upload-btn-icon">🚀</span>
              Upload & Classify
            </>
          )}
        </button>

        {uploadStatus && (
          <div className={`status-message ${
            uploadStatus.includes('✅') ? 'success' : 
            uploadStatus.includes('❌') ? 'error' : 'info'
          }`}>
            {uploadStatus}
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentUpload;
