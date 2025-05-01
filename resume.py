import re
import json
import spacy
import fitz
import pytesseract
from PIL import Image

nlp = spacy.load("en_core_web_sm")

def extract_text_from_pdf(file_path):
    try:
        with fitz.open(file_path) as doc:
            text = ""
            for page in doc:
                text += page.get_text()
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None

def extract_text_from_image(file_path):
    try:
        img = Image.open(file_path)
        text = pytesseract.image_to_string(img)
        return text
    except Exception as e:
        print(f"Error extracting text from image: {e}")
        return None

def extract_email(text):
    email_match = re.search(r"\b[\w.-]+?@\w+?\.\w+?\b", text)
    return email_match.group(0) if email_match else None


def extract_phone_number(text):
    phone_match = re.search(r"\b(?:\+?\d{1,3}[- ]?)?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}\b", text)
    return phone_match.group(0) if phone_match else None


def extract_linkedin(text):
    linkedin_match = re.search(r"(https?://)?(www\.)?linkedin\.com/in/\S+", text)
    return linkedin_match.group(0) if linkedin_match else None


def extract_skills(text):
    skills_keywords = [
        "Python", "SQL", "Power BI", "Tableau", "Excel", "Machine Learning",
        "Deep Learning", "Data Science", "Java", "C++", "R", "NLP",
        "TensorFlow", "PyTorch", "JavaScript", "HTML", "CSS", "React",
        "Angular", "Node.js", "AWS", "Azure", "GCP", "Docker", "Kubernetes",
        "Git", "Agile", "Scrum", "Communication Skills", "Problem Solving",
        "Data Analysis", "Data Visualization", "Project Management", "Leadership",
        "Teamwork", "Time Management", "Critical Thinking", "Sales", "Marketing",
        "Finance", "Accounting"
    ]
    extracted_skills = re.findall(r"(?i)\b(" + "|".join(re.escape(skill) for skill in skills_keywords) + r")\b", text)
    return list(set(extracted_skills))


def extract_education(text):
    education_details = []
    # Define regex patterns for degree, institution, and year
    degree_keywords = r"(B\.?Tech|M\.?Tech|MBA|B\.?Sc|M\.?Sc|B\.?E|M\.?E|Bachelor|Master|Ph\.?D|Diploma|Certificate|High School|Graduate)"
    institution_keywords = r"(University|College|Institute|School|Academy|Department)"
    year_pattern = r"(19|20)\d{2}(?:-(19|20)\d{2})?"

    match = re.search(r"(EDUCATION)(.*?)(CERTIFICATES|EXPERIENCE|PROJECTS|SKILLS|TECHNICAL SKILLS|$)", text, re.IGNORECASE | re.DOTALL)
    if match:
        education_text = match.group(2)
        lines = [line.strip() for line in education_text.strip().splitlines() if line.strip()]
        i = 0
        while i < len(lines):
            combined = " ".join(lines[i:i+3])
            degree_match = re.search(degree_keywords, combined, re.IGNORECASE)
            institution_match = re.search(institution_keywords + r"[\w\s,.-]*", combined, re.IGNORECASE)
            year_match = re.search(year_pattern, combined)

            degree = degree_match.group(0) if degree_match else None
            institution = institution_match.group(0).strip() if institution_match else None
            year = year_match.group(0) if year_match else None

            if degree or institution or year:
                education_details.append({
                    "degree": degree,
                    "institution": institution,
                    "year": year
                })
            i += 3
    return education_details



def extract_experience(text):
    experience_details = []
    match = re.search(r"\n?EXPERIENCE\s*\n(.*?)(\n(?:EDUCATION|CERTIFICATES|PROJECTS|SKILLS|LANGUAGE)\s*\n|$)", text, re.IGNORECASE | re.DOTALL)

    if not match:
        return []

    experience_text = match.group(1).strip()
    lines = [line.strip() for line in experience_text.splitlines() if line.strip()]
    i = 0

    while i < len(lines):
        title = company = location = duration = ""
        description_lines = []
        header_match = re.match(r"(.+?),\s*(.+?),\s*(.+?)\.?$", lines[i])
        if header_match:
            title = header_match.group(1).strip()
            company = header_match.group(2).strip()
            location = header_match.group(3).strip()
            i += 1

            if i < len(lines) and re.match(r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|\w+)\s+\d{4}\s*[-–]\s*(Present|\w+\s+\d{4})", lines[i], re.IGNORECASE):
                duration = lines[i].strip()
                i += 1

            while i < len(lines):
                if re.match(r".+?,\s*.+?,\s*.+?\.", lines[i]):
                    break
                if re.search(r"(EDUCATION|CERTIFICATES|PROJECTS|SKILLS|LANGUAGE)", lines[i], re.IGNORECASE):
                    break
                description_lines.append(lines[i])
                i += 1

            experience_details.append({
                "Title": title,
                "Company": company,
                "Location": location,
                "Duration": duration,
                "Description": " ".join(description_lines)
            })
        else:
            i += 1
    return experience_details


def extract_certifications(text):
    certifications = []
    match = re.search(r"(CERTIFICATES|CERTIFICATIONS)(.*?)(EDUCATION|EXPERIENCE|PROJECTS|SKILLS|LANGUAGE|$)", text, re.IGNORECASE | re.DOTALL)
    if match:
        cert_text = match.group(2).strip()
        lines = cert_text.splitlines()

        for line in lines:
            line = re.sub(r"^[•\-\u2022\u2023\u25E6\u2043\u2219\uf0b7*]+", "", line).strip()
            if not line:
                continue
            line = re.sub(r"\s*\(?((Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*|\d{4}).*", "", line, flags=re.IGNORECASE).strip()

            if line:
                certifications.append(line)
    return certifications


def extract_projects(text):
    project_titles = []
    match = re.search(r"(PROJECTS)(.*?)(EXPERIENCE|EDUCATION|CERTIFICATES|SKILLS|TECHNICAL SKILLS|$)", text, re.IGNORECASE | re.DOTALL)
    
    if match:
        project_block = match.group(2).strip()
        lines = [line.strip("•–- \uf0b7") for line in project_block.splitlines() if line.strip()]
        
        for line in lines:
            # Check if line looks like a title
            if len(line) < 150 and not line.lower().startswith(("develop", "create", "built", "implemented", "worked")):
                project_titles.append(line)
    return project_titles



def extract_name(file_path):
    if file_path.lower().endswith(".pdf"):
        resume_text = extract_text_from_pdf(file_path)
    elif file_path.lower().endswith((".jpg", ".jpeg", ".png")):
        resume_text = extract_text_from_image(file_path)
    else:
        print("Error: Unsupported file format. Please provide a PDF or image file.")
        return None

    if resume_text is None:
        return None

    doc = nlp(resume_text)

    # Method 1: check first line
    lines = resume_text.splitlines()
    if lines:
        first_line = lines[0].strip()
        name_parts = first_line.split()
        if len(name_parts) >= 2:
            return " ".join(name_parts[:2])

    # Method 2: Using spaCy's Named Entity Recognition
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text

    # Method 3: Using a simple regex
    name_match = re.search(r"^[A-Z][a-z]+ [A-Z][a-z]+", resume_text)
    if name_match:
        return name_match.group(0)

    return None


from tkinter import Tk
from tkinter.filedialog import askopenfilename
def select_resume_file():
    Tk().withdraw()
    file_path = askopenfilename(
        title="Select your resume",
        filetypes=[("PDF files", "*.pdf"), ("Image files", "*.jpg *.jpeg")]
    )
    return file_path


if __name__ == "__main__":
    file_path = select_resume_file()

    text = extract_text_from_pdf(file_path) or extract_text_from_image(file_path)

    resume_data = {
        "name": extract_name(file_path) or "",
        "email": extract_email(text) or "",
        "phone": extract_phone_number(text) or "",
        "linkedin": extract_linkedin(text) or "",
        "skills": extract_skills(text),
        "education": extract_education(text) or [{"degree": "", "institution": "", "year": ""}],
        "experience": [],
        "certifications": extract_certifications(text),
        "projects": [{"title": title, "description": ""} for title in extract_projects(text)]
    }
    
    experiences = extract_experience(text)
    for exp in experiences:
        resume_data["experience"].append({
            "company": exp.get("Company", ""),
            "title": exp.get("Title", ""),
            "duration": exp.get("Duration", ""),
            "description": exp.get("Description", "")
        })

    if not resume_data["experience"]:
        resume_data["experience"].append({
            "company": "",
            "title": "",
            "duration": "",
            "description": ""
        })

    print(json.dumps(resume_data, indent=2))