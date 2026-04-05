import pdfplumber
import os
import re

# File paths
pdf_path = "Clinical Research Associate Models.pdf"
output_folder = "jds_txt"

# Create output folder
os.makedirs(output_folder, exist_ok=True)

# Extract text from PDF
full_text = ""

with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        full_text += page.extract_text() + "\n"

# Split JDs using numbering (1., 2., 3., ...)
jd_list = re.split(r'\n\d+\.\s', full_text)

# Remove empty first element
jd_list = jd_list[1:]

# Save each JD as a separate txt file
for i, jd in enumerate(jd_list, start=1):
    file_name = f"jd_{i}.txt"
    file_path = os.path.join(output_folder, file_name)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(jd.strip())

print(f"✅ {len(jd_list)} JDs saved in '{output_folder}' folder")