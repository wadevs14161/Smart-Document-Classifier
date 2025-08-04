from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class DocumentBase(BaseModel):
    filename: str
    file_type: str

class DocumentCreate(DocumentBase):
    content_text: Optional[str] = None

class DocumentResponse(DocumentBase):
    id: int
    original_filename: str
    file_size: int
    content_text: Optional[str] = None
    predicted_category: Optional[str] = None
    confidence_score: Optional[float] = None
    is_classified: bool = False
    upload_timestamp: datetime
    
    class Config:
        from_attributes = True

class DocumentListResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_size: int
    predicted_category: Optional[str] = None
    confidence_score: Optional[float] = None
    is_classified: bool = False
    upload_timestamp: datetime
    file_type: str
    
    class Config:
        from_attributes = True

class UploadResponse(BaseModel):
    message: str
    document_id: int
    filename: str
    file_size: int
    content_preview: Optional[str] = None

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
