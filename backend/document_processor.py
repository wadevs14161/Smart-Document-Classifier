import aiofiles
from typing import Optional
import PyPDF2
from docx import Document as DocxDocument
from io import BytesIO

class DocumentProcessor:
    """Handles document text extraction from various file formats"""
    
    @staticmethod
    async def extract_text_from_file(file_path: str, file_type: str) -> Optional[str]:
        """Extract text content from uploaded files"""
        try:
            if file_type.lower() == 'txt':
                return await DocumentProcessor._extract_from_txt(file_path)
            elif file_type.lower() == 'pdf':
                return await DocumentProcessor._extract_from_pdf(file_path)
            elif file_type.lower() in ['docx', 'doc']:
                return await DocumentProcessor._extract_from_docx(file_path)
            else:
                return None
        except Exception as e:
            print(f"Error extracting text from {file_path}: {str(e)}")
            return None
    
    @staticmethod
    async def _extract_from_txt(file_path: str) -> str:
        """Extract text from plain text files"""
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
            content = await file.read()
            return content
    
    @staticmethod
    async def _extract_from_pdf(file_path: str) -> str:
        """Extract text from PDF files"""
        text_content = ""
        try:
            async with aiofiles.open(file_path, 'rb') as file:
                pdf_content = await file.read()
                pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_content))
                
                for page in pdf_reader.pages:
                    text_content += page.extract_text() + "\n"
                    
            return text_content.strip()
        except Exception as e:
            print(f"Error reading PDF: {str(e)}")
            return ""
    
    @staticmethod
    async def _extract_from_docx(file_path: str) -> str:
        """Extract text from DOCX files"""
        try:
            async with aiofiles.open(file_path, 'rb') as file:
                docx_content = await file.read()
                doc = DocxDocument(BytesIO(docx_content))
                
                text_content = ""
                for paragraph in doc.paragraphs:
                    text_content += paragraph.text + "\n"
                    
            return text_content.strip()
        except Exception as e:
            print(f"Error reading DOCX: {str(e)}")
            return ""
    
    @staticmethod
    def get_file_type(filename: str) -> str:
        """Get file type from filename"""
        return filename.split('.')[-1].lower() if '.' in filename else 'unknown'
    
    @staticmethod
    def is_supported_file_type(file_type: str) -> bool:
        """Check if file type is supported"""
        supported_types = ['txt', 'pdf', 'docx', 'doc']
        return file_type.lower() in supported_types
    
    @staticmethod
    def get_content_preview(content: str, max_length: int = 200) -> str:
        """Get a preview of the content"""
        if not content:
            return ""
        
        content = content.strip()
        if len(content) <= max_length:
            return content
        
        return content[:max_length] + "..."
