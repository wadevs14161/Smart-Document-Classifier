import React, { useState, useEffect } from 'react';
import { documentAPI } from '../services/api';
import type { Document } from '../services/api';
import './StatisticsDashboard.css';

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
      recentActivity: documents.slice(0, 5)
    };

    let totalConfidence = 0;
    let confidenceCount = 0;

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
