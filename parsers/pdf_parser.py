import pdfplumber
import os
from utils.logger import logger

logger.info("Parsing PDF")

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from PDF resumes with handling for:
    - Multi-page PDFs.
    - Tables to readable text.
    - Proper column merging.
    - Ignoring images.
    """
    if not os.path.exists(pdf_path):
        logger.error(f"File not found: {pdf_path}")
        return None

    full_text = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                logger.info(f"Parsing page {i+1} of {pdf_path}...")
                
                # 1. Extract tables separately and convert to text
                table_text = ""
                tables = page.extract_tables()
                if tables:
                    for table in tables:
                        # Convert table (list of lists) to joined row strings
                        for row in table:
                            # Filter out None and join cells with space
                            clean_row = [cell if cell is not None else "" for cell in row]
                            table_text += " | ".join(clean_row) + "\n"
                
                # 2. Extract layout-aware text (handles columns properly)
                # This combines text from the layout without being as noisy as extract_text()
                page_text = page.extract_text(layout=True)
                
                if not page_text and not table_text:
                    logger.warning(f"No text found on page {i+1} of {pdf_path}.")
                    continue
                
                # Combine extracted layout text and table text
                full_text.append(f"{page_text or ''}\n\n{table_text or ''}")
                
        return "\n\n".join(full_text)
        
    except Exception as e:
        logger.error(f"Error parsing {pdf_path}: {e}")
        return None
