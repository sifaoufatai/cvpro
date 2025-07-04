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
    def __init__(self, width, height=0.25, color=colors.HexColor('#003366')):
        Flowable.__init__(self)
        self.width = width
        self.height = height
        self.color = color
    
    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(0.2)
        self.canv.line(0, 0, self.width, 0)

def load_resume_data(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def add_contact_info(flowables, contact):
    styles = getSampleStyleSheet()
    
    # Name
    name_style = ParagraphStyle(
        'NameStyle',
        parent=styles['Heading1'],
        fontSize=12,
        spaceAfter=2,
        alignment=1,
        leading=12
    )
    flowables.append(Paragraph(contact['name'].upper(), name_style))
    
    # Contact details
    contact_text = f"{contact['email']} | {contact['phone']} | {contact['linkedin']}"
    if 'location' in contact:
        contact_text += f" | {contact['location']}"
    
    contact_style = ParagraphStyle(
        'ContactStyle',
        parent=styles['Normal'],
        fontSize=7,
        spaceAfter=4,
        alignment=1,
        leading=8
    )
    flowables.append(Paragraph(contact_text, contact_style))
    flowables.append(Spacer(1, 2))
    flowables.append(HorizontalLine(550, 0.2))

def add_section_header(flowables, title):
    styles = getSampleStyleSheet()
    
    header_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=9,
        textColor=colors.HexColor('#003366'),
        spaceAfter=1,
        spaceBefore=2,
        leading=10
    )
    
    flowables.append(Paragraph(title.upper(), header_style))
    flowables.append(Spacer(1, 1))
    flowables.append(HorizontalLine(550, 0.1))
    flowables.append(Spacer(1, 1))

def add_summary(flowables, summary):
    if not summary:
        return
    
    add_section_header(flowables, 'Professional Summary')
    
    # Limiter la longueur du résumé
    if len(summary) > 250:
        summary = summary[:247] + '...'
    
    styles = getSampleStyleSheet()
    summary_style = ParagraphStyle(
        'Summary',
        parent=styles['Normal'],
        fontSize=8,
        spaceAfter=4,
        leading=9,
        firstLineIndent=0
    )
    
    flowables.append(Paragraph(summary, summary_style))

def add_skills(flowables, skills):
    if not skills:
        return
        
    add_section_header(flowables, 'Skills')
    
    # Diviser les compétences en 3 colonnes
    col1 = skills[::3]
    col2 = skills[1::3]
    col3 = skills[2::3]
    
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
    
    # Créer un tableau avec 3 colonnes
    table = Table(data, colWidths=[165, 165, 165])
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ('TOPPADDING', (0, 0), (-1, -1), 0,
    )]))
    
    flowables.append(table)
    flowables.append(Spacer(1, 2))

def add_experience(flowables, experience):
    if not experience:
        return
        
    add_section_header(flowables, 'Professional Experience')
    
    styles = getSampleStyleSheet()
    
    for exp in experience:
        # Titre du poste et entreprise
        title_style = ParagraphStyle(
            'JobTitle',
            parent=styles['Normal'],
            fontSize=8,
            spaceAfter=0,
            leading=9
        )
        
        title_text = f"<b>{exp['title']}</b>, {exp['company']} | {exp['location']}"
        flowables.append(Paragraph(title_text, title_style))
        
        # Dates
        date_style = ParagraphStyle(
            'Date',
            parent=styles['Italic'],
            fontSize=7,
            spaceAfter=2,
            leading=8
        )
        flowables.append(Paragraph(exp['dates'], date_style))
        
        # Réalisations (limitées à 3)
        achievements = exp.get('achievements', [])[:3]
        for achievement in achievements:
            achievement_style = ParagraphStyle(
                'Achievement',
                parent=styles['Normal'],
                fontSize=7,
                spaceAfter=1,
                leftIndent=8,
                bulletIndent=0,
                bulletFontName='Helvetica',
                bulletFontSize=7,
                bulletText='•',
                leading=8
            )
            flowables.append(Paragraph(achievement, achievement_style))
        
        flowables.append(Spacer(1, 2))

def add_education(flowables, education):
    if not education:
        return
        
    add_section_header(flowables, 'Education')
    
    styles = getSampleStyleSheet()
    
    for edu in education:
        # Diplôme et établissement
        degree_style = ParagraphStyle(
            'Degree',
            parent=styles['Normal'],
            fontSize=8,
            spaceAfter=0,
            leading=9
        )
        
        degree_text = f"<b>{edu['degree']}</b>, {edu['institution']}"
        flowables.append(Paragraph(degree_text, degree_style))
        
        # Année
        year_style = ParagraphStyle(
            'Year',
            parent=styles['Italic'],
            fontSize=7,
            spaceAfter=4,
            leading=8
        )
        flowables.append(Paragraph(str(edu['year']), year_style))

def add_projects(flowables, projects):
    if not projects:
        return
        
    add_section_header(flowables, 'Projects')
    
    styles = getSampleStyleSheet()
    
    for project in projects[:2]:  # Limiter à 2 projets
        # Nom du projet
        name_style = ParagraphStyle(
            'ProjectName',
            parent=styles['Normal'],
            fontSize=8,
            spaceAfter=0,
            leading=9
        )
        
        name_text = f"<b>{project['name']}</b>"
        if 'technologies' in project and project['technologies']:
            name_text += f" <i>({project['technologies']})</i>"
            
        flowables.append(Paragraph(name_text, name_style))
        
        # Description (limitée à 100 caractères)
        if 'description' in project and project['description']:
            desc = project['description']
            if len(desc) > 100:
                desc = desc[:97] + '...'
                
            desc_style = ParagraphStyle(
                'ProjectDesc',
                parent=styles['Normal'],
                fontSize=7,
                spaceAfter=4,
                leading=8,
                leftIndent=8
            )
            flowables.append(Paragraph(desc, desc_style))
        else:
            flowables.append(Spacer(1, 4))

def add_languages(flowables, languages):
    if not languages:
        return
        
    add_section_header(flowables, 'Languages')
    
    styles = getSampleStyleSheet()
    
    lang_text = " • ".join([f"{lang['language']} ({lang['level']})" for lang in languages])
    
    lang_style = ParagraphStyle(
        'Languages',
        parent=styles['Normal'],
        fontSize=8,
        spaceAfter=4,
        leading=9
    )
    
    flowables.append(Paragraph(lang_text, lang_style))

def generate_resume_pdf(resume_data, output_file):
    doc = SimpleDocTemplate(
        output_file,
        pagesize=letter,
        leftMargin=15,
        rightMargin=15,
        topMargin=12,
        bottomMargin=12
    )
    
    flowables = []
    
    # Ajouter les sections dans l'ordre souhaité
    add_contact_info(flowables, resume_data['contact_info'])
    
    if 'summary' in resume_data and resume_data['summary']:
        add_summary(flowables, resume_data['summary'])
    
    if 'skills' in resume_data and resume_data['skills']:
        add_skills(flowables, resume_data['skills'])
    
    if 'experience' in resume_data and resume_data['experience']:
        add_experience(flowables, resume_data['experience'])
    
    if 'education' in resume_data and resume_data['education']:
        add_education(flowables, resume_data['education'])
    
    if 'projects' in resume_data and resume_data['projects']:
        add_projects(flowables, resume_data['projects'])
    
    if 'languages' in resume_data and resume_data['languages']:
        add_languages(flowables, resume_data['languages'])
    
    # Générer le PDF
    doc.build(flowables)
    print(f"CV généré avec succès : {output_file}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_file = os.path.join(script_dir, 'resume_ats_optimized.json')
    pdf_file = os.path.join(script_dir, 'FATAI_IDRISSOU_Resume_Compact.pdf')
    
    try:
        resume_data = load_resume_data(json_file)
        generate_resume_pdf(resume_data, pdf_file)
    except Exception as e:
        print(f"Erreur lors de la génération du PDF : {e}")
