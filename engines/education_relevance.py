import re
from typing import List, Dict, Any

class EducationScorer:
    """
    Handles education & certification relevance logic.
    Scores relevance based on matching target roles or fields.
    """
    def __init__(self):
        # Relevance mapping for certifications
        self.cert_categories = {
            "technology": ['aws', 'cisco', 'comptia', 'microsoft', 'google cloud', 'azure', 'oracle', 'itil'],
            "management": ['pmp', 'scrum', 'agile', 'six sigma', 'prince2', 'cbap'],
            "finance": ['cfa', 'cpa', 'frm', 'acca', 'cima'],
            "healthcare": ['cpr', 'bls', 'acls', 'rn', 'nclex', 'ptcb'],
            "fitness": ['nasm', 'ace', 'issa', 'acsm', 'nsca']
        }
        
    def tag_certifications(self, certifications: List[str]) -> List[Dict[str, str]]:
        """
        Tags extracted certifications with relevance categories.
        """
        tagged_certs = []
        for cert in certifications:
            cert_lower = cert.lower()
            assigned_category = "General/Other"
            for category, keywords in self.cert_categories.items():
                if any(kw in cert_lower for kw in keywords):
                    assigned_category = category.capitalize()
                    break
            
            tagged_certs.append({
                "certification_name": cert,
                "category": assigned_category
            })
            
        return tagged_certs
        
    def score_education_relevance(self, education_data: List[Dict[str, Any]], target_role: str) -> float:
        """
        Scores academic profile relevance for a specific target role.
        Returns a score between 0.0 and 1.0.
        """
        if not education_data or not target_role:
            return 0.0
            
        target_role_lower = target_role.lower()
        score = 0.0
        
        for edu in education_data:
            degree = edu.get('degree', '').lower()
            field = edu.get('field_of_study', '')
            if field:
                field = field.lower()
            else:
                field = ''
                
            # Base score for having a degree
            if degree in ['bachelor', 'master', 'phd']:
                score += 0.3
            elif degree in ['associate']:
                score += 0.15
                
            # Relevance score based on field of study matching target role keywords loosely
            role_keywords = set(target_role_lower.split())
            field_tokens = set(re.findall(r'\w+', field))
            
            if role_keywords.intersection(field_tokens):
                score += 0.5
            elif field:
                # Has some field, minor relevance
                score += 0.2
                
        return min(1.0, score)
