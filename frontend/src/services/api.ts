import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types for API responses
export interface Document {
  id: number;
  filename: string;
  original_filename: string;
  file_path: string;
  file_size: number;
  file_type: string;
  content_text: string | null;
  predicted_category: string | null;
  confidence_score: number | null;
  all_scores: Record<string, number> | null;
  is_classified: boolean;
  classification_time: string | null;
  inference_time: number | null;
  uploaded_at: string;
  updated_at: string | null;
}

export interface UploadResponse {
  message: string;
  document_id: number;
  filename: string;
  file_size: number;
  content_preview?: string;
  classification?: {
    predicted_category: string;
    confidence_score: number;
    auto_classified: boolean;
  };
}

export interface ClassificationResult {
  message: string;
  document_id: number;
  classification_result: {
    predicted_category: string;
    confidence_score: number;
    all_scores: Record<string, number>;
    inference_time: number;
    model_used: string;
    text_length_chars: number;
    text_length_tokens: number;
    was_truncated: boolean;
    original_token_count: number;
    chunks_used?: number;
  };
}

export interface DocumentListResponse {
  documents: Document[];
}

// API Functions
export const documentAPI = {
  // Get all documents
  getDocuments: async (): Promise<Document[]> => {
    const response = await api.get('/documents');
    return response.data;
  },

  // Upload document
  uploadDocument: async (file: File): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Classify document
  classifyDocument: async (documentId: number): Promise<ClassificationResult> => {
    const response = await api.post(`/documents/${documentId}/classify`);
    return response.data;
  },

  // Delete document
  deleteDocument: async (documentId: number): Promise<{ message: string }> => {
    const response = await api.delete(`/documents/${documentId}`);
    return response.data;
  },

  // Get single document
  getDocument: async (documentId: number): Promise<Document> => {
    const response = await api.get(`/documents/${documentId}`);
    return response.data;
  },

  // Health check
  healthCheck: async (): Promise<{ status: string; message: string }> => {
    const response = await api.get('/health');
    return response.data;
  },
};

export default api;
