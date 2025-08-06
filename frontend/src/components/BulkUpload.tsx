import React, { useState, useEffect } from 'react';
import { documentAPI } from '../services/api';
import type { BulkUploadResponse, BulkUploadFileResult, ModelInfo } from '../services/api';
import './BulkUpload.css';

interface BulkUploadProps {
  onUploadSuccess: (results: BulkUploadFileResult[]) => void;
}

interface FileWithStatus {
  file: File;
  status: 'pending' | 'uploading' | 'success' | 'error' | 'warning';
  result?: BulkUploadFileResult;
  id: string;
}

const BulkUpload: React.FC<BulkUploadProps> = ({ onUploadSuccess }) => {
  const [selectedFiles, setSelectedFiles] = useState<FileWithStatus[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [availableModels, setAvailableModels] = useState<Record<string, ModelInfo>>({});
  const [selectedModel, setSelectedModel] = useState<string>('bart-large-mnli');
  const [autoClassify, setAutoClassify] = useState<boolean>(true);
  const [uploadResults, setUploadResults] = useState<BulkUploadResponse | null>(null);

  // Load available models on component mount
  useEffect(() => {
    documentAPI.getModels()
      .then(response => {
        setAvailableModels(response.models);
      })
      .catch(error => {
        console.error('Failed to load models:', error);
      });
  }, []);

  // Supported file types
  const supportedTypes = ['text/plain', 'application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword'];
  const supportedExtensions = ['.txt', '.pdf', '.docx', '.doc'];

  const validateFile = (file: File): boolean => {
    const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
    return supportedTypes.includes(file.type) || supportedExtensions.includes(fileExtension);
  };

  const generateFileId = (): string => {
    return Date.now().toString() + Math.random().toString(36).substr(2, 9);
  };

  const handleFilesSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);
    addFiles(files);
    // Reset input
    event.target.value = '';
  };

  const addFiles = (files: File[]) => {
    const validFiles = files.filter(validateFile);
    const invalidFiles = files.filter(f => !validateFile(f));
    
    if (invalidFiles.length > 0) {
      alert(`${invalidFiles.length} file(s) were skipped due to unsupported file types. Only TXT, PDF, and DOCX files are supported.`);
    }

    const newFiles: FileWithStatus[] = validFiles.map(file => ({
      file,
      status: 'pending',
      id: generateFileId()
    }));

    setSelectedFiles(prev => {
      const combined = [...prev, ...newFiles];
      // Limit to 10 files max
      if (combined.length > 10) {
        alert('Maximum 10 files allowed. Excess files will be removed.');
        return combined.slice(0, 10);
      }
      return combined;
    });
  };

  const removeFile = (fileId: string) => {
    setSelectedFiles(prev => prev.filter(f => f.id !== fileId));
  };

  const clearAllFiles = () => {
    setSelectedFiles([]);
    setUploadResults(null);
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
    
    if (e.dataTransfer.files) {
      const files = Array.from(e.dataTransfer.files);
      addFiles(files);
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending': return '⏳';
      case 'uploading': return '🔄';
      case 'success': return '✅';
      case 'error': return '❌';
      case 'warning': return '⚠️';
      default: return '📄';
    }
  };

  const handleBulkUpload = async () => {
    if (selectedFiles.length === 0) {
      alert('Please select files to upload');
      return;
    }

    setIsUploading(true);
    setUploadResults(null);
    
    // Set all files to uploading status
    setSelectedFiles(prev => prev.map(f => ({ ...f, status: 'uploading' })));

    try {
      const files = selectedFiles.map(f => f.file);
      const response = await documentAPI.bulkUploadDocuments(files, selectedModel, autoClassify);
      
      // Update file statuses based on results
      setSelectedFiles(prev => prev.map(fileWithStatus => {
        const result = response.results.find(r => r.filename === fileWithStatus.file.name);
        if (result) {
          return {
            ...fileWithStatus,
            status: result.status as any,
            result: result
          };
        }
        return { ...fileWithStatus, status: 'error' };
      }));

      setUploadResults(response);
      onUploadSuccess(response.results);
      
    } catch (error: any) {
      console.error('Bulk upload failed:', error);
      
      // Set all files to error status
      setSelectedFiles(prev => prev.map(f => ({ 
        ...f, 
        status: 'error',
        result: {
          filename: f.file.name,
          status: 'error',
          error: error.response?.data?.detail || error.message || 'Upload failed'
        }
      })));
      
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="bulk-upload">
      <div className="bulk-upload-header">
        <h3>📦 Bulk Upload Documents</h3>
        <p>Upload multiple documents at once (max 10 files)</p>
      </div>

      {/* Model Selection */}
      <div className="model-selection">
        <label htmlFor="model-select">Classification Model:</label>
        <select
          id="model-select"
          value={selectedModel}
          onChange={(e) => setSelectedModel(e.target.value)}
          disabled={isUploading}
        >
          {Object.entries(availableModels).map(([key, model]) => (
            <option key={key} value={key}>
              {model.name}
            </option>
          ))}
        </select>
      </div>

      {/* Auto-classify Option */}
      <div className="auto-classify-option">
        <label>
          <input
            type="checkbox"
            checked={autoClassify}
            onChange={(e) => setAutoClassify(e.target.checked)}
            disabled={isUploading}
          />
          Automatically classify documents after upload
        </label>
      </div>

      {/* File Selection Area */}
      <div 
        className={`file-drop-area ${dragActive ? 'drag-active' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <div className="drop-area-content">
          <div className="upload-icon">📁</div>
          <p>Drag and drop files here</p>
          <p className="or-text">or</p>
          <label className="file-input-label">
            <input
              type="file"
              multiple
              accept=".txt,.pdf,.docx,.doc"
              onChange={handleFilesSelect}
              disabled={isUploading}
              style={{ display: 'none' }}
            />
            Choose Files
          </label>
          <p className="supported-formats">
            Supported: TXT, PDF, DOCX files (max 25MB each)
          </p>
        </div>
      </div>

      {/* Selected Files List */}
      {selectedFiles.length > 0 && (
        <div className="selected-files">
          <div className="files-header">
            <h4>Selected Files ({selectedFiles.length}/10)</h4>
            <div className="files-actions">
              <button 
                onClick={clearAllFiles}
                disabled={isUploading}
                className="clear-all-btn"
              >
                Clear All
              </button>
              <button 
                onClick={handleBulkUpload}
                disabled={isUploading || selectedFiles.length === 0}
                className="upload-btn"
              >
                {isUploading ? 'Uploading...' : `Upload ${selectedFiles.length} Files`}
              </button>
            </div>
          </div>

          <div className="files-list">
            {selectedFiles.map((fileWithStatus) => (
              <div key={fileWithStatus.id} className={`file-item ${fileWithStatus.status}`}>
                <div className="file-info">
                  <div className="file-details">
                    <span className="status-icon">{getStatusIcon(fileWithStatus.status)}</span>
                    <span className="file-name">{fileWithStatus.file.name}</span>
                    <span className="file-size">{formatFileSize(fileWithStatus.file.size)}</span>
                  </div>
                  
                  {fileWithStatus.result?.error && (
                    <div className="file-error">
                      Error: {fileWithStatus.result.error}
                    </div>
                  )}
                  
                  {fileWithStatus.result?.warnings && (
                    <div className="file-warnings">
                      {fileWithStatus.result.warnings.map((warning, idx) => (
                        <div key={idx} className="warning">⚠️ {warning}</div>
                      ))}
                    </div>
                  )}
                  
                  {fileWithStatus.result?.classification && (
                    <div className="classification-preview">
                      <strong>Category:</strong> {fileWithStatus.result.classification.predicted_category} 
                      <span className="confidence">
                        ({(fileWithStatus.result.classification.confidence_score * 100).toFixed(1)}% confidence)
                      </span>
                    </div>
                  )}
                </div>

                {!isUploading && fileWithStatus.status === 'pending' && (
                  <button 
                    onClick={() => removeFile(fileWithStatus.id)}
                    className="remove-file-btn"
                    title="Remove file"
                  >
                    ✕
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Upload Results Summary */}
      {uploadResults && (
        <div className="upload-results">
          <h4>Upload Results</h4>
          <div className="results-summary">
            <div className="result-stat">
              <span className="stat-label">Total Files:</span>
              <span className="stat-value">{uploadResults.total_files}</span>
            </div>
            <div className="result-stat success">
              <span className="stat-label">Successful:</span>
              <span className="stat-value">{uploadResults.successful_uploads}</span>
            </div>
            <div className="result-stat error">
              <span className="stat-label">Failed:</span>
              <span className="stat-value">{uploadResults.failed_uploads}</span>
            </div>
            <div className="result-stat">
              <span className="stat-label">Processing Time:</span>
              <span className="stat-value">{uploadResults.processing_time.toFixed(2)}s</span>
            </div>
          </div>
          <p className="results-message">{uploadResults.message}</p>
        </div>
      )}
    </div>
  );
};

export default BulkUpload;
