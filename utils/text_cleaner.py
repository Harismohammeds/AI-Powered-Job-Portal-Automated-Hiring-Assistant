import re

def clean_text(text):
    """
    Cleans raw text from resumes.
    - Removes noise and symbols.
    - Normalizes whitespace.
    - Standardizes capitalization.
    - Preserves structural clues (headers).
    """
    # 1. Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # 2. Clean noise/symbols (keep standard punctuation)
    # Removing bullet points like ●, ■, ◆, etc.
    text = re.sub(r'[●■◆•\-\*]', ' ', text)
    
    # 3. Standardize whitespace again after symbol removal
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 4. Heading cleaning - Ensure they are prominent
    # Common headers: Skills, Education, Experience, Work Experience, Projects, Certifications
    headers = ["SKILLS", "EDUCATION", "EXPERIENCE", "WORK EXPERIENCE", "PROJECTS", "CERTIFICATIONS", "SUMMARY"]
    for header in headers:
        # Match headers even if they are in mixed case or followed by a colon
        pattern = re.compile(rf'\b{header}\b:?', re.IGNORECASE)
        # Standardize to uppercase and add a newline before/after for structure
        text = pattern.sub(f"\n\n{header}\n", text)

    # 5. Final whitespace adjustment
    text = re.sub(r'\n\s+', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text).strip()
    
    return text

def normalize_headings(text):
    """Specific normalization for resume headings."""
    # This could be more advanced with machine learning, 
    # but for now, we use rule-based standardization.
    return text
