from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
import requests
import tempfile


def get_pdf_file(path):
    '''Downloads file if path is an HTTP address. Returns a file pointer.'''
    if path.startswith('http'):
        fp = tempfile.SpooledTemporaryFile()
        response = requests.get(path, stream=True)
        if response.ok:
            for block in response.iter_content(1024):
                if not block:
                    break
                fp.write(block)
        fp.seek(0)
        return fp
    return open(path)


def pdf_to_text(pdf_file):
    with tempfile.SpooledTemporaryFile() as pdf_out:
        resource_manager = PDFResourceManager()
        converter = TextConverter(resource_manager, pdf_out,
                                  codec='utf-8', laparams=LAParams())
        interpreter = PDFPageInterpreter(resource_manager, converter)
        for page in PDFPage.get_pages(pdf_file):
            interpreter.process_page(page)
        converter.close()
        pdf_out.seek(0)
        return pdf_out.read()
