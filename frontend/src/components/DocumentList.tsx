import React, { useState, useEffect } from 'react';
import { documentAPI } from '../services/api';
import type { Document, ClassificationResult } from '../services/api';
import './DocumentList.css';

interface DocumentListProps {
  refreshTrigger: number;
}

const DocumentList: React.FC<DocumentListProps> = ({ refreshTrigger }) => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [classifyingIds, setClassifyingIds] = useState<Set<number>>(new Set());
  const [expandedContent, setExpandedContent] = useState<Set<number>>(new Set());
  const [error, setError] = useState<string>('');

  const fetchDocuments = async () => {
    try {
      setError('');
      const docs = await documentAPI.getDocuments();
      setDocuments(docs);
    } catch (error: any) {
      console.error('Failed to fetch documents:', error);
      setError(error.response?.data?.detail || 'Failed to load documents');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, [refreshTrigger]);

  const handleClassify = async (documentId: number) => {
    setClassifyingIds(prev => new Set(prev).add(documentId));
    
    try {
      const result: ClassificationResult = await documentAPI.classifyDocument(documentId);
      
      // Update the document in the list
      setDocuments(prev => prev.map(doc => 
        doc.id === documentId 
          ? { 
              ...doc, 
              predicted_category: result.classification_result.predicted_category,
              confidence_score: result.classification_result.confidence_score,
              inference_time: result.classification_result.inference_time,
              is_classified: true,
              classification_time: new Date().toISOString(),
              updated_at: new Date().toISOString(),
            }
          : doc
      ));
    } catch (error: any) {
      console.error('Classification failed:', error);
      const errorMessage = error.response?.data?.detail || 'Classification failed';
      alert(`Classification failed: ${errorMessage}`);
    } finally {
      setClassifyingIds(prev => {
        const newSet = new Set(prev);
        newSet.delete(documentId);
        return newSet;
      });
    }
  };

  const handleDelete = async (documentId: number, filename: string) => {
    if (!window.confirm(`Are you sure you want to delete "${filename}"?`)) {
      return;
    }

    try {
      await documentAPI.deleteDocument(documentId);
      setDocuments(prev => prev.filter(doc => doc.id !== documentId));
    } catch (error: any) {
      console.error('Delete failed:', error);
      const errorMessage = error.response?.data?.detail || 'Delete failed';
      alert(`Delete failed: ${errorMessage}`);
    }
  };

  const toggleContent = (documentId: number) => {
    setExpandedContent(prev => {
      const newSet = new Set(prev);
      if (newSet.has(documentId)) {
        newSet.delete(documentId);
      } else {
        newSet.add(documentId);
      }
      return newSet;
    });
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const getFileTypeEmoji = (fileType: string) => {
    switch (fileType.toLowerCase()) {
      case 'pdf': return '📕';
      case 'docx': case 'doc': return '📄';
      case 'txt': return '📝';
      default: return '📄';
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return '#28a745'; // Green
    if (confidence >= 0.6) return '#ffc107'; // Yellow
    return '#dc3545'; // Red
  };

  if (loading) {
    return (
      <div className="documents-section">
        <div className="loading">
          <span className="spinner-large"></span>
          Loading documents...
        </div>
      </div>
    );
  }

  return (
    <div className="documents-section">
      <div className="documents-header">
        <h2>📚 Document Library</h2>
        <div className="documents-stats">
          <span className="stat">
            <strong>{documents.length}</strong> documents
          </span>
          <span className="stat">
            <strong>{documents.filter(d => d.is_classified).length}</strong> classified
          </span>
          <button 
            onClick={fetchDocuments} 
            className="refresh-btn"
            disabled={loading}
          >
            🔄 Refresh
          </button>
        </div>
      </div>
      
      {error && (
        <div className="error-message">
          ❌ {error}
        </div>
      )}
      
      {documents.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📂</div>
          <h3>No documents uploaded yet</h3>
          <p>Upload your first document above to get started with AI classification!</p>
        </div>
      ) : (
        <div className="documents-grid">
          {documents.map((doc) => (
            <div key={doc.id} className="document-card">
              <div className="document-header">
                <div className="document-title">
                  <span className="file-emoji">{getFileTypeEmoji(doc.file_type)}</span>
                  <h3>{doc.original_filename}</h3>
                </div>
                <span className={`file-type-badge ${doc.file_type.toLowerCase()}`}>
                  {doc.file_type.toUpperCase()}
                </span>
              </div>

              <div className="document-info">
                <div className="info-row">
                  <span className="info-label">Size:</span>
                  <span>{formatFileSize(doc.file_size)}</span>
                </div>
                <div className="info-row">
                  <span className="info-label">Uploaded:</span>
                  <span>{formatDate(doc.uploaded_at)}</span>
                </div>
                
                {doc.is_classified && doc.predicted_category && (
                  <div className="classification-info">
                    <div className="info-row">
                      <span className="info-label">Category:</span>
                      <span className="category-tag">{doc.predicted_category}</span>
                    </div>
                    
                    {doc.confidence_score && (
                      <div className="confidence-section">
                        <div className="confidence-header">
                          <span className="info-label">Confidence:</span>
                          <span className="confidence-value">
                            {(doc.confidence_score * 100).toFixed(1)}%
                          </span>
                        </div>
                        <div className="confidence-bar">
                          <div 
                            className="confidence-fill"
                            style={{ 
                              width: `${doc.confidence_score * 100}%`,
                              backgroundColor: getConfidenceColor(doc.confidence_score)
                            }}
                          />
                        </div>
                      </div>
                    )}
                    
                    {doc.inference_time && (
                      <div className="info-row">
                        <span className="info-label">Processing Time:</span>
                        <span>{doc.inference_time.toFixed(3)}s</span>
                      </div>
                    )}
                  </div>
                )}
              </div>

              <div className="document-actions">
                {!doc.is_classified ? (
                  <button
                    onClick={() => handleClassify(doc.id)}
                    disabled={classifyingIds.has(doc.id)}
                    className="classify-btn primary"
                  >
                    {classifyingIds.has(doc.id) ? (
                      <>
                        <span className="spinner-small"></span>
                        Classifying...
                      </>
                    ) : (
                      <>
                        <span>🔍</span>
                        Classify
                      </>
                    )}
                  </button>
                ) : (
                  <button
                    onClick={() => handleClassify(doc.id)}
                    disabled={classifyingIds.has(doc.id)}
                    className="classify-btn secondary"
                  >
                    {classifyingIds.has(doc.id) ? (
                      <>
                        <span className="spinner-small"></span>
                        Re-classifying...
                      </>
                    ) : (
                      <>
                        <span>🔄</span>
                        Re-classify
                      </>
                    )}
                  </button>
                )}

                {doc.content_text && (
                  <button
                    onClick={() => toggleContent(doc.id)}
                    className="toggle-content-btn"
                  >
                    <span>{expandedContent.has(doc.id) ? '📖' : '👁️'}</span>
                    {expandedContent.has(doc.id) ? 'Hide Content' : 'Show Content'}
                  </button>
                )}

                <button
                  onClick={() => handleDelete(doc.id, doc.original_filename)}
                  className="delete-btn"
                >
                  <span>🗑️</span>
                  Delete
                </button>
              </div>

              {doc.content_text && expandedContent.has(doc.id) && (
                <div className="document-content">
                  <h4>Document Content:</h4>
                  <div className="content-text">
                    {doc.content_text}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default DocumentList;
