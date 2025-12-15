import PyPDF2
import docx2txt
import re


def extract_text(file_path):
    if file_path.endswith(".pdf"):
        text = ""
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
        return text

    elif file_path.endswith(".docx"):
        return docx2txt.process(file_path)

    elif file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    return ""


def extract_sections(text):
    text = text.lower()

    sections = {
        "skills": "",
        "experience": "",
        "projects": ""
    }

    # Very forgiving patterns
    skills_pattern = r"(skills|technical skills)([\s\S]{0,1500})"
    experience_pattern = r"(work\s*experience|professional\s*experience|experience)([\s\S]{0,2000})"
    projects_pattern = r"(projects|academic projects)([\s\S]{0,2000})"

    skills_match = re.search(skills_pattern, text)
    experience_match = re.search(experience_pattern, text)
    projects_match = re.search(projects_pattern, text)

    if skills_match:
        sections["skills"] = skills_match.group(2)

    if experience_match:
        sections["experience"] = experience_match.group(2)

    if projects_match:
        sections["projects"] = projects_match.group(2)

    return sections

