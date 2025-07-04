import json
from fpdf import FPDF
import os

class ResumePDF(FPDF):
    def __init__(self):
        super().__init__()
        # Use built-in font that supports Unicode
        self.add_font('Arial', '', '', 'arial.ttf', uni=True)
        self.add_font('Arial', 'B', '', 'arialbd.ttf', uni=True)
        self.add_font('Arial', 'I', '', 'ariali.ttf', uni=True)
        self.set_auto_page_break(auto=True, margin=15)
        self.add_page()
        self.set_margins(20, 15, 20)
        
    def header(self):
        # Add header with name and contact info
        self.set_font('Arial', 'B', 20)
        self.cell(0, 10, self.title, 0, 1, 'C')
        self.set_font('Arial', '', 10)
        self.cell(0, 5, self.subtitle, 0, 1, 'C')
        self.ln(5)
        
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def add_section_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(230, 240, 255)
        self.cell(0, 10, title, 0, 1, 'L', 1)
        self.ln(5)
        
    def add_contact_info(self, contact):
        self.set_font('Arial', 'B', 20)
        self.cell(0, 10, contact['name'], 0, 1, 'C')
        
        self.set_font('DejaVu', '', 10)
        contact_line = f"{contact['email']} | {contact['phone']} | {contact['linkedin']}"
        if 'location' in contact:
            contact_line += f" | {contact['location']}"
        self.cell(0, 5, contact_line, 0, 1, 'C')
        self.ln(5)
        
    def add_summary(self, summary):
        self.set_font('DejaVu', '', 10)
        self.multi_cell(0, 5, summary)
        self.ln(5)
        
    def add_skills(self, skills):
        self.add_section_title('SKILLS')
        self.set_font('DejaVu', '', 10)
        col_width = 60
        x = self.get_x()
        y = self.get_y()
        
        for i, skill in enumerate(skills):
            if i > 0 and i % 3 == 0:
                self.ln(5)
                x = self.l_margin
                y = self.get_y() + 5
                
            self.set_xy(x, y + (i//3) * 5)
            self.cell(col_width, 5, f"• {skill}", 0, 0, 'L')
            
            if (i + 1) % 3 == 0:
                x = self.l_margin
            else:
                x += col_width
                
        self.ln(10 + (len(skills)//3) * 5)
        
    def add_experience(self, experience):
        self.add_section_title('EXPERIENCE')
        self.set_font('Arial', 'B', 11)
        self.cell(0, 5, experience['title'], 0, 1)
        
        self.set_font('Arial', 'B', 9)
        self.cell(0, 5, f"{experience['company']} | {experience['location']} | {experience['dates']}", 0, 1)
        
        self.set_font('DejaVu', '', 9)
        self.ln(2)
        
        for achievement in experience['achievements']:
            self.cell(5, 5, '•', 0, 0)
            self.multi_cell(0, 5, f" {achievement}")
        self.ln(3)
        
    def add_education(self, education):
        self.add_section_title('EDUCATION')
        for edu in education:
            self.set_font('DejaVu', 'B', 10)
            self.cell(0, 5, edu['degree'], 0, 1)
            
            self.set_font('DejaVu', '', 9)
            self.cell(0, 5, f"{edu['institution']} | {edu['year']}", 0, 1)
            self.ln(3)
            
    def add_projects(self, projects):
        self.add_section_title('PROJECTS')
        for project in projects:
            self.set_font('DejaVu', 'B', 10)
            self.cell(0, 5, project['name'], 0, 1)
            
            self.set_font('Arial', 'I', 9)
            self.cell(0, 5, project['technologies'], 0, 1)
            
            self.set_font('DejaVu', '', 9)
            self.multi_cell(0, 5, project['description'])
            self.ln(2)
            
    def add_languages(self, languages):
        self.add_section_title('LANGUAGES')
        self.set_font('DejaVu', '', 10)
        lang_str = " • ".join([f"{lang['language']} ({lang['level']})" for lang in languages])
        self.cell(0, 5, lang_str, 0, 1)

def generate_resume(json_file, output_file):
    # Load resume data
    with open(json_file, 'r', encoding='utf-8') as f:
        resume_data = json.load(f)
    
    # Create PDF
    pdf = ResumePDF()
    
    # Set document properties
    pdf.set_title(f"{resume_data['contact_info']['name']} - Resume")
    pdf.set_author(resume_data['contact_info']['name'])
    pdf.set_creator('Cascade AI Resume Generator')
    
    # Add content
    pdf.add_contact_info(resume_data['contact_info'])
    pdf.add_summary(resume_data['summary'])
    
    # Add skills in two columns
    mid_point = len(resume_data['skills']) // 2
    if len(resume_data['skills']) % 2 != 0:
        mid_point += 1
    
    skills_col1 = resume_data['skills'][:mid_point]
    skills_col2 = resume_data['skills'][mid_point:]
    
    pdf.add_section_title('SKILLS')
    pdf.set_font('Arial', '', 10)
    
    # Create two columns for skills
    col_width = 90
    x = pdf.l_margin
    y = pdf.get_y()
    
    # Left column
    for skill in skills_col1:
        pdf.set_xy(x, y)
        pdf.cell(5, 5, '•', 0, 0)
        pdf.cell(col_width, 5, skill, 0, 2)
        y += 5
    
    # Right column
    x += col_width + 10
    y = pdf.get_y() - (len(skills_col1) * 5)
    for skill in skills_col2:
        pdf.set_xy(x, y)
        pdf.cell(5, 5, '•', 0, 0)
        pdf.cell(col_width, 5, skill, 0, 2)
        y += 5
    
    pdf.ln(10)
    
    # Add experience
    for exp in resume_data['experience']:
        pdf.add_experience(exp)
        
    # Add education
    pdf.add_education(resume_data['education'])
    
    # Add projects
    pdf.add_projects(resume_data['projects'])
    
    # Add languages
    pdf.add_languages(resume_data['languages'])
    
    # Save PDF
    pdf.output(output_file)

if __name__ == "__main__":
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define input and output paths
    json_file = os.path.join(script_dir, 'resume_ats_optimized.json')
    output_file = os.path.join(script_dir, 'FATAI_IDRISSOU_Resume.pdf')
    
    # Generate the resume
    generate_resume(json_file, output_file)
    print(f"Resume generated successfully at: {output_file}")
