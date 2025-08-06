import { useState } from 'react';
import DocumentUpload from './components/DocumentUpload';
import DocumentList from './components/DocumentList';
import StatisticsDashboard from './components/StatisticsDashboard';
import type { UploadResponse } from './services/api';
import './App.css';

function App() {
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [activeTab, setActiveTab] = useState<'upload' | 'statistics'>('upload');

  const handleUploadSuccess = (result: UploadResponse) => {
    console.log('Upload successful:', result);
    // Trigger document list refresh
    setRefreshTrigger(prev => prev + 1);
  };

  return (
    <div className="App">
      <header className="app-header">
        <div className="header-content">
          <h1>🤖 Smart Document Classifier</h1>
          <p>Upload documents and classify them using AI-powered models</p>
          
          {/* Navigation Tabs */}
          <nav className="app-nav">
            <button 
              className={`nav-tab ${activeTab === 'upload' ? 'active' : ''}`}
              onClick={() => setActiveTab('upload')}
            >
              📄 Documents
            </button>
            <button 
              className={`nav-tab ${activeTab === 'statistics' ? 'active' : ''}`}
              onClick={() => setActiveTab('statistics')}
            >
              📊 Statistics
            </button>
          </nav>
        </div>
      </header>

      <main className="app-main">
        <div className="main-content">
          {activeTab === 'upload' ? (
            <>
              <DocumentUpload onUploadSuccess={handleUploadSuccess} />
              <DocumentList refreshTrigger={refreshTrigger} />
            </>
          ) : (
            <StatisticsDashboard />
          )}
        </div>
      </main>

      <footer className="app-footer">
        <p>Powered by FastAPI + React + Multi-Model AI</p>
      </footer>
    </div>
  );
}

export default App;
