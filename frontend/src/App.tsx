import { useState } from 'react';
import DocumentUpload from './components/DocumentUpload';
import DocumentList from './components/DocumentList';
import type { UploadResponse } from './services/api';
import './App.css';

function App() {
  const [refreshTrigger, setRefreshTrigger] = useState(0);

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
          <p>Upload documents and classify them using AI-powered BART-Large-MNLI model</p>
        </div>
      </header>

      <main className="app-main">
        <div className="main-content">
          <DocumentUpload onUploadSuccess={handleUploadSuccess} />
          <DocumentList refreshTrigger={refreshTrigger} />
        </div>
      </main>

      <footer className="app-footer">
        <p>Powered by FastAPI + React + BART-Large-MNLI</p>
      </footer>
    </div>
  );
}

export default App;
