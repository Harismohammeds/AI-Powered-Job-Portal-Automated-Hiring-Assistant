import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
import os
from parsers.pdf_parser import extract_text_from_pdf
from parsers.docx_parser import extract_text_from_docx
from utils.text_cleaner import clean_text


class TestParsers(unittest.TestCase):

    def test_clean_text(self):
        """Test resume text cleaning logic."""
        sample_text = "John Doe\n● Experience: 5 years\n- Skills: Python, AI\n* Education: MIT"
        expected_output = "John Doe EXPERIENCE 5 years SKILLS Python, AI EDUCATION MIT"
        
        # Test cleaning (ignore case for specific words like EXPERIENCE)
        cleaned = clean_text(sample_text)
        self.assertIn("John Doe", cleaned)
        self.assertIn("EXPERIENCE", cleaned)
        self.assertIn("SKILLS", cleaned)
        self.assertNotIn("●", cleaned)
        self.assertNotIn("-", cleaned)

    def test_file_extraction_missing_file(self):
        """Test the parsers for handling missing files gracefully."""
        self.assertIsNone(extract_text_from_pdf('invalid_path.pdf'))
        self.assertIsNone(extract_text_from_docx('invalid_path.docx'))

if __name__ == '__main__':
    unittest.main()
