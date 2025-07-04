import os
import json
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Flowable
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

class HorizontalLine(Flowable):
    def __init__(self, width, height=1, color=colors.HexColor('#003366')):
        Flowable.__init__(self)
        self.width = width
        self.height = height
        self.color = color
    
    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(0.5)
        self.canv.line(0, 0, self.width, 0)

def load_resume_data(json_file):
    """Load resume data from JSON file"""
    with open(json_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def add_contact_info(flowables, contact):
    """Add contact information to the PDF"""
    styles = getSampleStyleSheet()
    
    # Name
    name_style = ParagraphStyle(
        'NameStyle',
        parent=styles['Heading1'],
        fontSize=14,  # Taille réduite
        spaceAfter=2, # Espacement réduit au minimum
        alignment=1,  # Center aligned
        leading=14    # Interligne réduit
    )
    flowables.append(Paragraph(contact['name'].upper(), name_style))
    
    # Contact details
    contact_text = f"{contact['email']} | {contact['phone']} | {contact['linkedin']}"
    if 'location' in contact:
        contact_text += f" | {contact['location']}"
    
    contact_style = ParagraphStyle(
        'ContactStyle',
        parent=styles['Normal'],
        fontSize=5,    # Taille très réduite
        spaceAfter=3,  # Espacement minimal
        alignment=1,   # Center aligned
        leading=5      # Interligne réduit
    )
    flowables.append(Paragraph(contact_text, contact_style))
    
    # Ligne très fine avec espace minimal
    flowables.append(Spacer(1, 2))
    flowables.append(HorizontalLine(550, 0.25))  # Ligne très fine et plus large

def add_section_header(flowables, title):
    """Add a section header"""
    styles = getSampleStyleSheet()
    
    header_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=9,  # Taille réduite
        textColor=colors.HexColor('#003366'),
        spaceAfter=2,  # Espacement minimal
        spaceBefore=4,  # Espacement minimal
        leading=8     # Interligne réduit
    )
    
    flowables.append(Paragraph(title.upper(), header_style))
    
    # Ligne très fine avec espace minimal
    flowables.append(Spacer(1, 1))
    flowables.append(HorizontalLine(550, 0.25))  # Ligne très fine et plus large
    flowables.append(Spacer(1, 1))

def add_summary(flowables, summary):
    """Add professional summary"""
    styles = getSampleStyleSheet()
    
    add_section_header(flowables, 'Professional Summary')
    
    summary_style = ParagraphStyle(
        'Summary',
        parent=styles['Normal'],
        fontSize=8,      # Taille réduite
        spaceAfter=6,    # Espacement réduit
        leading=10,      # Interligne réduit
        firstLineIndent=0
    )
    
    flowables.append(Paragraph(summary, summary_style))

def add_skills(flowables, skills):
    """Add skills section with two columns"""
    add_section_header(flowables, 'Skills')
    
    # Split skills into two columns
    mid = (len(skills) + 1) // 2
    col1 = skills[:mid]
    col2 = skills[mid:]
    
    # Create a table with three columns for more compact layout
    third = (len(skills) + 2) // 3  # Divise en 3 colonnes
    col1 = skills[:third]
    col2 = skills[third:2*third]
    col3 = skills[2*third:]
    
    data = []
    max_rows = max(len(col1), len(col2), len(col3))
    
    for i in range(max_rows):
        row = []
        for col in [col1, col2, col3]:
            if i < len(col):
                row.append(f"• {col[i]}")
            else:
                row.append("")
        data.append(row)
    
    # Create table with 3 columns
    table = Table(data, colWidths=[165, 165, 165])  # 3 colonnes égales
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
    ]))
    
    flowables.append(table)
    flowables.append(Spacer(1, 12))

def add_experience(flowables, experience):
    """Add work experience section"""
    add_section_header(flowables, 'Professional Experience')
    
    styles = getSampleStyleSheet()
    
    for exp in experience:
        # Job title and company
        title_style = ParagraphStyle(
            'JobTitle',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=0,
            leading=14
        )
        
        title_text = f"<b>{exp['title']}</b>, {exp['company']} | {exp['location']}"
        flowables.append(Paragraph(title_text, title_style))
        
        # Dates
        date_style = ParagraphStyle(
            'Date',
            parent=styles['Italic'],
            fontSize=9,
            spaceAfter=6,
            leading=12
        )
        flowables.append(Paragraph(exp['dates'], date_style))
        
        # Achievements
        for achievement in exp['achievements']:
            achievement_style = ParagraphStyle(
                'Achievement',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=4,
                leftIndent=10,
                bulletIndent=0,
                bulletFontName='Helvetica',
                bulletFontSize=10,
                bulletText='•'
            )
            flowables.append(Paragraph(achievement, achievement_style))
        
        flowables.append(Spacer(1, 6))

def add_education(flowables, education):
    """Add education section"""
    add_section_header(flowables, 'Education')
    
    styles = getSampleStyleSheet()
    
    for edu in education:
        # Degree and institution
        degree_style = ParagraphStyle(
            'Degree',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=0,
            leading=14
        )
        
        degree_text = f"<b>{edu['degree']}</b>, {edu['institution']}"
        flowables.append(Paragraph(degree_text, degree_style))
        
        # Year
        year_style = ParagraphStyle(
            'Year',
            parent=styles['Italic'],
            fontSize=9,
            spaceAfter=12,
            leading=12
        )
        flowables.append(Paragraph(str(edu['year']), year_style))

def add_projects(flowables, projects):
    """Add projects section"""
    if not projects:
        return
        
    add_section_header(flowables, 'Projects')
    
    styles = getSampleStyleSheet()
    
    for project in projects:
        # Project name
        name_style = ParagraphStyle(
            'ProjectName',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=0,
            leading=14
        )
        
        name_text = f"<b>{project['name']}</b>"
        if 'technologies' in project and project['technologies']:
            name_text += f" <i>({project['technologies']})</i>"
            
        flowables.append(Paragraph(name_text, name_style))
        
        # Description
        if 'description' in project and project['description']:
            desc_style = ParagraphStyle(
                'ProjectDesc',
                parent=styles['Normal'],
                fontSize=9,
                spaceAfter=12,
                leading=12,
                leftIndent=10
            )
            flowables.append(Paragraph(project['description'], desc_style))
        else:
            flowables.append(Spacer(1, 12))

def add_languages(flowables, languages):
    """Add languages section"""
    if not languages:
        return
        
    add_section_header(flowables, 'Languages')
    
    styles = getSampleStyleSheet()
    
    lang_text = " • ".join([f"{lang['language']} ({lang['level']})" for lang in languages])
    
    lang_style = ParagraphStyle(
        'Languages',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=12,
        leading=14
    )
    
    flowables.append(Paragraph(lang_text, lang_style))

def generate_resume_pdf(resume_data, output_file):
    """Generate a PDF resume from resume data"""
    doc = SimpleDocTemplate(
        output_file,
        pagesize=letter,
        leftMargin=25,      # Marge très réduite
        rightMargin=25,     # Marge très réduite
        topMargin=20,       # Marge supérieure minimale
        bottomMargin=20      # Marge inférieure minimale
    )
    
    # Create a list to hold all flowable elements
    flowables = []
    
    # Add content to the PDF with compact formatting
    add_contact_info(flowables, resume_data['contact_info'])
    
    # Réduire l'espace après le titre
    if len(flowables) > 0:
        flowables.append(Spacer(1, 6))  # Réduit l'espace après le titre
    
    if 'summary' in resume_data and resume_data['summary']:
        # Raccourcir le résumé si nécessaire
        summary = resume_data['summary']
        if len(summary) > 300:  # Limiter la longueur du résumé
            summary = summary[:297] + '...'
        add_summary(flowables, summary)
    
    if 'skills' in resume_data and resume_data['skills']:
        # Limiter le nombre de compétences affichées
        skills = resume_data['skills'][:12]  # Maximum 12 compétences
        add_skills(flowables, skills)
    
    if 'experience' in resume_data and resume_data['experience']:
        # Limiter le nombre d'expériences et de réalisations
        experiences = resume_data['experience']
        for exp in experiences:
            if 'achievements' in exp and len(exp['achievements']) > 3:
                exp['achievements'] = exp['achievements'][:3]  # Maximum 3 réalisations par expérience
        add_experience(flowables, experiences)
    
    if 'education' in resume_data and resume_data['education']:
        add_education(flowables, resume_data['education'])
    
    if 'projects' in resume_data and resume_data['projects']:
        # Limiter le nombre de projets
        projects = resume_data['projects'][:2]  # Maximum 2 projets
        for proj in projects:
            if 'description' in proj and len(proj['description']) > 150:
                proj['description'] = proj['description'][:147] + '...'  # Limiter la description
        add_projects(flowables, projects)
    
    if 'languages' in resume_data and resume_data['languages']:
        add_languages(flowables, resume_data['languages'])
    
    # Build the PDF
    doc.build(flowables)
    print(f"PDF resume generated successfully at: {output_file}")

if __name__ == "__main__":
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define input and output paths
    json_file = os.path.join(script_dir, 'resume_ats_optimized.json')
    pdf_file = os.path.join(script_dir, 'FATAI_IDRISSOU_Resume.pdf')
    
    # Load resume data and generate PDF
    try:
        resume_data = load_resume_data(json_file)
        generate_resume_pdf(resume_data, pdf_file)
    except Exception as e:
        print(f"Error generating PDF: {e}")
