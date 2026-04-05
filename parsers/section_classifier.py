import re
import spacy
import logging
from .skill_extractor import SkillExtractor

logger = logging.getLogger(__name__)

class ResumeSectionClassifier:
    """
    A hybrid rule-based and NLP-based text segmentor that parses raw resume text,
    identifying core sections like Skills, Work Experience, Education, Certifications, 
    and Projects.
    """
    
    SECTION_MAPPINGS = {
        "experience": [
            r"experience", r"employment", r"work history", r"career history",
            r"professional experience", r"employment history"
        ],
        "education": [
            r"education", r"academic background", r"academic qualifications",
            r"educational background", r"degrees"
        ],
        "skills": [
            r"skills", r"technical skills", r"core competencies", r"expertise",
            r"proficiencies"
        ],
        "certifications": [
            r"certifications", r"licenses", r"credentials", r"training"
        ],
        "projects": [
            r"projects", r"academic projects", r"personal projects", r"portfolio"
        ],
        "summary": [
            r"summary", r"professional summary", r"profile", r"objective", 
            r"about me"
        ]
    }

    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("Spacy model 'en_core_web_sm' not found. NLP heuristic checks might be disabled or use basic fallback.")
            self.nlp = None
            
        self._compile_regexes()
        self.skill_extractor = SkillExtractor()

    def _compile_regexes(self):
        self.compiled_rules = {}
        for section, patterns in self.SECTION_MAPPINGS.items():
            combined_pattern = "|".join([f"^{p}$|^{p}:" for p in patterns])
            self.compiled_rules[section] = re.compile(combined_pattern, re.IGNORECASE)

    def is_heading(self, line: str) -> str:
        """
        Determines if a given line is a section heading. 
        Returns the canonical section name, or None.
        """
        line_clean = line.strip()
        
        # Heuristic: Headings are usually short.
        if not line_clean or len(line_clean) > 50 or len(line_clean.split()) > 7:
            return None
            
        # NLP check: Headings rarely have verbs. If they do, they might be sentences, not headings.
        if self.nlp:
            doc = self.nlp(line_clean)
            has_verb = any(token.pos_ == "VERB" for token in doc)
            if has_verb and len(list(doc.sents)) > 1:
                return None
                
        # Regex rule matching
        for section, regex in self.compiled_rules.items():
            cl_lower = line_clean.lower()
            if regex.search(cl_lower):
                return section
                
        # Handle uppercase short terms as generic sections potentially,
        # but here we focus on explicit matches.
        return None

    def segment(self, raw_text: str) -> dict:
        """
        Segments raw resume text into classified sections and extracts skills.
        """
        sections = {
            "profile": [],
            "summary": [],
            "experience": [],
            "education": [],
            "skills": [],
            "certifications": [],
            "projects": [],
            "unclassified": []
        }
        
        current_section = "profile" # Default starting section
        
        # Split text handling possible weird spacing from tables/columns
        lines = [line.strip() for line in re.split(r'\n|\r\n', raw_text)]
        
        for line in lines:
            if not line:
                continue
                
            heading = self.is_heading(line)
            
            if heading:
                current_section = heading
            else:
                sections[current_section].append(line)
                
        # Post-process: Join lines back up
        result = {k: "\n".join(v) for k, v in sections.items() if v}
        
        # Extract skills (prioritize the "skills" section if it exists, but also scan the whole text)
        skills_text = result.get("skills", "")
        # First extract from the skills section (higher confidence boost)
        extracted_skills = self.skill_extractor.extract_skills(skills_text, section_context="skills")
        
        # Then extract from the entire text to catch scattered skills
        general_skills = self.skill_extractor.extract_skills(raw_text, section_context="general")
        
        # Merge skills (deduplicate, keeping highest confidence)
        skill_dict = {s['skill']: s for s in extracted_skills}
        for s in general_skills:
            if s['skill'] not in skill_dict or skill_dict[s['skill']]['confidence'] < s['confidence']:
                skill_dict[s['skill']] = s
                
        result["extracted_skills"] = sorted(skill_dict.values(), key=lambda x: (-x['confidence'], x['skill']))
        return result
        
if __name__ == "__main__":
    # Quick test
    sample_text = """John Doe
Software Engineer
SUMMARY
Passionate engineer with 5 years experience.
EXPERIENCE
Google - Senior Engineer (2020-Present)
Built scalable AI pipelines.
EDUCATION
B.S. Computer Science, MIT
SKILLS
Python, spacy, AWS"""
    
    classifier = ResumeSectionClassifier()
    result = classifier.segment(sample_text)
    for k, v in result.items():
        print(f"[{k.upper()}]\n{v}\n")
