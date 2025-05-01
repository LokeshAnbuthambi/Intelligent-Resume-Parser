# Intelligent-Resume-Parser
This project is an AI/NLP-powered script that extracts structured information from resumes (PDF or image format) using text extraction, regular expressions, and natural language processing (NLP). The parser returns a clean JSON object containing key details such as name, contact information, skills, education, experience, certifications, and projects.

## Features Extracted
- `Full Name`
- `Email Address`
- `Phone Number`
- `LinkedIn URL`
- `Skills`
- `Education` (Degree, Institution, Year)
- `Experience` (Title, Company, Location, Duration, Description)
- `Certifications`
- `Projects`

## How It Works
Text Extraction: Uses `PyMuPDF` (for PDFs) or `Tesseract OCR` (for images) to extract raw text.
Preprocessing & Parsing:
   - Extracts email, phone, LinkedIn using regex.
   - Extracts name using `spaCy` NER or top-line heuristic.
   - Identifies sections like `EDUCATION`, `EXPERIENCE`, `CERTIFICATES`, `PROJECTS` using regex-based block segmentation.
Skills Extraction: Matches against a predefined list of technical & soft skills.
Returns: Returns a structured JSON object with all parsed data.

## Libraries & Tools Used
PyMuPDF (fitz)
pytesseract
Pillow
spacy
re
tkinter
json

## How to Run
python resume_parser.py
