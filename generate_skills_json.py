import json
import os
from parsers.section_classifier import ResumeSectionClassifier
from utils.file_handler import get_resumes_from_dir
from parsers.pdf_parser import extract_text_from_pdf
from parsers.docx_parser import extract_text_from_docx

def generate_skills_json():
    output_path = os.path.join('samples', 'skill_master.json')
    resume_paths = get_resumes_from_dir('data/resumes/')
    
    if not os.path.exists('samples'):
        os.makedirs('samples')

    if not resume_paths:
        print("No resumes found in data/resumes/")
        return

    classifier = ResumeSectionClassifier()
    all_resume_skills = []

    for path in resume_paths:
        filename = os.path.basename(path)
        _, ext = os.path.splitext(path)
        raw_text = ""
        
        try:
            if ext.lower() == '.pdf':
                raw_text = extract_text_from_pdf(path)
            elif ext.lower() == '.docx':
                raw_text = extract_text_from_docx(path)
            elif ext.lower() == '.txt':
                with open(path, 'r', encoding='utf-8') as f:
                    raw_text = f.read()
            
            if not raw_text:
                continue
                
            processed_data = classifier.segment(raw_text)
            extracted_skills = processed_data.get("extracted_skills", [])
            
            current_resume_entry = {
                "id": filename,
                "skills": []
            }
            
            for s in extracted_skills:
                current_resume_entry["skills"].append({
                    "skill name": s["skill"],
                    "confidence_score": s["confidence"],
                    "source": s["match_type"]
                })
            
            all_resume_skills.append(current_resume_entry)
            
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_resume_skills, f, indent=4)
        
    print(f"Structured skills JSON generated as {output_path}")

if __name__ == "__main__":
    generate_skills_json()
