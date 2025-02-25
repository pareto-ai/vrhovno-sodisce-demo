import pymupdf
import textract


def pdf_to_text(file_path):
    # pymupdf, fall back to OCR if not sucessfull
    doc = pymupdf.open(file_path)

    pages = [page.get_text() for page in doc]
    text = " ".join([p for p in pages if p])

    if not pages:
        text = textract.process(file_path, extension="pdf", method="tesseract")

    return text
