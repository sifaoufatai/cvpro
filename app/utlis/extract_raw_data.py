import os
from PyPDF2 import PdfReader
from docx import Document


def pdf_to_txt(path: str) -> str:
    """
    Extracts text from a PDF file and returns it as a string.

    Args:
        path (str): Path to the PDF file.

    Returns:
        str: Extracted text from the PDF.
    """
    with open(path, "rb") as pdf_file:
        reader = PdfReader(pdf_file)
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages)


def extract_text_from_docx(filepath):
    """
    Extracts text from a DOCX file and returns it as a string.

    Args:
        filepath (str): Path to the DOCX file.

    Returns:
        str: Extracted text from the DOCX.
    """
    doc = Document(filepath)
    return "\n".join(p.text for p in doc.paragraphs)


def extract_text_from_txt(filepath):
    """
    Reads the content of a text file (.txt) and returns it as a string.

    Args:
        filepath (str): Path to the text file.

    Returns:
        str: Content of the text file.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def extract_text_from_file(filepath: str) -> str:
    """
    Extracts text from a file based on its extension (.pdf, .docx, .txt).

    Args:
        filepath (str): Path to the file to process.

    Returns:
        str: Extracted text from the file.

    Raises:
        ValueError: If the file format is not supported.
    """
    if filepath.endswith('.pdf'):
        return pdf_to_txt(filepath)
    elif filepath.endswith('.docx'):
        return extract_text_from_docx(filepath)
    elif filepath.endswith('.txt'):
        return extract_text_from_txt(filepath)
    else:
        raise ValueError("Unsupported file format. Please provide a .pdf, .docx, or .txt file.")