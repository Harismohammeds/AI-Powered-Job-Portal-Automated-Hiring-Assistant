import re
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class EducationParser:
    """
    Extracts and normalizes educational qualifications and certifications from resume text.
    """
    def __init__(self):
        # Degree normalization mapping
        self.degree_map = {
            r'\b(bachelor(?:s)?|b\.?s\.?|b\.?a\.?|b\.?sc\.?|b\.?e\.?|b\.?tech\.?)\b': 'Bachelor',
            r'\b(master(?:s)?|m\.?s\.?|m\.?a\.?|m\.?sc\.?|m\.?e\.?|m\.?tech\.?|mba)\b': 'Master',
            r'\b(doctorate|ph\.?d\.?|d\.?phil\.?)\b': 'PhD',
            r'\b(associate(?:s)?|a\.?s\.?|a\.?a\.?)\b': 'Associate',
            r'\b(high school|diploma|ged)\b': 'High School'
        }
        
        # Certification keywords to detect certifications
        self.cert_keywords = [
            'certified', 'certification', 'certificate', 'cpr', 'bls', 'acls', 'aws', 'cisco', 'comptia', 
            'pmp', 'scrum', 'six sigma', 'cfa', 'cpa'
        ]

    def extract_education(self, text: str) -> List[Dict[str, Any]]:
        """
        Extracts structured education data: degree, field, institution, year.
        Basic heuristic-based extraction.
        """
        education_list = []
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # Detect Degree
            detected_degree = None
            for pattern, norm_degree in self.degree_map.items():
                if re.search(pattern, line_lower):
                    detected_degree = norm_degree
                    break
            
            if detected_degree:
                # Heuristics for Institution: usually capitalized words, containing 'University', 'College', 'Institute'
                institution = self._extract_institution(line)
                if not institution and i+1 < len(lines):
                    institution = self._extract_institution(lines[i+1])
                    
                # Field of study: looking for 'in [Field]'
                field = self._extract_field(line)
                
                # Graduation year: 4 digit number that looks like a recent year
                year = self._extract_year(line)
                if not year and i+1 < len(lines):
                    year = self._extract_year(lines[i+1])
                    
                education_list.append({
                    "degree": detected_degree,
                    "field_of_study": field,
                    "institution": institution,
                    "graduation_year": year,
                    "raw_text": line.strip()
                })
                
        # Deduplication
        deduped_ed = []
        seen = set()
        for ed in education_list:
            key = f"{ed['degree']}_{ed['institution']}_{ed['graduation_year']}"
            if key not in seen:
                seen.add(key)
                deduped_ed.append(ed)
                
        return deduped_ed

    def extract_certifications(self, text: str) -> List[str]:
        """
        Extracts certifications from text based on keywords.
        """
        certifications = set()
        lines = text.split('\n')
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in self.cert_keywords):
                # Clean and add the line as a certification (simple heuristic)
                cleaned = re.sub(r'[^a-zA-Z0-9\s,\.-]', '', line).strip()
                if 5 < len(cleaned) < 100: # reasonable length for a cert name
                    certifications.add(cleaned)
                    
        return list(certifications)

    def _extract_institution(self, text: str) -> str:
        # Match capitalized words followed by University, College, Institute, etc.
        match = re.search(r'([A-Z][a-zA-Z]*\s+)*(University|College|Institute|School|Academy)(?:\s+of\s+[A-Z][a-zA-Z]*)*', text)
        if match:
            return match.group(0).strip()
        return None

    def _extract_field(self, text: str) -> str:
        match = re.search(r'\b(?:in|of)\s+([A-Z][a-zA-Z]*\s*(?:and|&)?\s*[A-Z][a-zA-Z]*)', text)
        if match:
            field = match.group(1).strip()
            if field.lower() not in ['the', 'a', 'an']:
                return field
        return None

    def _extract_year(self, text: str) -> str:
        # Match years between 1950 and 2030
        years = re.findall(r'\b(19[5-9]\d|20[0-3]\d)\b', text)
        if years:
            return max(years) # return the latest year assumed as graduation
        return None
