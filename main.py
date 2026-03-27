import os
from parsers.pdf_parser import extract_text_from_pdf
from parsers.docx_parser import extract_text_from_docx
from utils.text_cleaner import clean_text
from utils.file_handler import get_resumes_from_dir, save_cleaned_resume
from utils.logger import logger

logger.info("App started")

def process_resumes():
    """
    Main pipeline for resume text extraction.
    1. Extract raw text from resumes (.pdf or .docx).
    2. Clean the extracted text based on resume patterns.
    3. Save the output to processed directory.
    """
    resume_paths = get_resumes_from_dir('data/resumes/')
    
    if not resume_paths:
        logger.warning("No resumes found to process.")
        return

    logger.info(f"Starting processing for {len(resume_paths)} resumes...")

    for path in resume_paths:
        _, ext = os.path.splitext(path)
        raw_text = None
        
        logger.info(f"Processing: {path}")

        try:
            if ext.lower() == '.pdf':
                raw_text = extract_text_from_pdf(path)
            elif ext.lower() == '.docx':
                raw_text = extract_text_from_docx(path)
            
            if raw_text:
                # 2. Extract -> Clean
                cleaned_text = clean_text(raw_text)
                
                # 3. Save
                save_cleaned_resume(path, cleaned_text)
            else:
                logger.error(f"Failed to extract text from: {path}")
                
        except Exception as e:
            logger.error(f"Critical error during processing {path}: {e}")

    logger.info("Resume processing complete.")

if __name__ == "__main__":
    process_resumes()
