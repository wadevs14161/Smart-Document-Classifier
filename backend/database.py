from sqlalchemy import create_engine, Column, Integer, String, Text, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./documents.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Document model
class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    content_text = Column(Text, nullable=True)  # Extracted text content
    
    # Classification results (will be implemented later)
    predicted_category = Column(String, nullable=True)
    confidence_score = Column(Float, nullable=True)
    is_classified = Column(Boolean, default=False)
    
    # Metadata
    upload_timestamp = Column(DateTime, default=datetime.utcnow)
    file_type = Column(String, nullable=False)  # pdf, txt, docx, etc.
    
    def __repr__(self):
        return f"<Document(id={self.id}, filename={self.filename}, category={self.predicted_category})>"

# Create tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
