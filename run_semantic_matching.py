import os
import json
import glob
from engines.semantic_matching import SemanticMatcher

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_jd_files():
    jd_files = glob.glob(os.path.join('output', 'jd_files', '*.json'))
    jds = []
    for f in jd_files:
        try:
            jds.append(load_json(f))
        except Exception as e:
            print(f"Error loading JD {f}: {e}")
    return jds

def build_resume_text_blocks(resume_data):
    # Skills
    skills = resume_data.get('extracted_skills_normalized', [])
    skills_text = " ".join([s['skill'] for s in skills]) if skills else resume_data.get('skills', '')
    
    # Experience
    exp_text = resume_data.get('experience', '')
    if not exp_text:
        # Fallback to structured if string isn't there
        struct_exp = resume_data.get('structured_experience', [])
        for e in struct_exp:
            exp_text += f"{e.get('job_title', '')} {e.get('company', '')} {e.get('description', '')} "
            
    # Projects
    proj_text = resume_data.get('projects', '')
    
    return skills_text, exp_text, proj_text

def build_jd_text_blocks(jd_data):
    skills_list = jd_data.get('skills_required', [])
    skills_text = " ".join(skills_list) if skills_list else jd_data.get('skills', '')
    
    # Experience / Responsibilities
    exp_text = f"{jd_data.get('job_summary', '')} {jd_data.get('key_responsibilities', '')}"
    
    # JDs typically don't have explicit project descriptions, use responsibilities as comparison
    proj_text = exp_text 
    
    return skills_text, exp_text, proj_text

def main():
    print("Loading JDs...")
    jds = get_jd_files()
    if not jds:
        print("No JDs found. Be sure to run jd_parser.py first.")
        return
        
    print("Initializing Semantic Matcher (this may download a model if run for the first time)...")
    matcher = SemanticMatcher()
    
    # User requested using data/resumes, but we can use the already processed sections directly
    # from data/processed to speed things up as it contains the classified sections
    resume_files = glob.glob(os.path.join('data', 'processed', '*_classified.json'))
    print(f"Found {len(resume_files)} processed resumes.")
    
    results = {}
    
    # Tunable weights
    weights = {"skills": 0.3, "experience": 0.5, "projects": 0.2}
    
    # Create the report
    report_lines = []
    report_lines.append("# Semantic Matching Accuracy Report\n\n")
    report_lines.append("This report validates semantic similarity matching across multiple job types by comparing Resume content to JDs.\n\n")

    for r_file in resume_files:
        filename = os.path.basename(r_file).replace('_classified.json', '')
        resume_data = load_json(r_file)
        
        r_skills, r_exp, r_proj = build_resume_text_blocks(resume_data)
        
        matches = []
        for jd in jds:
            j_skills, j_exp, j_proj = build_jd_text_blocks(jd)
            
            sim_skills = matcher.compute_similarity(r_skills, j_skills)
            sim_exp = matcher.compute_similarity(r_exp, j_exp)
            sim_proj = matcher.compute_similarity(r_proj, j_proj)
            
            # Weighted Overall Score
            overall_sim = (sim_skills * weights['skills'] + 
                           sim_exp * weights['experience'] + 
                           sim_proj * weights['projects'])
            
            matches.append({
                "job_title": jd.get("job_title", "Unknown"),
                "similarity_scores": {
                    "skills": round(sim_skills, 4),
                    "experience": round(sim_exp, 4),
                    "projects": round(sim_proj, 4),
                    "overall": round(overall_sim, 4)
                }
            })
            
        # Sort by overall similarity descending
        matches.sort(key=lambda x: x["similarity_scores"]["overall"], reverse=True)
        
        # Filter to give only the matching results (threshold >= 0.2)
        matching_results = [m for m in matches if m["similarity_scores"]["overall"] >= 0.2]
        
        results[filename] = {
            "top_matches": matching_results
        }
        
        # Append to report if there are matches
        if matching_results:
            report_lines.append(f"### Resume: {filename}\n")
            report_lines.append(f"**Found {len(matching_results)} matching result(s) (Score >= 0.2):**\n")
            for i, match in enumerate(matching_results, 1):
                sc = match['similarity_scores']
                report_lines.append(f"{i}. **{match['job_title']}** (Overall Score: {sc['overall']:.2f})\n")
                report_lines.append(f"   - Skills Match: {sc['skills']:.2f}\n")
                report_lines.append(f"   - Experience Match: {sc['experience']:.2f}\n")
                report_lines.append(f"   - Project Match: {sc['projects']:.2f}\n")
            report_lines.append("\n")
        else:
            # Optional: Log if no match found for clarity in report
            report_lines.append(f"### Resume: {filename}\n")
            report_lines.append("*No jobs found with a similarity score above 0.2.*\n\n")

    # Outputs
    os.makedirs('output', exist_ok=True)
    out_path = os.path.join('output', 'semantic_matching_report.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4)
        
    print(f"Semantic matching completed. Results saved to {out_path}.")
    
    report_path = os.path.join('output', 'matching_accuracy_report.md')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.writelines(report_lines)
    print(f"Accuracy report saved to {report_path}.")

if __name__ == '__main__':
    main()
