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
            elif ext.lower() == '.txt':
                with open(path, 'r', encoding='utf-8') as f:
                    raw_text = f.read()
            
            if raw_text:
                # 2. Extract -> Clean
                cleaned_text = clean_text(raw_text)
                
                # 3. Classify / Segment
                processed_data = classifier.segment(cleaned_text)
            
            # --- New Experience Parsing & Relevance Engine Integration ---
            exp_text = processed_data.get('experience', '')
            if exp_text:
                from parsers.experience_parser import ExperienceParser
                from engines.experience_scoring import ExperienceScorer
                
                exp_parser = ExperienceParser()
                extracted_exp = exp_parser.parse_experience(exp_text)
                exp_metrics = exp_parser.calculate_metrics(extracted_exp)
                
                # Update processed data with structured experience
                processed_data['structured_experience'] = extracted_exp
                processed_data['experience_metrics'] = exp_metrics
                
                # Mock target role based on filename or just provide a default baseline
                # For demonstration, let's assume the target role is derived broadly, 
                # but we'll use a generic "Data Analyst" or "Personal Trainer" based on keywords
                target_role = "Data Analyst" if "Data" in raw_text else "Personal Trainer"
                
                scorer = ExperienceScorer()
                relevance = scorer.score_relevance(extracted_exp, target_role)
                processed_data['experience_relevance'] = dict(relevance, target_role_assumed=target_role)
            # -------------------------------------------------------------
            
                # Use json schema format if available or just raw json dump confidence scoring
                from parsers.skill_extractor import SkillExtractor
                skill_ext = SkillExtractor()
                
                # Combine skill extraction over full text but heavily boost what is found in the 'skills' block
                all_skills = []
                all_skills = skill_ext.extract_skills(processed_data.get('skills', ''), section_context='skills')
                # Append unique others from general text
                general_skills = skill_ext.extract_skills(cleaned_text, section_context='general')
                current_skill_names = {s['skill'] for s in all_skills}
                for gs in general_skills:
                    if gs['skill'] not in current_skill_names:
                        all_skills.append(gs)
                        
                processed_data['extracted_skills_normalized'] = sorted(all_skills, key=lambda x: -x['confidence'])
                
                # --- New Education Parsing & Relevance Engine Integration ---
                from parsers.education_parser import EducationParser
                from engines.education_relevance import EducationScorer
                
                edu_parser = EducationParser()
                edu_scorer = EducationScorer()
                
                edu_text = processed_data.get('education', '')
                if not edu_text:
                    edu_text = raw_text # Fallback to raw text if section classifier missed it
                    
                parsed_education = edu_parser.extract_education(edu_text)
                parsed_certifications = edu_parser.extract_certifications(raw_text) # Certs can be anywhere
                tagged_certs = edu_scorer.tag_certifications(parsed_certifications)
                target_role_for_edu = "Data Analyst" if "Data" in raw_text else "Personal Trainer"
                edu_score = edu_scorer.score_education_relevance(parsed_education, target_role_for_edu)
                
                processed_data['academic_profile'] = parsed_education
                processed_data['certifications'] = tagged_certs
                processed_data['education_relevance_score'] = round(edu_score, 2)
                # -------------------------------------------------------------
                
                # 4. Save Cleaned TXT and Segmented JSON
                save_cleaned_resume(path, cleaned_text)
                save_classified_resume(path, processed_data)
            else:
                logger.error(f"Failed to extract text from: {path}")
                
        except Exception as e:
            logger.error(f"Critical error during processing {path}: {e}")

    logger.info("Resume processing complete.")
    
    # Automatically update the aggregated skills JSON
    try:
        from generate_skills_json import generate_skills_json
        generate_skills_json()
        logger.info("Updated samples/skill_master.json with all resumes.")
    except Exception as e:
        logger.error(f"Failed to update aggregated skills JSON: {e}")

if __name__ == "__main__":
    process_resumes()
