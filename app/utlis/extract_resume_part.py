import json
import os
from typing import List, Optional
from pydantic import BaseModel, Field
from openai import OpenAI
from dotenv import load_dotenv
import PyPDF2
load_dotenv()
class ContactInfo(BaseModel):
    """Basic contact details of the candidate."""
    name: str = Field(..., description="Full name of the candidate.")
    email: Optional[str] = Field(None, description="Email address.")
    phone: Optional[str] = Field(None, description="Phone number.")
    linkedin: Optional[str] = Field(None, description="LinkedIn profile URL.")


class Education(BaseModel):
    """Educational qualification details."""
    institution: str = Field(..., description="Name of the educational institution.")
    degree: str = Field(..., description="Degree obtained.")
    field_of_study: str = Field(..., description="Field of study.")
    graduation_year: Optional[int] = Field(None, description="Year of graduation.")


class LanguageProficiency(BaseModel):
    """
    Represents a candidate's language proficiency.
    """
    language: str = Field(..., description="Language name.")
    proficiency_level: Optional[str] = Field(None, description="Proficiency level (e.g., 'Beginner', 'Intermediate', 'Advanced').")


class SkillSection(BaseModel):
    """Core skills, tools, and languages."""
    core_skills: List[str] = Field(..., description="Key skills relevant to the candidate's field.")
    tools_and_technologies: Optional[List[str]] = Field(
        None, description="Tools, software, or technologies used.")
    languages: Optional[List[str]] = Field(
        None, description="Spoken or written languages.")


class WorkExperience(BaseModel):
    """Details of a professional employment period."""
    company: str = Field(..., description="Company name.")
    job_title: str = Field(..., description="Job title held.")
    start_date: str = Field(..., description="Start date (e.g. YYYY-MM).")
    end_date: Optional[str] = Field(None, description="End date (e.g. YYYY-MM or 'Present').")
    location: Optional[str] = Field(None, description="Location of the role.")
    achievements: List[str] = Field(..., description="Key achievements and responsibilities.")
    used_skills_and_tools: List[str] = Field(
        ..., description="Skills and tools used in this role.")


class VolunteerExperience(BaseModel):
    """Details of volunteer or community service."""
    organization: str = Field(..., description="Organization name.")
    role: str = Field(..., description="Role or title.")
    start_date: Optional[str] = Field(None, description="Start date.")
    end_date: Optional[str] = Field(None, description="End date.")
    responsibilities: Optional[List[str]] = Field(
        None, description="Duties performed.")


class Project(BaseModel):
    """Information about a personal or academic project."""
    project_name: str = Field(..., description="Project title.")
    description: Optional[str] = Field(None, description="Short description of the project.")
    technologies_used: Optional[List[str]] = Field(
        None, description="Technologies used in the project.")
    start_date: Optional[str] = Field(None, description="Project start date.")
    end_date: Optional[str] = Field(None, description="Project end date.")


class Publication(BaseModel):
    """Details of a published work."""
    title: str = Field(..., description="Title of the publication.")
    journal_or_source: Optional[str] = Field(
        None, description="Journal, website, or source.")
    publication_date: Optional[str] = Field(
        None, description="Publication date (e.g. YYYY-MM).")
    link: Optional[str] = Field(None, description="URL to the publication.")


class Award(BaseModel):
    """Recognition or honor received by the candidate."""
    title: str = Field(..., description="Title of the award or honor.")
    issuer: Optional[str] = Field(None, description="Organization that issued the award.")
    date: Optional[str] = Field(None, description="Date of the award.")
    description: Optional[str] = Field(None, description="Short context of the award.")


class Reference(BaseModel):
    """Professional reference contact details."""
    name: str = Field(..., description="Reference's full name.")
    relationship: str = Field(..., description="Relationship to the candidate.")
    email: Optional[str] = Field(None, description="Email address of the reference.")
    phone: Optional[str] = Field(None, description="Phone number of the reference.")


class Affiliation(BaseModel):
    """Professional or academic affiliations."""
    organization: str = Field(..., description="Organization name.")
    role: Optional[str] = Field(None, description="Role or title held.")
    membership_date: Optional[str] = Field(None, description="Affiliation start date.")


class HobbiesAndInterests(BaseModel):
    """
    Represents a candidate's hobbies and interests.
    """
    hobbies: List[str] = Field(..., description="List of hobbies and interests.")
    description: Optional[str] = Field(None, description="Brief description of the hobbies or interests.")



class ResumeTemplate(BaseModel):
    """Comprehensive structured representation of a candidate's resume."""
    contact_info: ContactInfo = Field(..., description="Candidate's contact information.")
    introduction: Optional[str] = Field(
        None, description="Optional introduction or headline.")
    professional_summary: str = Field(
        ..., description="Professional summary or career objective.")
    skills_section: SkillSection = Field(
        ..., description="Skills grouped by type, adaptable to any profession.")
    work_experience: List[WorkExperience] = Field(
        ..., description="List of professional work experiences.")
    volunteer_experience: Optional[List[VolunteerExperience]] = Field(
        default_factory=list, description="List of volunteer work.")
    projects: Optional[List[Project]] = Field(
        default_factory=list, description="List of personal or academic projects.")
    education: Optional[List[Education]] = Field(
        default_factory=list, description="Educational background.")
    publications: Optional[List[Publication]] = Field(
        default_factory=list, description="Published works.")
    awards: Optional[List[Award]] = Field(
        default_factory=list, description="Awards and honors received.")
    affiliations: Optional[List[Affiliation]] = Field(
        default_factory=list, description="Memberships or affiliations.")
    references: Optional[List[Reference]] = Field(
        default_factory=list, description="Professional references.")
    certifications: Optional[List[str]] = Field(
        default_factory=list, description="Certifications earned.")
    language_proficiency: Optional[List[LanguageProficiency]] = Field(
        default_factory=list, description="Languages and proficiency levels.")
    hobbies_and_interests: Optional[List[HobbiesAndInterests]] = Field(
        None, description="Candidate's hobbies and interests.")



def main():
    # Load API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY not set")

    client = OpenAI(api_key=api_key)

    # Load a raw resume text from a TXT file
    with open("CV_original.txt") as file:
        raw_resume = file.read()
    print(f"Extracted resume length: {len(raw_resume)} characters")

    # Generate JSON Schema for ResumeTemplate
    schema_dict = ResumeTemplate.model_json_schema(by_alias=False)
    schema_json = json.dumps(schema_dict, indent=2)
    with open("resume_template_schema.json", "w") as schema_file:
        schema_file.write(schema_json)

    # Construct prompts
    system_prompt = f"""
You are a resume parser. Convert the following resume into a JSON object matching this Pydantic schema.
Here is the schema definition for ResumeTemplate:
{schema_json}
Ensure that the output keys match the schema exactly and return valid JSON.
"""
    user_prompt = raw_resume

    # Call OpenAI using .parse instead of .create
    response = client.responses.parse(
        model="gpt-4.1",
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.0,

        text_format=ResumeTemplate,
    )


    parsed = response.output_parsed


    if not isinstance(parsed, ResumeTemplate):
        raise ValueError("La réponse n'est pas conforme au modèle ResumeTemplate")
    print("Parsed resume successfully:", parsed)
    # Save the parsed resume to a JSON file
    with open("parsed_resume.json", "w") as json_file:
        json.dump(parsed.model_dump(), json_file, indent=2)

if __name__ == "__main__":
    main()
