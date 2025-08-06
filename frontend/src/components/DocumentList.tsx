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
      setLoading(true);
      const docs = await documentAPI.getDocuments();
      setDocuments(docs);
      console.log(`Successfully loaded ${docs.length} documents`);
    } catch (error: any) {
      console.error('Failed to fetch documents:', error);
      
      let errorMessage = 'Failed to load documents';
      if (error.response?.status === 500) {
        errorMessage = 'Server error while loading documents. Please try again later.';
      } else if (error.response?.status === 404) {
        errorMessage = 'Document service not found. Please check server status.';
      } else if (error.code === 'NETWORK_ERROR' || !error.response) {
        errorMessage = 'Network error. Please check your connection and try again.';
      } else if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      }
      
      setError(errorMessage);
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
              all_scores: result.classification_result.all_scores,
              inference_time: result.classification_result.inference_time,
              is_classified: true,
              classification_time: new Date().toISOString(),
              updated_at: new Date().toISOString(),
            }
          : doc
      ));
      console.log(`Successfully classified document ${documentId}`);
    } catch (error: any) {
      console.error('Classification failed:', error);
      
      let errorMessage = 'Classification failed';
      if (error.response?.status === 404) {
        errorMessage = 'Document not found. It may have been deleted.';
      } else if (error.response?.status === 400) {
        errorMessage = 'Document cannot be classified (no readable text content).';
      } else if (error.response?.status === 500) {
        errorMessage = 'Server error during classification. Please try again.';
      } else if (error.code === 'NETWORK_ERROR' || !error.response) {
        errorMessage = 'Network error. Please check your connection.';
      } else if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      }
      
      alert(`❌ ${errorMessage}`);
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
      console.log(`Successfully deleted document ${documentId}: ${filename}`);
    } catch (error: any) {
      console.error('Delete failed:', error);
      
      let errorMessage = 'Delete failed';
      if (error.response?.status === 404) {
        errorMessage = 'Document not found. It may have already been deleted.';
        // Remove from UI anyway since it doesn't exist
        setDocuments(prev => prev.filter(doc => doc.id !== documentId));
      } else if (error.response?.status === 500) {
        errorMessage = 'Server error during deletion. Please try again.';
      } else if (error.code === 'NETWORK_ERROR' || !error.response) {
        errorMessage = 'Network error. Please check your connection.';
      } else if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      }
      
      alert(`❌ ${errorMessage}`);
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

  const getSortedClassificationScores = (allScores: Record<string, number> | null) => {
    if (!allScores) return [];
    
    return Object.entries(allScores)
      .map(([category, score]) => ({ category, score }))
      .sort((a, b) => b.score - a.score);
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

  if (error) {
    return (
      <div className="documents-section">
        <div className="error-state">
          <div className="error-icon">⚠️</div>
          <h3>Unable to load documents</h3>
          <p className="error-message">{error}</p>
          <button 
            onClick={fetchDocuments} 
            className="retry-btn"
          >
            🔄 Try Again
          </button>
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
        <div className="documents-table-wrapper">
          <table className="documents-table">
            <thead>
              <tr>
                <th>Document</th>
                <th>Type</th>
                <th>Size</th>
                <th>Upload Date</th>
                <th>Classification</th>
                <th>Confidence</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {documents.map((doc) => (
                <React.Fragment key={doc.id}>
                  <tr className="document-row">
                    <td className="document-title-cell">
                      <div className="document-title">
                        <span className="file-emoji">{getFileTypeEmoji(doc.file_type)}</span>
                        <div className="title-info">
                          <h3>{doc.original_filename}</h3>
                          {doc.inference_time && (
                            <div className="processing-time">
                              Processing: {doc.inference_time.toFixed(3)}s
                            </div>
                          )}
                        </div>
                      </div>
                    </td>
                    
                    <td className="file-type-cell">
                      <span className={`file-type-badge ${doc.file_type.toLowerCase()}`}>
                        {doc.file_type.toUpperCase()}
                      </span>
                    </td>
                    
                    <td className="size-cell">
                      {formatFileSize(doc.file_size)}
                    </td>
                    
                    <td className="date-cell">
                      {formatDate(doc.uploaded_at)}
                    </td>
                    
                    <td className="classification-cell">
                      {doc.is_classified && doc.predicted_category ? (
                        <span className="category-tag">{doc.predicted_category}</span>
                      ) : (
                        <span className="not-classified">Not classified</span>
                      )}
                    </td>
                    
                    <td className="confidence-cell">
                      {doc.confidence_score ? (
                        <div className="confidence-display">
                          <span 
                            className="confidence-value"
                            style={{ color: getConfidenceColor(doc.confidence_score) }}
                          >
                            {(doc.confidence_score * 100).toFixed(1)}%
                          </span>
                          <div className="confidence-bar-mini">
                            <div 
                              className="confidence-fill-mini"
                              style={{ 
                                width: `${doc.confidence_score * 100}%`,
                                backgroundColor: getConfidenceColor(doc.confidence_score)
                              }}
                            />
                          </div>
                        </div>
                      ) : (
                        <span className="no-confidence">-</span>
                      )}
                    </td>
                    
                    <td className="actions-cell">
                      <div className="action-buttons">
                        {!doc.is_classified ? (
                          <button
                            onClick={() => handleClassify(doc.id)}
                            disabled={classifyingIds.has(doc.id)}
                            className="classify-btn primary"
                            title="Classify document"
                          >
                            {classifyingIds.has(doc.id) ? (
                              <span className="spinner-small"></span>
                            ) : (
                              <span>🔍</span>
                            )}
                          </button>
                        ) : (
                          <button
                            onClick={() => handleClassify(doc.id)}
                            disabled={classifyingIds.has(doc.id)}
                            className="classify-btn secondary"
                            title="Re-classify document"
                          >
                            {classifyingIds.has(doc.id) ? (
                              <span className="spinner-small"></span>
                            ) : (
                              <span>🔄</span>
                            )}
                          </button>
                        )}

                        {doc.content_text && (
                          <button
                            onClick={() => toggleContent(doc.id)}
                            className="toggle-content-btn"
                            title={expandedContent.has(doc.id) ? 'Hide content' : 'Show content'}
                          >
                            <span>{expandedContent.has(doc.id) ? '📖' : '👁️'}</span>
                          </button>
                        )}

                        <button
                          onClick={() => handleDelete(doc.id, doc.original_filename)}
                          className="delete-btn"
                          title="Delete document"
                        >
                          <span>🗑️</span>
                        </button>
                      </div>
                    </td>
                  </tr>
                  
                  {/* Expandable row for detailed scores */}
                  {doc.all_scores && expandedContent.has(doc.id) && (
                    <tr className="details-row">
                      <td colSpan={7}>
                        <div className="detailed-info">
                          <div className="scores-section">
                            <h4>Classification Scores:</h4>
                            <div className="scores-grid">
                              {getSortedClassificationScores(doc.all_scores).map(({ category, score }, index) => (
                                <div key={category} className={`score-item ${index === 0 ? 'top-score' : ''}`}>
                                  <div className="score-header">
                                    <span className="score-category">{category}</span>
                                    <span className="score-percentage">{(score * 100).toFixed(1)}%</span>
                                  </div>
                                  <div className="score-bar">
                                    <div 
                                      className="score-fill"
                                      style={{ 
                                        width: `${score * 100}%`,
                                        backgroundColor: index === 0 ? getConfidenceColor(score) : '#e9ecef'
                                      }}
                                    />
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                          
                          {doc.content_text && (
                            <div className="content-section">
                              <h4>Document Content:</h4>
                              <div className="content-text">
                                {doc.content_text}
                              </div>
                            </div>
                          )}
                        </div>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default DocumentList;
