# Zecpath AI: Automated Hiring Intelligence Assistant

Zecpath AI is a production-ready suite of AI-powered tools designed to revolutionize the recruitment process. It leverages advanced Natural Language Processing (NLP) to parse, analyze, and match candidates with job opportunities, automating the preliminary stages of hiring with high precision.

---

## 🚀 Key Features

- **Advanced Resume Parsing**: Extract and structure data from PDF and DOCX resumes, identifying key sections like Skills, Experience, and Education.
- **Job Description (JD) Intelligence**: Automatically parse unstructured job descriptions into AI-ready JSON formats, normalizing skills and roles.
- **ATS Scoring Engine**: intelligent matching of candidate profiles against job requirements using sophisticated scoring algorithms.
- **Automated Screening & Classification**: AI-driven categorization of candidates based on their profiles and suitability.
- **Interview Intelligence**: Generation of targeted interview questions and automated evaluation of candidate responses.
- **Scalable Data Pipeline**: Robust architecture for handling large datasets of resumes and job postings.

---

## 🛠 Project Structure

The repository is organized into modular components for scalability and maintainability:

- **`ats_engine/`**: Core logic for Applicant Tracking System (ATS) scoring and matching.
- **`parsers/`**: Specialized engines for extracting text from diverse formats (PDF, DOCX, etc.).
- **`screening_ai/`**: AI models for automated candidate screening and profile classification.
- **`interview_ai/`**: Systems for interview question generation and response analysis.
- **`jd_parser.py`**: A specialized pipeline for parsing unstructured JDs into structured JSON.
- **`main.py`**: The entry point for the resume processing pipeline.
- **`data/`**: Training datasets, raw resumes, and job description files.
- **`output/`**: Directory for processed JSON outputs and structured data.
- **`utils/`**: Shared utilities (logging, text cleaning, file handlers).
- **`tests/`**: Comprehensive suite of unit and integration tests.

---

## ⚙️ Environment Setup

Follow these steps to set up the development environment:

### 1. Clone the Repository
```bash
git clone <repository_url>
cd Zecpath_AI
```

### 2. Configure Virtual Environment
```bash
# Initialize venv
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 📖 Usage Guide

### Processing Job Descriptions
To parse unstructured job descriptions into structured JSON:
```bash
python jd_parser.py
```
Outputs are saved in `output/jd_files/` and a combined JSON in `output/jd_parsed_output.json`.

### Processing Resumes
To extract and clean text from resumes (PDF/DOCX):
```bash
python main.py
```
Cleaned resumes are saved to the defined `processed/` directory within `data/`.

---

## 📊 Data Architecture & Standards

Zecpath AI follows a rigorous data lifecycle and metadata standard to ensure high-quality AI matching and explainable results:

- **[AI Data Flow & Lifecycle](docs/data_design/ai_data_flow.md)**: Details the end-to-end journey from raw resume upload to hiring decision.
- **[Metadata Standards](docs/data_design/metadata_standards.md)**: Universal fields used for tracking data lineage and model versioning.
- **[Core Entity Design](docs/data_design/entity_design.md)**: High-level design for Candidate and Job Profile entities.

---

## 🧪 Quality Assurance

We maintain high code quality through rigorous testing. To run the test suite:
```bash
pytest tests/
```

For detailed coding standards, refer to the [Code Standards](docs/code_standards.md).

---

## 🤝 Contributing

Contributions are welcome! Please ensure that your pull requests follow the established coding standards and include appropriate tests.
