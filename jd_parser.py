import os
import json
import re

def clean_text(text):
    """
    Cleans job description text by removing symbols, bullet points, 
    extra spaces, and converting to lowercase.
    """
    if not text:
        return ""
    # Remove emojis and special symbols
    text = re.sub(r'[^\w\s\.\,\-\(\)\/\:]', '', text)
    # Remove bullet points (often • or - at start of lines)
    text = re.sub(r'^\s*[\u2022\-\*]\s*', '', text, flags=re.MULTILINE)
    # Remove extra spaces and newlines
    text = re.sub(r'\s+', ' ', text).strip()
    return text.lower()

def normalize_skills(skills_list):
    """
    Maps similar skills into standard forms.
    """
    mapping = {
        "clinical trial monitoring": "clinical monitoring",
        "site initiation visits": "site monitoring",
        "monitoring visits": "site monitoring",
        "close-out visits": "site monitoring",
        "source data verification": "SDV",
        "case report forms": "CRF review",
        "crfs": "CRF review",
        "good clinical practice": "GCP compliance",
        "gcp guidelines": "GCP compliance",
        "regulatory compliance": "regulatory knowledge",
        "regulatory guidelines": "regulatory knowledge",
        "documentation & organizational skills": "documentation",
        "organizational skills": "organization",
        "attention to detail": "attention to detail",
        "site management": "site management",
        "tmf": "TMF maintenance",
        "trial master file": "TMF maintenance",
        "edc": "EDC systems",
        "ctms": "CTMS systems"
    }
    
    normalized = []
    for skill in skills_list:
        skill_clean = skill.lower().strip()
        found = False
        for key, val in mapping.items():
            if key in skill_clean:
                normalized.append(val)
                found = True
        if not found:
            normalized.append(skill_clean)
    
    # Also add keyword tagging
    keywords = ["GCP", "SDV", "Monitoring", "Regulatory"]
    for kw in keywords:
        if any(kw.lower() in s.lower() for s in normalized):
            if kw not in normalized:
                normalized.append(kw)
                
    return sorted(list(set(normalized)))

def normalize_roles(job_title):
    """
    Maps similar job titles into standard roles and identifies career level.
    """
    title_lower = job_title.lower()
    
    # Normalization mapping
    role_mapping = {
        "junior clinical research associate": "clinical research associate",
        "senior cra": "clinical research associate",
        "field cra": "clinical research associate",
        "in-house cra": "clinical research associate",
        "oncology cra": "clinical research associate",
        "cardiology cra": "clinical research associate",
        "traveling cra": "clinical research associate",
        "remote cra": "clinical research associate",
        "neurology cra": "clinical research associate",
        "infectious disease cra": "clinical research associate",
        "vaccine cra": "clinical research associate",
        "regulatory cra": "clinical research associate",
        "pharmacovigilance cra": "clinical research associate",
        "medical device cra": "clinical research associate",
        "cra i": "clinical research associate",
        "cra ii": "clinical research associate",
        "cra iii": "clinical research associate"
    }
    
    normalized_role = job_title
    for key, val in role_mapping.items():
        if key in title_lower:
            normalized_role = val
            break
            
    # Level Identification
    level = "Mid Level"
    entry_keywords = ["junior", "assistant", "coordinator", "cta", "crc", "trainee"]
    senior_keywords = ["senior", "lead", "manager", "principal", "director", "head", "specialist"]
    
    if any(kw in title_lower for kw in entry_keywords):
        level = "Entry Level"
    elif any(kw in title_lower for kw in senior_keywords):
        level = "Senior Level"
        
    return normalized_role, level

def extract_job_title(section):
    match = re.search(r'^\d+\.\s*(.*?)(?:\n|$)', section)
    if match:
        return match.group(1).strip()
    return "Unknown Title"

def extract_skills(section):
    skills = []
    # Extract from Skills section
    skills_match = re.search(r'Skills(.*?)(?:Work Environment|Career Path|$)', section, re.DOTALL | re.IGNORECASE)
    if skills_match:
        items = re.findall(r'[•\*\-]\s*(.*?)(?:\n|$)', skills_match.group(1))
        skills.extend(items)
        # If no bullet points, split by newline or comma
        if not items:
            skills.extend([s.strip() for s in skills_match.group(1).split('\n') if s.strip()])
            
    # Extract from Responsibilities section
    resp_match = re.search(r'Key Responsibilities(.*?)(?:Qualifications|Skills|$)', section, re.DOTALL | re.IGNORECASE)
    if resp_match:
        items = re.findall(r'[•\*\-]\s*(.*?)(?:\n|$)', resp_match.group(1))
        # Add some key terms if they appear in responsibilities
        if "Source Data Verification" in resp_match.group(1):
            skills.append("Source Data Verification (SDV)")
        if "Good Clinical Practice" in resp_match.group(1):
            skills.append("Good Clinical Practice (GCP)")
            
    return [s for s in skills if s]

def extract_education(section):
    edu_list = []
    qual_match = re.search(r'Qualifications(.*?)(?:Skills|$)', section, re.DOTALL | re.IGNORECASE)
    if qual_match:
        text = qual_match.group(1)
        # Keywords to look for
        keywords = ["B.Pharm", "M.Pharm", "Life Sciences", "Nursing", "PharmD", "Biotechnology", "Biostatistics", "Microbiology", "Biomedical Engineering", "BSc", "MSc", "Degree in", "Bachelor", "Master"]
        for kw in keywords:
            if kw.lower() in text.lower():
                edu_list.append(kw)
    return sorted(list(set(edu_list)))

def extract_experience(section):
    # Search for year ranges like 1–3 years, 3–6+ years
    match = re.search(r'(\d+[\–\-]\d+\+?\s*years?)', section, re.IGNORECASE)
    if match:
        return match.group(1)
    
    # Try alternate pattern
    match = re.search(r'(\d+\+?\s*years?)', section, re.IGNORECASE)
    if match:
        return match.group(1)
        
    return "Not specified"

def extract_work_environment(section):
    env_match = re.search(r'Work Environment(.*?)(?:Career Path|$)', section, re.DOTALL | re.IGNORECASE)
    if env_match:
        text = env_match.group(1).strip()
        # Clean text and split by common separators
        envs = re.split(r'[,\n\/]', text)
        return [clean_text(e) for e in envs if e.strip() and len(e.strip()) > 1]
    return []

def extract_section(section, start_marker, end_markers):
    """
    Extracts text between a start marker and any of the end markers.
    """
    # Escaping markers for regex
    esc_start = re.escape(start_marker)
    # Match the start marker and capture until any end marker or end of string
    # We use a non-greedy .*? and a lookahead for the end markers
    pattern = rf'{esc_start}\s*(.*?)(?=\n\s*(?:{"|".join(map(re.escape, end_markers))})|$)'
    match = re.search(pattern, section, re.DOTALL | re.IGNORECASE)
    if match:
        text = match.group(1).strip()
        # Clean bullet points and formatting
        lines = [re.sub(r'^[^\w\s]\s*', '', line).strip() for line in text.split('\n') if line.strip()]
        # Remove any leading marker names if they accidentally got included
        return [l for l in lines if l.lower() not in [m.lower() for m in end_markers]]
    return []

def build_jd_object(section):
    job_title = extract_job_title(section)
    
    # Define markers for section extraction in exact order found in text
    markers = ["Job Summary", "Key Responsibilities", "Qualifications", "Skills", "Work Environment", "Career Path"]
    
    # Extract exact sections as requested
    job_summary_list = extract_section(section, "Job Summary", markers[1:])
    job_summary = " ".join(job_summary_list)
    
    key_responsibilities = extract_section(section, "Key Responsibilities", markers[2:])
    qualifications = extract_section(section, "Qualifications", markers[3:])
    skills = extract_section(section, "Skills", markers[4:])
    work_environment = extract_section(section, "Work Environment", markers[5:])
    career_path = extract_section(section, "Career Path", [r"\d+\.\s"]) # Until next job number
    
    # Structured fields for AI
    norm_skills = normalize_skills(skills + key_responsibilities)
    edu = extract_education(section)
    exp = extract_experience(section)
    
    # Identify career level
    _, level = normalize_roles(job_title)

    # Return ordered dictionary
    from collections import OrderedDict
    jd_obj = OrderedDict()
    jd_obj["job_title"] = job_title
    jd_obj["career_level"] = level
    jd_obj["category"] = "Clinical Research"
    jd_obj["job_summary"] = job_summary
    jd_obj["key_responsibilities"] = key_responsibilities
    jd_obj["qualifications"] = qualifications
    jd_obj["skills"] = skills
    jd_obj["work_environment"] = work_environment
    jd_obj["career_path"] = career_path
    
    # Keep the refined fields for AI matching
    jd_obj["skills_required"] = norm_skills
    jd_obj["education_required"] = edu
    jd_obj["experience_required"] = exp
    
    return jd_obj

def save_each_job_to_file(jd_objects, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    else:
        # Try to clear the directory without deleting the directory itself
        # This is more robust against permission errors if the folder is open
        for filename in os.listdir(output_dir):
            file_path = os.path.join(output_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Warning: Could not delete {filename}: {e}")
        
    # Track base names for duplicate handling within the list
    filenames_count = {}
    
    for i, jd in enumerate(jd_objects, start=1):
        # Generate filename base
        clean_title = jd["job_title"].lower()
        base_name = re.sub(r'\s+', '_', clean_title)
        base_name = re.sub(r'[^\w_]', '', base_name)
        
        # Handle duplicates of the same title
        suffix = ""
        if base_name in filenames_count:
            filenames_count[base_name] += 1
            suffix = f"_{filenames_count[base_name]}"
        else:
            filenames_count[base_name] = 1
            
        # Format index with leading zero (e.g., 01, 02... 61)
        filename = f"{i:02d}_{base_name}{suffix}.json"
            
        file_path = os.path.join(output_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            # Use json.dump with the OrderedDict to preserve order
            json.dump(jd, f, indent=2, ensure_ascii=False)
            
    print(f"Saved {len(jd_objects)} jobs to {output_dir}")

def main():
    input_file = r'c:\Users\LOQ\OneDrive\Desktop\Zecpath_AI\data\jobs_data.txt\1. Clinical Trial Assistant (CTA).txt'
    output_dir = r'c:\Users\LOQ\OneDrive\Desktop\Zecpath_AI\output\jd_files'
    combined_file = r'c:\Users\LOQ\OneDrive\Desktop\Zecpath_AI\output\jd_parsed_output.json'
    
    if not os.path.exists(input_file):
        print(f"Input file not found: {input_file}")
        return

    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Split content by job number patterns (e.g., "2. Clinical Research Coordinator")
    # We use a lookahead to split before the next number at start of line
    jobs_raw = re.split(r'\n(?=\d+\.\s)', content)
    
    parsed_jobs = []
    for job_raw in jobs_raw:
        if job_raw.strip():
            jd_obj = build_jd_object(job_raw)
            if jd_obj["job_title"] != "Unknown Title":
                parsed_jobs.append(jd_obj)
                
    # Save individual files
    save_each_job_to_file(parsed_jobs, output_dir)
    
    # Save combined file
    with open(combined_file, 'w', encoding='utf-8') as f:
        json.dump(parsed_jobs, f, indent=2, ensure_ascii=False)
        print(f"Saved combined output to {combined_file}")

if __name__ == "__main__":
    main()
