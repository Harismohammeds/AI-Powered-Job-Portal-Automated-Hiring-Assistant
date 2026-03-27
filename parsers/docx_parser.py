import docx
import os
from utils.logger import logger

logger.info("Reading DOCX file")

def extract_text_from_docx(docx_path):
    """
    Extracts text from DOCX resumes.
    - Extracts from paragraphs.
    - Extracts from tables to readable text.
    """
    if not os.path.exists(docx_path):
        logger.error(f"File not found: {docx_path}")
        return None

    try:
        doc = docx.Document(docx_path)
        full_text = []

        # Iterate through paragraphs and tables in their document order
        for block in doc.element.body:
            if block.tag.endswith('p'):  # Paragraph
                para = docx.text.paragraph.Paragraph(block, doc)
                if para.text.strip():
                    full_text.append(para.text)
            elif block.tag.endswith('tbl'):  # Table
                table = docx.table.Table(block, doc)
                for row in table.rows:
                    row_text = ' | '.join(cell.text.strip() for cell in row.cells if cell.text.strip())
                    if row_text:
                        full_text.append(row_text)

        return '\n'.join(full_text)

    except Exception as e:
        logger.error(f"Error parsing {docx_path}: {e}")
        return None
