import React, { useState, useEffect } from 'react';
import { documentAPI } from '../services/api';
import type { Document } from '../services/api';
import './StatisticsDashboard.css';

interface ModelComparison {
  modelName: string;
  documentCount: number;
  averageConfidence: number;
  categoryDistribution: Record<string, number>;
  confidenceDistribution: {
    high: number;
    medium: number;
    low: number;
  };
  averageInferenceTime: number;
}

interface Statistics {
  totalDocuments: number;
  classifiedDocuments: number;
  documentsByType: Record<string, number>;
  documentsByCategory: Record<string, number>;
  modelUsage: Record<string, number>;
  averageConfidence: number;
  confidenceDistribution: {
    high: number; // >= 0.7
    medium: number; // 0.4-0.69
    low: number; // < 0.4
  };
  uploadTrends: {
    today: number;
    thisWeek: number;
    thisMonth: number;
  };
  recentActivity: Document[];
  modelComparison: ModelComparison[];
  sameDocumentComparisons: Array<{
    filename: string;
    bartResult: { category: string; confidence: number; time: number } | null;
    mdebertaResult: { category: string; confidence: number; time: number } | null;
    agreement: boolean;
  }>;
}

const StatisticsDashboard: React.FC = () => {
  const [statistics, setStatistics] = useState<Statistics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const calculateStatistics = (documents: Document[]): Statistics => {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const thisWeek = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
    const thisMonth = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000);

    const stats: Statistics = {
      totalDocuments: documents.length,
      classifiedDocuments: documents.filter(doc => doc.is_classified).length,
      documentsByType: {},
      documentsByCategory: {},
      modelUsage: {},
      averageConfidence: 0,
      confidenceDistribution: { high: 0, medium: 0, low: 0 },
      uploadTrends: { today: 0, thisWeek: 0, thisMonth: 0 },
      recentActivity: documents.slice(0, 5),
      modelComparison: [],
      sameDocumentComparisons: []
    };

    let totalConfidence = 0;
    let confidenceCount = 0;

    // Group documents by model for comparison
    const modelGroups: Record<string, Document[]> = {};
    const documentsByFilename: Record<string, Document[]> = {};

    documents.forEach(doc => {
      // Document type distribution
      const fileType = doc.file_type || 'unknown';
      stats.documentsByType[fileType] = (stats.documentsByType[fileType] || 0) + 1;

      // Category distribution
      if (doc.predicted_category) {
        stats.documentsByCategory[doc.predicted_category] = 
          (stats.documentsByCategory[doc.predicted_category] || 0) + 1;
      }

      // Model usage
      if (doc.model_used) {
        stats.modelUsage[doc.model_used] = (stats.modelUsage[doc.model_used] || 0) + 1;
        
        // Group by model
        if (!modelGroups[doc.model_used]) {
          modelGroups[doc.model_used] = [];
        }
        modelGroups[doc.model_used].push(doc);
      }

      // Group by filename for same-document comparisons
      if (doc.original_filename) {
        if (!documentsByFilename[doc.original_filename]) {
          documentsByFilename[doc.original_filename] = [];
        }
        documentsByFilename[doc.original_filename].push(doc);
      }

      // Confidence distribution
      if (doc.confidence_score !== null && doc.confidence_score !== undefined) {
        totalConfidence += doc.confidence_score;
        confidenceCount++;

        if (doc.confidence_score >= 0.7) {
          stats.confidenceDistribution.high++;
        } else if (doc.confidence_score >= 0.4) {
          stats.confidenceDistribution.medium++;
        } else {
          stats.confidenceDistribution.low++;
        }
      }

      // Upload trends
      const uploadDate = new Date(doc.uploaded_at);
      if (uploadDate >= today) {
        stats.uploadTrends.today++;
      }
      if (uploadDate >= thisWeek) {
        stats.uploadTrends.thisWeek++;
      }
      if (uploadDate >= thisMonth) {
        stats.uploadTrends.thisMonth++;
      }
    });

    stats.averageConfidence = confidenceCount > 0 ? totalConfidence / confidenceCount : 0;

    // Calculate model comparison statistics
    stats.modelComparison = Object.entries(modelGroups).map(([modelName, docs]) => {
      const categoryDist: Record<string, number> = {};
      const confDist = { high: 0, medium: 0, low: 0 };
      let totalConf = 0;
      let totalTime = 0;
      let confCount = 0;
      let timeCount = 0;

      docs.forEach(doc => {
        if (doc.predicted_category) {
          categoryDist[doc.predicted_category] = (categoryDist[doc.predicted_category] || 0) + 1;
        }

        if (doc.confidence_score !== null && doc.confidence_score !== undefined) {
          totalConf += doc.confidence_score;
          confCount++;
          
          if (doc.confidence_score >= 0.7) confDist.high++;
          else if (doc.confidence_score >= 0.4) confDist.medium++;
          else confDist.low++;
        }

        if (doc.inference_time !== null && doc.inference_time !== undefined) {
          totalTime += doc.inference_time;
          timeCount++;
        }
      });

      return {
        modelName,
        documentCount: docs.length,
        averageConfidence: confCount > 0 ? totalConf / confCount : 0,
        categoryDistribution: categoryDist,
        confidenceDistribution: confDist,
        averageInferenceTime: timeCount > 0 ? totalTime / timeCount : 0
      };
    });

    // Calculate same-document comparisons
    stats.sameDocumentComparisons = Object.entries(documentsByFilename)
      .filter(([_, docs]) => docs.length >= 2)
      .map(([filename, docs]) => {
        const bartDoc = docs.find(d => d.model_key === 'bart-large-mnli');
        const mdebertaDoc = docs.find(d => d.model_key === 'mdeberta-v3-base');

        const bartResult = bartDoc ? {
          category: bartDoc.predicted_category || 'Unknown',
          confidence: bartDoc.confidence_score || 0,
          time: bartDoc.inference_time || 0
        } : null;

        const mdebertaResult = mdebertaDoc ? {
          category: mdebertaDoc.predicted_category || 'Unknown',
          confidence: mdebertaDoc.confidence_score || 0,
          time: mdebertaDoc.inference_time || 0
        } : null;

        const agreement = bartResult && mdebertaResult ? 
          bartResult.category === mdebertaResult.category : false;

        return {
          filename,
          bartResult,
          mdebertaResult,
          agreement
        };
      });

    return stats;
  };

  const fetchStatistics = async () => {
    try {
      setLoading(true);
      const documents = await documentAPI.getDocuments();
      const stats = calculateStatistics(documents);
      setStatistics(stats);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch statistics:', err);
      setError('Failed to load statistics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatistics();
  }, []);

  const formatPercentage = (value: number, total: number): string => {
    return total > 0 ? ((value / total) * 100).toFixed(1) : '0.0';
  };

  const formatConfidence = (confidence: number): string => {
    return (confidence * 100).toFixed(1);
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  if (loading) {
    return (
      <div className="statistics-dashboard">
        <div className="dashboard-header">
          <h2>📊 Statistics Dashboard</h2>
        </div>
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading statistics...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="statistics-dashboard">
        <div className="dashboard-header">
          <h2>📊 Statistics Dashboard</h2>
        </div>
        <div className="error-state">
          <p>{error}</p>
          <button onClick={fetchStatistics} className="retry-btn">
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!statistics) {
    return null;
  }

  return (
    <div className="statistics-dashboard">
      <div className="dashboard-header">
        <h2>📊 Statistics Dashboard</h2>
        <button onClick={fetchStatistics} className="refresh-btn">
          🔄 Refresh
        </button>
      </div>

      {/* Overview Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">📄</div>
          <div className="stat-content">
            <h3>Total Documents</h3>
            <p className="stat-number">{statistics.totalDocuments}</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">🤖</div>
          <div className="stat-content">
            <h3>Classified</h3>
            <p className="stat-number">{statistics.classifiedDocuments}</p>
            <p className="stat-subtitle">
              {formatPercentage(statistics.classifiedDocuments, statistics.totalDocuments)}%
            </p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">🎯</div>
          <div className="stat-content">
            <h3>Avg Confidence</h3>
            <p className="stat-number">{formatConfidence(statistics.averageConfidence)}%</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">📈</div>
          <div className="stat-content">
            <h3>Today's Uploads</h3>
            <p className="stat-number">{statistics.uploadTrends.today}</p>
          </div>
        </div>
      </div>

      {/* Model Comparison Section */}
      <div className="model-comparison-section">
        <h2>🤖 AI Model Performance Comparison</h2>
        
        {/* Model Overview Cards */}
        <div className="model-overview-grid">
          {statistics.modelComparison.map((model, index) => (
            <div key={model.modelName} className={`model-card ${index === 0 ? 'primary-model' : 'secondary-model'}`}>
              <div className="model-header">
                <h3>{model.modelName}</h3>
                <div className="model-badge">
                  {model.modelName.includes('BART') ? '🅱️' : '🇲'}
                </div>
              </div>
              
              <div className="model-stats">
                <div className="model-stat">
                  <span className="stat-label">Documents Processed</span>
                  <span className="stat-value">{model.documentCount}</span>
                </div>
                
                <div className="model-stat">
                  <span className="stat-label">Average Confidence</span>
                  <span className="stat-value">{formatConfidence(model.averageConfidence)}%</span>
                </div>
                
                <div className="model-stat">
                  <span className="stat-label">Avg Inference Time</span>
                  <span className="stat-value">{model.averageInferenceTime.toFixed(2)}s</span>
                </div>
                
                <div className="model-stat">
                  <span className="stat-label">High Confidence Classifications</span>
                  <span className="stat-value">{model.confidenceDistribution.high}</span>
                </div>
              </div>

              {/* Model-specific confidence distribution */}
              <div className="model-confidence-viz">
                <div className="confidence-bar-container">
                  <div 
                    className="confidence-segment high-conf"
                    style={{ 
                      width: `${(model.confidenceDistribution.high / model.documentCount) * 100}%` 
                    }}
                    title={`High confidence: ${model.confidenceDistribution.high} documents`}
                  ></div>
                  <div 
                    className="confidence-segment medium-conf"
                    style={{ 
                      width: `${(model.confidenceDistribution.medium / model.documentCount) * 100}%` 
                    }}
                    title={`Medium confidence: ${model.confidenceDistribution.medium} documents`}
                  ></div>
                  <div 
                    className="confidence-segment low-conf"
                    style={{ 
                      width: `${(model.confidenceDistribution.low / model.documentCount) * 100}%` 
                    }}
                    title={`Low confidence: ${model.confidenceDistribution.low} documents`}
                  ></div>
                </div>
                <div className="confidence-legend">
                  <span className="legend-item high">High (≥70%)</span>
                  <span className="legend-item medium">Medium (40-69%)</span>
                  <span className="legend-item low">Low (&lt;40%)</span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Head-to-Head Comparison */}
        <div className="head-to-head-section">
          <h3>🔍 Head-to-Head Document Comparisons</h3>
          <div className="comparison-stats">
            <div className="agreement-summary">
              <div className="agreement-stat">
                <span className="agreement-label">Total Comparisons</span>
                <span className="agreement-value">{statistics.sameDocumentComparisons.length}</span>
              </div>
              <div className="agreement-stat">
                <span className="agreement-label">Model Agreement</span>
                <span className="agreement-value">
                  {statistics.sameDocumentComparisons.filter(comp => comp.agreement).length}/
                  {statistics.sameDocumentComparisons.length}
                  ({formatPercentage(
                    statistics.sameDocumentComparisons.filter(comp => comp.agreement).length,
                    statistics.sameDocumentComparisons.length
                  )}%)
                </span>
              </div>
            </div>
          </div>

          {/* Individual Comparisons */}
          <div className="comparison-list">
            {statistics.sameDocumentComparisons.map((comparison, index) => (
              <div key={index} className={`comparison-item ${comparison.agreement ? 'agreement' : 'disagreement'}`}>
                <div className="comparison-header">
                  <div className="filename-container">
                    <span className="comparison-filename">{comparison.filename}</span>
                    <div className={`agreement-indicator ${comparison.agreement ? 'agree' : 'disagree'}`}>
                      {comparison.agreement ? '✅ Agreement' : '❌ Disagreement'}
                    </div>
                  </div>
                </div>
                
                <div className="model-results">
                  <div className="model-result bart-result">
                    <div className="model-name">BART-Large-MNLI</div>
                    {comparison.bartResult ? (
                      <>
                        <div className="result-category">{comparison.bartResult.category}</div>
                        <div className="result-metrics">
                          <span className="confidence">{formatConfidence(comparison.bartResult.confidence)}%</span>
                          <span className="inference-time">{comparison.bartResult.time.toFixed(2)}s</span>
                        </div>
                      </>
                    ) : (
                      <div className="no-result">No classification</div>
                    )}
                  </div>
                  
                  <div className="vs-divider">VS</div>
                  
                  <div className="model-result mdeberta-result">
                    <div className="model-name">mDeBERTa-v3-Base</div>
                    {comparison.mdebertaResult ? (
                      <>
                        <div className="result-category">{comparison.mdebertaResult.category}</div>
                        <div className="result-metrics">
                          <span className="confidence">{formatConfidence(comparison.mdebertaResult.confidence)}%</span>
                          <span className="inference-time">{comparison.mdebertaResult.time.toFixed(2)}s</span>
                        </div>
                      </>
                    ) : (
                      <div className="no-result">No classification</div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="charts-grid">
        
        {/* Document Types */}
        <div className="chart-card">
          <h3>📁 Document Types</h3>
          <div className="chart-content">
            {Object.entries(statistics.documentsByType).map(([type, count]) => (
              <div key={type} className="bar-item">
                <div className="bar-label">
                  <span className="file-type">.{type.toUpperCase()}</span>
                  <span className="bar-count">{count}</span>
                </div>
                <div className="bar-container">
                  <div 
                    className="bar-fill"
                    style={{ width: `${(count / statistics.totalDocuments) * 100}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Categories */}
        <div className="chart-card">
          <h3>🏷️ Classification Categories</h3>
          <div className="chart-content">
            {Object.entries(statistics.documentsByCategory).map(([category, count]) => (
              <div key={category} className="bar-item">
                <div className="bar-label">
                  <span className="category-name">{category}</span>
                  <span className="bar-count">{count}</span>
                </div>
                <div className="bar-container">
                  <div 
                    className="bar-fill category-bar"
                    style={{ width: `${(count / statistics.classifiedDocuments) * 100}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Model Usage */}
        <div className="chart-card">
          <h3>🤖 Model Usage</h3>
          <div className="chart-content">
            {Object.entries(statistics.modelUsage).map(([model, count]) => (
              <div key={model} className="bar-item">
                <div className="bar-label">
                  <span className="model-name">{model}</span>
                  <span className="bar-count">{count}</span>
                </div>
                <div className="bar-container">
                  <div 
                    className="bar-fill model-bar"
                    style={{ width: `${(count / statistics.classifiedDocuments) * 100}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Confidence Distribution */}
        <div className="chart-card">
          <h3>🎯 Confidence Distribution</h3>
          <div className="chart-content">
            <div className="confidence-stats">
              <div className="confidence-item high">
                <span className="confidence-label">High (≥70%)</span>
                <span className="confidence-count">{statistics.confidenceDistribution.high}</span>
                <div className="confidence-bar">
                  <div 
                    className="confidence-fill high-confidence"
                    style={{ 
                      width: `${formatPercentage(statistics.confidenceDistribution.high, statistics.classifiedDocuments)}%` 
                    }}
                  ></div>
                </div>
              </div>
              
              <div className="confidence-item medium">
                <span className="confidence-label">Medium (40-69%)</span>
                <span className="confidence-count">{statistics.confidenceDistribution.medium}</span>
                <div className="confidence-bar">
                  <div 
                    className="confidence-fill medium-confidence"
                    style={{ 
                      width: `${formatPercentage(statistics.confidenceDistribution.medium, statistics.classifiedDocuments)}%` 
                    }}
                  ></div>
                </div>
              </div>
              
              <div className="confidence-item low">
                <span className="confidence-label">Low (&lt;40%)</span>
                <span className="confidence-count">{statistics.confidenceDistribution.low}</span>
                <div className="confidence-bar">
                  <div 
                    className="confidence-fill low-confidence"
                    style={{ 
                      width: `${formatPercentage(statistics.confidenceDistribution.low, statistics.classifiedDocuments)}%` 
                    }}
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>

      {/* Upload Trends */}
      <div className="trends-section">
        <h3>📈 Upload Trends</h3>
        <div className="trends-grid">
          <div className="trend-item">
            <span className="trend-period">Today</span>
            <span className="trend-count">{statistics.uploadTrends.today}</span>
          </div>
          <div className="trend-item">
            <span className="trend-period">This Week</span>
            <span className="trend-count">{statistics.uploadTrends.thisWeek}</span>
          </div>
          <div className="trend-item">
            <span className="trend-period">This Month</span>
            <span className="trend-count">{statistics.uploadTrends.thisMonth}</span>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="recent-activity">
        <h3>🕒 Recent Activity</h3>
        <div className="activity-list">
          {statistics.recentActivity.map(doc => (
            <div key={doc.id} className="activity-item">
              <div className="activity-info">
                <span className="activity-filename">{doc.original_filename}</span>
                <span className="activity-details">
                  {doc.is_classified ? doc.predicted_category : 'Not classified'} • 
                  {formatFileSize(doc.file_size)} • 
                  {new Date(doc.uploaded_at).toLocaleDateString()}
                </span>
              </div>
              {doc.confidence_score !== null && (
                <div className="activity-confidence">
                  {formatConfidence(doc.confidence_score)}%
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default StatisticsDashboard;
