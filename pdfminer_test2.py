from io import StringIO

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.utils import open_filename


def iter_text_per_page(pdf_file, password='', page_numbers=None, maxpages=0,
                 caching=True, codec='utf-8', laparams=None):
    if laparams is None:
        laparams = LAParams()

    with open_filename(pdf_file, "rb") as fp:
        rsrcmgr = PDFResourceManager(caching=caching)

        idx = 1
        for page in PDFPage.get_pages(
                fp,
                page_numbers,
                maxpages=maxpages,
                password=password,
                caching=caching,
        ):
            with StringIO() as output_string:
                device = TextConverter(rsrcmgr, output_string, codec=codec,
                                       laparams=laparams)
                interpreter = PDFPageInterpreter(rsrcmgr, device)
                interpreter.process_page(page)
                yield idx, output_string.getvalue()
                idx += 1


def main():
    pdf_file = 'source/Inter/Inter_statement_nov_dec_2024.pdf'
    #pdf_file = 'source/Meliuz/Meliuz_statement.pdf'
    for count, page_text in iter_text_per_page(pdf_file):
        print(f'page# {count}:\n{page_text}')
        print()


if __name__ == "__main__":
    main()