from flask import Flask, render_template, request, make_response, session
import os
import pdfkit

from services.parser import extract_text, extract_sections
from services.preprocessing import clean_text
from services.matcher import analyze_resumes

app = Flask(__name__)
app.secret_key = "resume_secret_key"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

PDF_CONFIG = pdfkit.configuration(
    wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
)

@app.route("/download-report")
def download_report():
    html = render_template(
        "results.html",
        results=session.get("results", [])
    )

    options = {
        "enable-local-file-access": ""
    }

    pdf = pdfkit.from_string(
        html,
        False,
        configuration=PDF_CONFIG,
        options=options
    )

    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = "attachment; filename=resume_report.pdf"
    return response


@app.route("/", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        resumes = request.files.getlist("resumes")
        job_desc = request.form["job_desc"]

        resume_texts = []
        resume_names = []

        for file in resumes:
            path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(path)

            text = extract_text(path)
            cleaned_text = clean_text(text)

            
            sections = extract_sections(cleaned_text)

            print("---- DEBUG ----")
            print("EXPERIENCE TEXT:", sections["experience"][:300])
            print("--------------")


            # 🔥 FALLBACK FIX
            for key in ["skills", "experience", "projects"]:
                if not sections.get(key, "").strip():
                    sections[key] = cleaned_text

            resume_texts.append(sections)
            resume_names.append(file.filename)

        job_desc_clean = clean_text(job_desc)
        analysis_results = analyze_resumes(resume_texts, job_desc_clean)

        final_results = []
        for i, data in enumerate(analysis_results):
            final_results.append({
                "name": resume_names[i],
                "score": data["score"],
                "skills_score": data["skills_score"],
                "experience_score": data["experience_score"],
                "projects_score": data["projects_score"],
                "skill_coverage": data["skill_coverage"],
                "matched_skills": data["matched_skills"],
                "missing_skills": data["missing_skills"]
            })

        final_results = sorted(final_results, key=lambda x: x["score"], reverse=True)

        session["results"] = final_results
        return render_template("results.html", results=final_results)

    return render_template("upload.html")

if __name__ == "__main__":
    os.makedirs("uploads", exist_ok=True)
    app.run(debug=True)
