import os
import json
import glob
from engines.experience_scoring import ExperienceScorer

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_all_jds():
    jds = []
    jd_files = glob.glob(os.path.join('output', 'jd_files', '*.json'))
    for f in jd_files:
        try:
            jds.append(load_json(f))
        except Exception:
            pass
    return jds

def compute_skill_match(resume_skills, jd_skills):
    if not jd_skills:
        return 0.0
    
    resume_skill_names = [s['skill'].lower() for s in resume_skills]
    jd_skill_names = [s.lower() for s in jd_skills]
    
    matches = 0
    for js in jd_skill_names:
        # Check if JD skill is anywhere in resume skills (substring or exact)
        if any(js in rs or rs in js for rs in resume_skill_names):
            matches += 1
            
    return matches / len(jd_skill_names)

def main():
    scorer = ExperienceScorer()
    
    jds = load_all_jds()
    print(f"Loaded {len(jds)} Job Descriptions.")
    
    resume_files = glob.glob(os.path.join('data', 'processed', '*_classified.json'))
    print(f"Loaded {len(resume_files)} Processed Resumes.\n")
    
    results = {}
    
    for r_file in resume_files:
        filename = os.path.basename(r_file)
        resume_data = load_json(r_file)
        
        structured_exp = resume_data.get('structured_experience', [])
        extracted_skills = resume_data.get('extracted_skills_normalized', [])
        
        matches = []
        for jd in jds:
            job_title = jd.get('job_title', 'Unknown Job')
            
            # 1. Experience Relevance against JD Job Title
            exp_relevance = scorer.score_relevance(structured_exp, job_title)
            score = exp_relevance['total_relevance_score']
            
            # 2. Skill Match
            jd_req_skills = jd.get('skills_required', [])
            skill_score = compute_skill_match(extracted_skills, jd_req_skills)
            
            # Total score (60% experience, 40% skills)
            total_match = (score * 0.6) + (skill_score * 0.4)
            
            matches.append({
                "job_title": job_title,
                "experience_score": score,
                "skill_score": round(skill_score, 2),
                "total_match_score": round(total_match, 2),
                "matching_roles": exp_relevance['matching_roles']
            })
            
        # Sort by total match descending
        matches.sort(key=lambda x: -x['total_match_score'])
        
        # Save top 3
        results[filename] = {
            "top_3_jd_matches": matches[:3]
        }
        
        print(f"--- Resume: {filename} ---")
        for i, m in enumerate(matches[:3]):
            print(f"  {i+1}. {m['job_title']} (Match: {m['total_match_score']*100:.1f}%)")
            print(f"     Experience Score: {m['experience_score']} | Skill Score: {m['skill_score']}")
            if m['matching_roles']:
                print(f"     Relevant Roles found: {m['matching_roles']}")
        print("\n")

    # Save outputs
    out_path = os.path.join('output', 'jd_resume_matches.json')
    os.makedirs('output', exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4)
        
    print(f"Full JD match results saved to {out_path}!")

if __name__ == "__main__":
    main()
