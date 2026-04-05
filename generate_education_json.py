import os
import json
from parsers.pdf_parser import extract_text_from_pdf
from parsers.docx_parser import extract_text_from_docx
from parsers.education_parser import EducationParser
from engines.education_relevance import EducationScorer
from utils.file_handler import get_resumes_from_dir
from utils.logger import logger

def generate_education_report():
    resume_paths = get_resumes_from_dir('data/resumes/')
    if not resume_paths:
        logger.warning("No resumes found to process.")
        return

    parser = EducationParser()
    scorer = EducationScorer()
    
    output_data = {}

    for path in resume_paths:
        filename = os.path.basename(path)
        _, ext = os.path.splitext(path)
        raw_text = None

        try:
            if ext.lower() == '.pdf':
                raw_text = extract_text_from_pdf(path)
            elif ext.lower() == '.docx':
                raw_text = extract_text_from_docx(path)
            elif ext.lower() == '.txt':
                with open(path, 'r', encoding='utf-8') as f:
                    raw_text = f.read()

            if raw_text:
                # Basic context mocking based on filename for dynamic target role
                target_role = "Data Analyst" if "Data" in raw_text else "Personal Trainer"
                
                # Extract education and certifications
                parsed_education = parser.extract_education(raw_text)
                parsed_certifications = parser.extract_certifications(raw_text)
                
                # Process and score
                tagged_certs = scorer.tag_certifications(parsed_certifications)
                edu_score = scorer.score_education_relevance(parsed_education, target_role)
                
                output_data[filename] = {
                    "academic_profile": parsed_education,
                    "certifications": tagged_certs,
                    "education_relevance_score": round(edu_score, 2),
                    "target_role_assumed": target_role
                }
                logger.info(f"Successfully extracted education for {filename}")
            else:
                logger.warning(f"Failed to extract text from {filename}")

        except Exception as e:
            logger.error(f"Error processing {filename}: {e}")

    output_file = 'output/education_certifications.json'
    os.makedirs('output', exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=4)
        
    logger.info(f"Saved structured academic profiles to {output_file}")

if __name__ == "__main__":
    generate_education_report()
