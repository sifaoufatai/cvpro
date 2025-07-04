import os
from docx2pdf import convert

def convert_docx_to_pdf(docx_path, output_path=None):
    """
    Convert a Word document to PDF
    
    Args:
        docx_path (str): Path to the input Word document
        output_path (str, optional): Path for the output PDF. If None, uses same name as input with .pdf extension
    """
    if not os.path.exists(docx_path):
        raise FileNotFoundError(f"Word document not found: {docx_path}")
    
    if output_path is None:
        output_path = os.path.splitext(docx_path)[0] + '.pdf'
    
    # Convert the document
    convert(docx_path, output_path)
    print(f"Successfully converted to PDF: {output_path}")
    return output_path

if __name__ == "__main__":
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define input and output paths
    docx_file = os.path.join(script_dir, 'FATAI_IDRISSOU_Resume.docx')
    pdf_file = os.path.join(script_dir, 'FATAI_IDRISSOU_Resume.pdf')
    
    # Convert to PDF
    try:
        convert_docx_to_pdf(docx_file, pdf_file)
    except Exception as e:
        print(f"Error converting to PDF: {e}")
