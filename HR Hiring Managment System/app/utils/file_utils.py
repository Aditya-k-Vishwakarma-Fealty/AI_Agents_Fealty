"""
File utility functions for resume handling and text extraction.
"""
import os
import uuid
from typing import Tuple, Optional
from pathlib import Path
import logging

from PyPDF2 import PdfReader
from docx import Document

from app.config.settings import settings

logger = logging.getLogger(__name__)

# Embedding model (removed to save memory, using OpenAI instead)


def validate_file_type(filename: str) -> Tuple[bool, Optional[str]]:
    """
    Validate if file type is allowed.
    
    Args:
        filename: Name of the file
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not filename:
        return False, "Filename is empty"
    
    file_ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    
    if file_ext not in settings.allowed_extensions_list:
        return False, f"File type .{file_ext} not allowed. Allowed types: {', '.join(settings.allowed_extensions_list)}"
    
    return True, None


def save_resume_file(file_content: bytes, filename: str, candidate_id: int) -> str:
    """
    Save uploaded resume file to disk.
    
    Args:
        file_content: File content as bytes
        filename: Original filename
        candidate_id: Candidate ID
    
    Returns:
        str: Path to saved file
    """
    try:
        # Ensure upload directory exists
        settings.ensure_directories()
        
        # Generate unique filename
        file_ext = filename.rsplit('.', 1)[-1].lower()
        unique_filename = f"candidate_{candidate_id}_{uuid.uuid4().hex[:8]}.{file_ext}"
        file_path = os.path.join(settings.resume_upload_dir, unique_filename)
        
        # Save file
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        logger.info(f"Saved resume file: {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"Error saving resume file: {e}")
        raise


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text content from PDF file.
    
    Args:
        file_path: Path to PDF file
    
    Returns:
        str: Extracted text
    """
    try:
        reader = PdfReader(file_path)
        text = ""
        
        for page in reader.pages:
            text += page.extract_text() + "\n"
        
        logger.info(f"Extracted text from PDF: {file_path}")
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        raise


def extract_text_from_docx(file_path: str) -> str:
    """
    Extract text content from DOCX file.
    
    Args:
        file_path: Path to DOCX file
    
    Returns:
        str: Extracted text
    """
    try:
        doc = Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        
        logger.info(f"Extracted text from DOCX: {file_path}")
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting text from DOCX: {e}")
        raise


def extract_text_from_resume(file_path: str) -> str:
    """
    Extract text from resume file (auto-detect format).
    
    Args:
        file_path: Path to resume file
    
    Returns:
        str: Extracted text
    """
    file_ext = file_path.rsplit('.', 1)[-1].lower()
    
    if file_ext == 'pdf':
        return extract_text_from_pdf(file_path)
    elif file_ext == 'docx':
        return extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_ext}")





def delete_resume_file(file_path: str):
    """
    Delete resume file from disk.
    
    Args:
        file_path: Path to file to delete
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Deleted resume file: {file_path}")
        else:
            logger.warning(f"File not found for deletion: {file_path}")
    except Exception as e:
        logger.error(f"Error deleting resume file: {e}")
        raise
