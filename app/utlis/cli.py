import json
from app.utlis.extract_resume_part import ResumeTemplate
from app.utlis.resume_to_pdf_zts_format import write_resume_to_pdf

def main():
    with open("parsed_resume.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    parsed_resume = ResumeTemplate.model_validate(data)
    write_resume_to_pdf(parsed_resume, "parsed_resume_ats.pdf")

if __name__ == "__main__":
    main()