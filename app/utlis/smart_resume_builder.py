import os
import json
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Frame, KeepInFrame
from reportlab.platypus.flowables import Flowable
from reportlab.lib.units import mm, inch
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

class CVOptimizer:
    def __init__(self, resume_data):
        self.resume_data = resume_data
        self.optimization_level = 0
        self.max_optimization_level = 5
        self.styles = getSampleStyleSheet()
        self.doc = None
        self.flowables = []
        
        # Paramètres par défaut (niveau 0)
        self.params = {
            'font_sizes': {
                'name': 14,
                'contact': 8,
                'section': 10,
                'content': 9,
                'small': 7
            },
            'margins': {
                'left': 15 * mm,
                'right': 15 * mm,
                'top': 12 * mm,
                'bottom': 12 * mm
            },
            'spacing': {
                'section': 3 * mm,
                'item': 2 * mm,
                'line': 1 * mm
            },
            'limits': {
                'skills': 15,
                'achievements': 3,
                'projects': 2,
                'educations': 3,
                'experiences': 3
            }
        }
    
    def apply_optimization_level(self):
        """Applique le niveau d'optimisation actuel"""
        if self.optimization_level == 1:
            # Réduire légèrement les polices et les marges
            self.params['font_sizes'] = {k: v-1 for k, v in self.params['font_sizes'].items()}
            self.params['margins'] = {k: v-2*mm for k, v in self.params['margins'].items()}
            
        elif self.optimization_level == 2:
            # Réduire les espacements et les limites de contenu
            self.params['spacing'] = {k: v*0.7 for k, v in self.params['spacing'].items()}
            self.params['limits'] = {k: int(v*0.8) for k, v in self.params['limits'].items()}
            
        elif self.optimization_level == 3:
            # Réduire davantage les polices et les marges
            self.params['font_sizes'] = {k: max(6, v-1) for k, v in self.params['font_sizes'].items()}
            self.params['margins'] = {k: max(5*mm, v-2*mm) for k, v in self.params['margins'].items()}
            
        elif self.optimization_level == 4:
            # Limiter sévèrement le contenu
            self.params['limits'] = {k: max(1, int(v*0.6)) for k, v in self.params['limits'].items()}
            
        elif self.optimization_level == 5:
            # Dernier recours : réduire au minimum
            self.params['font_sizes'] = {k: 6 for k in self.params['font_sizes']}
            self.params['margins'] = {k: 5*mm for k in self.params['margins']}
            self.params['spacing'] = {k: 0.5*mm for k in self.params['spacing']}
    
    def build_document(self):
        """Construit le document avec les paramètres actuels"""
        self.flowables = []
        
        # Créer le document avec les marges actuelles
        self.doc = SimpleDocTemplate(
            self.output_file,
            pagesize=letter,
            leftMargin=self.params['margins']['left'],
            rightMargin=self.params['margins']['right'],
            topMargin=self.params['margins']['top'],
            bottomMargin=self.params['margins']['bottom']
        )
        
        # Ajouter le contenu
        self._add_contact_info()
        self._add_summary()
        self._add_skills()
        self._add_experience()
        self._add_education()
        self._add_projects()
        self._add_languages()
        
        # Construire le PDF
        self.doc.build(self.flowables)
        
        # Vérifier le nombre de pages
        from PyPDF2 import PdfReader
        reader = PdfReader(self.output_file)
        return len(reader.pages)
    
    def optimize_and_build(self, output_file):
        """Optimise et construit le CV jusqu'à ce qu'il tienne sur une page"""
        self.output_file = output_file
        
        while self.optimization_level <= self.max_optimization_level:
            self.apply_optimization_level()
            num_pages = self.build_document()
            
            if num_pages <= 1:
                print(f"CV optimisé avec succès (niveau {self.optimization_level})")
                return True
                
            print(f"Niveau d'optimisation {self.optimization_level} : {num_pages} pages")
            self.optimization_level += 1
        
        print("Impossible de faire tenir le CV sur une seule page avec les paramètres actuels")
        return False
    
    # Méthodes d'ajout de contenu...
    def _add_contact_info(self):
        contact = self.resume_data['contact_info']
        styles = self.styles
        
        # Style du nom
        name_style = ParagraphStyle(
            'NameStyle',
            parent=styles['Heading1'],
            fontSize=self.params['font_sizes']['name'] + 2,
            spaceAfter=2,
            alignment=1,
            leading=self.params['font_sizes']['name'] + 4
        )
        self.flowables.append(Paragraph(contact['name'].upper(), name_style))
        
        # Coordonnées
        contact_text = f"{contact['email']} | {contact['phone']} | {contact['linkedin']}"
        if 'location' in contact:
            contact_text += f" | {contact['location']}"
        
        contact_style = ParagraphStyle(
            'ContactStyle',
            parent=styles['Normal'],
            fontSize=self.params['font_sizes']['contact'],
            spaceAfter=self.params['spacing']['section'],
            alignment=1,
            leading=self.params['font_sizes']['contact'] + 1
        )
        self.flowables.append(Paragraph(contact_text, contact_style))
    
    def _add_section_header(self, title):
        style = ParagraphStyle(
            'SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=self.params['font_sizes']['section'],
            textColor=colors.HexColor('#003366'),
            spaceAfter=self.params['spacing']['line'],
            spaceBefore=self.params['spacing']['section'],
            leading=self.params['font_sizes']['section'] + 2
        )
        self.flowables.append(Paragraph(title.upper(), style))
    
    def _add_summary(self):
        if 'summary' not in self.resume_data or not self.resume_data['summary']:
            return
            
        self._add_section_header('Professional Summary')
        
        summary = self.resume_data['summary']
        # Réduire la longueur du résumé si nécessaire
        max_length = 300 - (self.optimization_level * 50)
        if len(summary) > max_length:
            summary = summary[:max_length-3] + '...'
        
        style = ParagraphStyle(
            'Summary',
            parent=self.styles['Normal'],
            fontSize=self.params['font_sizes']['content'],
            spaceAfter=self.params['spacing']['section'],
            leading=self.params['font_sizes']['content'] + 1
        )
        self.flowables.append(Paragraph(summary, style))
    
    def _add_skills(self):
        if 'skills' not in self.resume_data or not self.resume_data['skills']:
            return
            
        self._add_section_header('Skills')
        
        skills = self.resume_data['skills'][:self.params['limits']['skills']]
        
        # Créer un tableau à 3 colonnes pour les compétences
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
        
        # Créer le tableau
        table = Table(data, colWidths=[
            (self.doc.width / 3) - 6,
            (self.doc.width / 3) - 6,
            (self.doc.width / 3) - 6
        ])
        
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), self.params['font_sizes']['small']),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        self.flowables.append(table)
        self.flowables.append(Spacer(1, self.params['spacing']['section']))
    
    def _add_experience(self):
        if 'experience' not in self.resume_data or not self.resume_data['experience']:
            return
            
        self._add_section_header('Professional Experience')
        
        for exp in self.resume_data['experience'][:self.params['limits']['experiences']]:
            # Titre du poste et entreprise
            title_style = ParagraphStyle(
                'JobTitle',
                parent=self.styles['Normal'],
                fontSize=self.params['font_sizes']['content'],
                spaceAfter=0,
                leading=self.params['font_sizes']['content'] + 1
            )
            
            title_text = f"<b>{exp['title']}</b>, {exp['company']} | {exp['location']}"
            self.flowables.append(Paragraph(title_text, title_style))
            
            # Dates
            date_style = ParagraphStyle(
                'Date',
                parent=self.styles['Italic'],
                fontSize=self.params['font_sizes']['small'],
                spaceAfter=self.params['spacing']['line'],
                leading=self.params['font_sizes']['small'] + 1
            )
            self.flowables.append(Paragraph(exp['dates'], date_style))
            
            # Réalisations
            achievements = exp.get('achievements', [])[:self.params['limits']['achievements']]
            for achievement in achievements:
                achievement_style = ParagraphStyle(
                    'Achievement',
                    parent=self.styles['Normal'],
                    fontSize=self.params['font_sizes']['small'],
                    spaceAfter=1,
                    leftIndent=8,
                    bulletIndent=0,
                    bulletFontName='Helvetica',
                    bulletFontSize=self.params['font_sizes']['small'],
                    bulletText='•',
                    leading=self.params['font_sizes']['small'] + 1
                )
                # Réduire la longueur des réalisations si nécessaire
                max_len = 150 - (self.optimization_level * 20)
                ach_text = (achievement[:max_len-3] + '...') if len(achievement) > max_len else achievement
                self.flowables.append(Paragraph(ach_text, achievement_style))
            
            self.flowables.append(Spacer(1, self.params['spacing']['item']))
    
    def _add_education(self):
        if 'education' not in self.resume_data or not self.resume_data['education']:
            return
            
        self._add_section_header('Education')
        
        for edu in self.resume_data['education'][:self.params['limits']['educations']]:
            # Diplôme et établissement
            degree_style = ParagraphStyle(
                'Degree',
                parent=self.styles['Normal'],
                fontSize=self.params['font_sizes']['content'],
                spaceAfter=0,
                leading=self.params['font_sizes']['content'] + 1
            )
            
            degree_text = f"<b>{edu['degree']}</b>, {edu['institution']}"
            self.flowables.append(Paragraph(degree_text, degree_style))
            
            # Année
            year_style = ParagraphStyle(
                'Year',
                parent=self.styles['Italic'],
                fontSize=self.params['font_sizes']['small'],
                spaceAfter=self.params['spacing']['item'],
                leading=self.params['font_sizes']['small'] + 1
            )
            self.flowables.append(Paragraph(str(edu['year']), year_style))
    
    def _add_projects(self):
        if 'projects' not in self.resume_data or not self.resume_data['projects']:
            return
            
        self._add_section_header('Projects')
        
        for project in self.resume_data['projects'][:self.params['limits']['projects']]:
            # Nom du projet
            name_style = ParagraphStyle(
                'ProjectName',
                parent=self.styles['Normal'],
                fontSize=self.params['font_sizes']['content'],
                spaceAfter=0,
                leading=self.params['font_sizes']['content'] + 1
            )
            
            name_text = f"<b>{project['name']}</b>"
            if 'technologies' in project and project['technologies']:
                name_text += f" <i>({project['technologies']})</i>"
                
            self.flowables.append(Paragraph(name_text, name_style))
            
            # Description
            if 'description' in project and project['description']:
                desc_style = ParagraphStyle(
                    'ProjectDesc',
                    parent=self.styles['Normal'],
                    fontSize=self.params['font_sizes']['small'],
                    spaceAfter=self.params['spacing']['item'],
                    leading=self.params['font_sizes']['small'] + 1,
                    leftIndent=8
                )
                # Réduire la description si nécessaire
                max_len = 100 - (self.optimization_level * 15)
                desc = project['description']
                desc = (desc[:max_len-3] + '...') if len(desc) > max_len else desc
                self.flowables.append(Paragraph(desc, desc_style))
            else:
                self.flowables.append(Spacer(1, self.params['spacing']['item']))
    
    def _add_languages(self):
        if 'languages' not in self.resume_data or not self.resume_data['languages']:
            return
            
        self._add_section_header('Languages')
        
        lang_text = " • ".join([f"{lang['language']} ({lang['level']})" for lang in self.resume_data['languages']])
        
        lang_style = ParagraphStyle(
            'Languages',
            parent=self.styles['Normal'],
            fontSize=self.params['font_sizes']['content'],
            spaceAfter=0,
            leading=self.params['font_sizes']['content'] + 1
        )
        
        self.flowables.append(Paragraph(lang_text, lang_style))

def generate_smart_resume(json_file, output_file):
    """Fonction principale pour générer un CV intelligent"""
    # Charger les données du CV
    with open(json_file, 'r', encoding='utf-8') as f:
        resume_data = json.load(f)
    
    # Créer et exécuter l'optimiseur
    optimizer = CVOptimizer(resume_data)
    success = optimizer.optimize_and_build(output_file)
    
    if success:
        print(f"CV généré avec succès : {output_file}")
    else:
        print(f"Le CV n'a pas pu être optimisé sur une seule page. Fichier généré : {output_file}")

if __name__ == "__main__":
    # Exemple d'utilisation
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_file = os.path.join(script_dir, 'resume_ats_optimized.json')
    pdf_file = os.path.join(script_dir, 'FATAI_IDRISSOU_Resume_Smart.pdf')
    
    generate_smart_resume(json_file, pdf_file)
