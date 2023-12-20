from pdfminer.high_level import extract_text
import os
import time
import re

months = ['Jan', 'Fev', 'Abr', 'Mai',
          'Jun', 'Jul', 'Ago', 'Set',
          'Out', 'Nov', 'Dez']


class Purchase:

    def __init__(self, date, description, card_info, value):
        self.date = date
        self.description = description
        self.card_info = card_info
        self.value = value


def get_text_from_pdf():
    pdf_path = os.path.join('.', 'source', 'Meliuz', 'Meliuz_statement.pdf')
    pdf_text = extract_text(pdf_path, password='36234618812')
    #print(pdf_text)
    return pdf_text

def text_file_from_statement(statement_text):
    outputdir_path = os.path.join('.', 'output')
    timestr = time.strftime("%Y%m%d-%H%M%S")
    output_f_name = 'output_pdf_text-' + timestr + '.txt'
    output_txt_file_path = os.path.join(outputdir_path, output_f_name)
    with open(output_txt_file_path, 'w', encoding='UTF-8') as f_text_output:
        f_text_output.writelines(statement_text)


def purchase_list(purch_block: str):
    card_pattern1 = re.compile(r"cartão virtual •{4} [0-9]{4}", re.IGNORECASE)
    card_pattern2 = re.compile(r"cartão físico", re.IGNORECASE)
    date_pattern = re.compile(r"[0-9]{2} [A-Z][a-z]{2}")
    date, description, card_info, value, purch_list = [], [], [], [], []
    for line in purch_block.split('\n')[:-1]:
        if date_pattern.match(line):
            #not len(line.split(' ')) == 2: and (0 < int(line.split(' ')[0]) < 31) and (line.split(' ')[1] in months):
            date.append(line.split(' '))
        elif card_pattern1.match(line) or card_pattern2.match(line):
            card_info.append(line)
        elif ('R$' in line) and (u'\xa0' in line):
            value.append(line[3:])
        else:
            description.append(line)

    # Removing payment data
    payment_index = description.index('Pagamento')
    del description[payment_index]
    del value[payment_index]
    del date[payment_index]

    if len(value) != len(date) or len(date) != len(card_info) or len(card_info) != len(description):
        raise("Parsing purchases ERROR!")

    for i in range(len(date)):
        purch_list.append(Purchase(date[i], description[i], card_info[i], value[i]))

    return purch_list


def purchases_block(statement_text: str):
    start_ref_string = "Valor em R\\$"
    end_ref_string = "\f"
    additional_lines = 1
    start_ref_indexes = [m.start() for m in re.finditer(start_ref_string, statement_text)]
    start_ref_indexes = [m + len(start_ref_string) + 1 for m in start_ref_indexes] # removing string 'Valor em R$'
    end_ref_indexes = [m.start() for m in re.finditer(end_ref_string, statement_text)][1:-1]
    full_block = ''
    for i in range(len(start_ref_indexes)):
        full_block += statement_text[start_ref_indexes[i]:end_ref_indexes[i]]

    return full_block.replace('\n\n', '\n')

    # start_ref_index = statement_text.find(start_ref_string) + len(start_ref_string) + additional_lines
    # end_ref_index = statement_text[start_ref_index:].find(end_ref_string) + start_ref_index
    # purchases_first_block = statement_text[start_ref_index:end_ref_index].replace('\n\n', '\n')


def total_uber(purchases_txt: str):
    uber_pattern = re.compile(r"uber", re.IGNORECASE)
    sum_uber = 0.0
    uber_occurences = 0
    for purchase in purchase_list(purchases_txt):
        if uber_pattern.match(purchase.description):
            uber_occurences += 1
            sum_uber += float(purchase.value.replace(',', '.'))
    print("total uber({0}): R${1}".format(str(uber_occurences), str(round(sum_uber, 2))))

def seller_total(purchases_txt: str, seller_name: str):
    uber_pattern = re.compile(seller_name, re.IGNORECASE)
    seller_sum = 0.0
    seller_occurences = 0
    for purchase in purchase_list(purchases_txt):
        if uber_pattern.match(purchase.description):
            seller_occurences += 1
            seller_sum += float(purchase.value.replace(',', '.'))
    print("total {2}({0}): R${1}".format(str(seller_occurences), str(round(seller_sum, 2)), seller_name))


if __name__ == '__main__':
    pdf_text = get_text_from_pdf()
    purchase_txt = purchases_block(pdf_text)
    total_uber(purchases_block(pdf_text))
    seller_total(purchase_txt, "ifood")
    #text_file_from_statement(pdf_text)