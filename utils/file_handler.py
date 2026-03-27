import os
from utils.logger import logger

logger.info("File handler started")

def get_resumes_from_dir(directory='data/resumes/'):
    """
    Retrieves all resume file paths from the specified directory.
    Filter for .pdf and .docx files.
    """
    if not os.path.exists(directory):
        logger.error(f"Directory not found: {directory}")
        return []

    resumes = []
    # Loop over all files in the directory
    for filename in os.listdir(directory):
        # Extract file extension 
        _, ext = os.path.splitext(filename)
        
        # Filter for .pdf and .docx extensions
        if ext.lower() in ['.pdf', '.docx']:
            resumes.append(os.path.abspath(os.path.join(directory, filename)))
            
    return resumes

def save_cleaned_resume(raw_filename, cleaned_text, output_dir='data/processed/'):
    """
    Saves the cleaned resume text as a .txt file in the target directory.
    Replaces the original file extension with .txt.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Clean the filename for the output file
    # Get only the base name and replace the extension with .txt
    base_name = os.path.splitext(os.path.basename(raw_filename))[0]
    output_filename = f"{base_name}_cleaned.txt"
    output_path = os.path.join(output_dir, output_filename)

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_text)
        logger.info(f"Successfully saved cleaned resume to: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Failed to save {output_filename}: {e}")
        return None
