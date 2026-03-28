import json
import re
import os
import logging
import spacy
from collections import defaultdict

logger = logging.getLogger(__name__)

class SkillExtractor:
    """
    Extracts, normalizes, deduplicates technical and non-technical skills out of raw text.
    Implements a confidence scoring mechanism based on matching type and context.
    """
    def __init__(self, dictionary_path="data/skills_master.json"):
        self.dict_path = dictionary_path
        self.skills_dict = {}
        self.stacks_dict = {}
        self._load_dictionary()
        self._build_matchers()

    def _load_dictionary(self):
        if not os.path.exists(self.dict_path):
            logger.error(f"Skill dictionary not found at {self.dict_path}")
            return
            
        with open(self.dict_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.skills_dict = data.get("skills", {})
            self.stacks_dict = data.get("stacks", {})

    def _build_matchers(self):
        """
        Builds spaCy PhraseMatcher for efficient NLP-based entity recognition 
        of technical and non-technical skills.
        """
        self.canonical_map = {}
        
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except Exception:
            logger.warning("Spacy model 'en_core_web_sm' not found. Falling back to simple regex matching.")
            self.nlp = None
            
        for canonical_skill, info in self.skills_dict.items():
            self.canonical_map[canonical_skill.lower()] = (canonical_skill, 'canonical')
            for syn in info.get("synonyms", []):
                self.canonical_map[syn.lower()] = (canonical_skill, 'synonym')
                
        for stack_name in self.stacks_dict.keys():
            self.canonical_map[stack_name.lower()] = (stack_name, 'stack')

        if self.nlp:
            from spacy.matcher import PhraseMatcher
            self.matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
            patterns = []
            
            for phrase in self.canonical_map.keys():
                patterns.append(self.nlp.make_doc(phrase))
                
            self.matcher.add("SKILLS", patterns)

    def _get_base_confidence(self, match_type: str) -> float:
        """Returns base confidence score depending on how the skill was matched."""
        if match_type == 'canonical':
            return 1.0
        elif match_type == 'stack':
            return 0.95
        elif match_type == 'synonym':
            return 0.85
        return 0.70

    def extract_skills(self, text: str, section_context: str = "general") -> list:
        """
        Extract normalized skills from text using NLP PhraseMatcher. 
        Apply context boost if section is 'skills'.
        """
        extracted = {}
        
        if self.nlp:
            doc = self.nlp(text)
            matches = self.matcher(doc)
            
            for match_id, start, end in matches:
                phrase = doc[start:end].text.lower()
                
                if phrase in self.canonical_map:
                    canonical, match_type = self.canonical_map[phrase]
                    
                    confidence = self._get_base_confidence(match_type)
                    if section_context.lower() == 'skills':
                        confidence = min(1.0, confidence + 0.15)
                        
                    if match_type == 'stack':
                        for stack_skill in self.stacks_dict.get(canonical, []):
                            self._insert_extracted(extracted, stack_skill, confidence, "stack_expansion")
                    else:
                        self._insert_extracted(extracted, canonical, confidence, match_type)
        else:
            # Basic fallback if spacy not available
            words = re.findall(r'\b[\w\.\+#]+\b', text.lower())
            for i in range(len(words)):
                for j in range(1, 4):
                    if i + j > len(words): break
                    phrase = " ".join(words[i:i+j])
                    if phrase in self.canonical_map:
                        canonical, match_type = self.canonical_map[phrase]
                        confidence = self._get_base_confidence(match_type)
                        if section_context.lower() == 'skills':
                            confidence = min(1.0, confidence + 0.15)
                        if match_type == 'stack':
                            for stack_skill in self.stacks_dict.get(canonical, []):
                                self._insert_extracted(extracted, stack_skill, confidence, "stack_expansion")
                        else:
                            self._insert_extracted(extracted, canonical, confidence, match_type)

        sorted_skills = sorted(extracted.values(), key=lambda x: (-x['confidence'], x['skill']))
        return sorted_skills

    def _insert_extracted(self, extracted: dict, skill_name: str, confidence: float, match_type: str):
        """Helper to deduplicate and choose the highest confidence score for a skill"""
        category = self.skills_dict.get(skill_name, {}).get("category", "unknown") if skill_name in self.skills_dict else "unknown"
        
        if skill_name not in extracted or extracted[skill_name]['confidence'] < confidence:
            extracted[skill_name] = {
                "skill": skill_name,
                "category": category,
                "confidence": round(confidence, 2),
                "match_type": match_type
            }

if __name__ == "__main__":
    # Test
    extractor = SkillExtractor()
    sample_text = "I am an expert in Reactjs, node, and python3. I also worked with the MERN stack."
    print("General Context:", json.dumps(extractor.extract_skills(sample_text), indent=2))
    print("\nSkills Context:", json.dumps(extractor.extract_skills(sample_text, section_context="skills"), indent=2))
