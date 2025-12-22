import PyPDF2

# Open the PDF file
with open('statementSource/Meliuz/Meliuz_statement.pdf', 'rb') as file:
    reader = PyPDF2.PdfFileReader(file)
    number_of_pages = reader.numPages

    # Extract text from each page
    for page_number in range(number_of_pages):
        page = reader.getPage(page_number)
        text = page.extract_text()
        print(text)