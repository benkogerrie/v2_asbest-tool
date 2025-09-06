"""
Text extraction from PDF files.
"""
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_path: Path) -> str:
    """
    Extract text from PDF file using PyMuPDF.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Extracted text content
        
    Raises:
        Exception: If text extraction fails
    """
    try:
        import fitz  # PyMuPDF
        text_chunks = []
        
        with fitz.open(str(pdf_path)) as doc:
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                if text.strip():  # Only add non-empty pages
                    text_chunks.append(text)
        
        extracted_text = "\n".join(text_chunks)
        logger.info(f"Extracted {len(extracted_text)} characters from PDF: {pdf_path}")
        return extracted_text
        
    except ImportError:
        logger.error("PyMuPDF (fitz) not available. Please install: pip install PyMuPDF")
        raise Exception("PyMuPDF not available for text extraction")
    except Exception as e:
        logger.error(f"Text extraction failed for {pdf_path}: {e}")
        raise Exception(f"Text extraction failed: {e}")
