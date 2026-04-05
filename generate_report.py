import json
import os
from parsers.section_classifier import ResumeSectionClassifier
from utils.file_handler import get_resumes_from_dir
from parsers.pdf_parser import extract_text_from_pdf
from parsers.docx_parser import extract_text_from_docx

def generate_report():
    report_path = 'section_detection_report.md'
    resume_paths = get_resumes_from_dir('data/resumes/')
    
    if not resume_paths:
        print("No resumes found in data/resumes/")
        return

    classifier = ResumeSectionClassifier()

    markdown_content = "# Resume Section & Skill Detection Report\n\n"
    markdown_content += "This report details the sections and **structured skills** detected for each resume in `data/resumes` using the new Skill Extraction Engine.\n\n"

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
                
            # Run the new engine on the raw text
            processed_data = classifier.segment(raw_text)
            extracted_skills = processed_data.get("extracted_skills", [])
            
            markdown_content += f"## Resume: {filename}\n\n"
            
            markdown_content += "### 1. Detected Sections\n"
            for section in processed_data.keys():
                if section not in ["extracted_skills", "unclassified"]:
                    markdown_content += f"- {section.capitalize()}\n"
            markdown_content += "\n"
            
            markdown_content += "### 2. Structured Skills (Extracted by Engine)\n"
            if not extracted_skills:
                markdown_content += "_No skills detected based on the current master dictionary._\n\n"
            else:
                markdown_content += "| Skill | Category | Confidence | Match Type |\n"
                markdown_content += "| :--- | :--- | :--- | :--- |\n"
                for s in extracted_skills:
                    markdown_content += f"| {s['skill']} | {s['category']} | {s['confidence']} | {s['match_type']} |\n"
                markdown_content += "\n"
            
            markdown_content += "### 3. Section Content Samples\n"
            for section in ["skills", "experience", "summary"]:
                if section in processed_data:
                    content = processed_data[section]
                    markdown_content += f"**{section.capitalize()}**:\n"
                    markdown_content += "```text\n"
                    markdown_content += f"{content.strip()[:500]}... (truncated)\n" if len(content) > 500 else f"{content.strip()}\n"
                    markdown_content += "```\n\n"
            
            markdown_content += "---\n\n"
            
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
        
    print(f"Enhanced report generated successfully as {report_path}")

if __name__ == "__main__":
    generate_report()
