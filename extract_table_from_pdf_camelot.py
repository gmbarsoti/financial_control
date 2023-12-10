import camelot
import os

pdf_path = os.path.join('.', 'source', 'table.pdf')
tables = camelot.read_pdf(pdf_path)
# number of tables extracted
print("Total tables extracted:", tables.n)
#pdf_text = extract_text(pdf_path, password='36234618812')'36234618812''36234618812'