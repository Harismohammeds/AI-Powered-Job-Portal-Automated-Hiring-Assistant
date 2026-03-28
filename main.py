import os
from parsers.pdf_parser import extract_text_from_pdf
from parsers.docx_parser import extract_text_from_docx
from parsers.section_classifier import ResumeSectionClassifier
from utils.text_cleaner import clean_text
from utils.file_handler import get_resumes_from_dir, save_cleaned_resume, save_classified_resume
from utils.logger import logger

logger.info("App started")

def process_resumes():
    """
    Main pipeline for resume text extraction and classification.
    1. Extract raw text from resumes (.pdf or .docx).
    2. Clean the extracted text based on resume patterns.
    3. Segment text into standard resume sections (e.g. Skills, Experience).
    4. Save output to processed directory.
    """
    resume_paths = get_resumes_from_dir('data/resumes/')
    
    if not resume_paths:
        logger.warning("No resumes found to process.")
        return

    logger.info(f"Starting processing for {len(resume_paths)} resumes...")
    classifier = ResumeSectionClassifier()

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
                
                # 3. Classify / Segment
                segmented_sections = classifier.segment(cleaned_text)
                
                # Extract and normalize skills w/ NLP and confidence scoring
                from parsers.skill_extractor import SkillExtractor
                skill_ext = SkillExtractor()
                
                # Combine skill extraction over full text but heavily boost what is found in the 'skills' block
                all_skills = []
                all_skills = skill_ext.extract_skills(segmented_sections.get('skills', ''), section_context='skills')
                # Append unique others from general text
                general_skills = skill_ext.extract_skills(cleaned_text, section_context='general')
                current_skill_names = {s['skill'] for s in all_skills}
                for gs in general_skills:
                    if gs['skill'] not in current_skill_names:
                        all_skills.append(gs)
                        
                segmented_sections['extracted_skills_normalized'] = sorted(all_skills, key=lambda x: -x['confidence'])
                
                # 4. Save Cleaned TXT and Segmented JSON
                save_cleaned_resume(path, cleaned_text)
                save_classified_resume(path, segmented_sections)
            else:
                logger.error(f"Failed to extract text from: {path}")
                
        except Exception as e:
            logger.error(f"Critical error during processing {path}: {e}")

    logger.info("Resume processing complete.")

if __name__ == "__main__":
    process_resumes()
