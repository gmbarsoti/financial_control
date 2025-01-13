import pdfminer_tests


def main():
    # pdf_file = 'source/Meliuz/Meliuz_statement.pdf'
    pdf_file = 'source/Inter/Inter_statement_nov_dec_2024.pdf'
    institution = 'Inter'
    statement_text = pdfminer_tests.get_text_from_pdf(pdf_file, institution)
    print(statement_text)


if __name__ == "__main__":
    main()