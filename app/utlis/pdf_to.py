import PyPDF2

def extract_text_from_pdf(file_path):
    with open(file_path, "rb") as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        pages = [page.extract_text() or "" for page in reader.pages]
    # Concaténer toutes les pages avec un saut de ligne
    full_text = "\n".join(pages)
    return full_text

# Exemple d'utilisation
pdf_text = extract_text_from_pdf("/home/INT/idrissou.f/PycharmProjects/cvpro/app/utlis/CV_original .pdf")
print(pdf_text)
with open("/home/INT/idrissou.f/PycharmProjects/cvpro/app/utlis/CV_original.txt", "w") as text_file:
    text_file.write(pdf_text)