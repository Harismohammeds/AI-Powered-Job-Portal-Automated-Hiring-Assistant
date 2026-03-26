# Zecpath AI Engine

This repository contains the core AI systems, parsers, classifiers, scoring algorithms, and screening automation functionality for the Zecpath platform.

## Environment Setup
To establish the development environment, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd Zecpath_AI
   ```

2. **Setup Virtual Environment:**
   Run the following commands to create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\Activate.ps1
   # Linux/Mac:
   source venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Repository Structure
- `data/`: Datasets for training, unparsed resumes, job descriptions, metadata.
- `parsers/`: Logic for extracting structured text from PDFs, DOCX, and URLs.
- `ats_engine/`: ATS scoring modules, matching candidates to job profiles.
- `screening_ai/`: AI models for candidate screening and auto-classification.
- `interview_ai/`: Logic handling interview question generation and response evaluation.
- `scoring/`: Generic or global scoring logic and metrics frameworks.
- `utils/`: Common utilities like loggers, configuration loaders, etc.
- `tests/`: Unit and integration testing directory (`pytest`).
- `docs/`: Additional documentation and code standards.

## Code Standards
Read the [Code Standards](docs/code_standards.md) for detailed guidelines on writing clean, maintainable, and well-documented code.

## Running Tests
To run tests across the application:
```bash
pytest tests/
```
