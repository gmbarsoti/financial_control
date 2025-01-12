from pdfminer.high_level import extract_text
import os
import time
import re
import yaml
import csv
import pandas as pd
import ast

months = ['Jan', 'Fev', 'Abr', 'Mai',
          'Jun', 'Jul', 'Ago', 'Set',
          'Out', 'Nov', 'Dez']


def create_yaml_file():
    article_info = [
        {
            'Ref_data': {
                'pdf_secret': ''
            }
        }
    ]
    yaml_path = os.path.join('.', 'source', 'financial.yaml')
    with open(yaml_path, 'w') as yaml_file:
        data = yaml.dump(article_info, yaml_file)
        print("Write successful")


def update_ref_yaml(data_to_update, value):
    yaml_path = os.path.join('.', 'source', 'financial.yaml')
    with open(yaml_path, "r") as yaml_file:
        data = yaml.load(yaml_file, Loader=yaml.FullLoader)
        data[0]['Ref_data'][data_to_update] = value
    with open(yaml_path, "w") as yaml_file:
        yaml.dump(data, yaml_file)


def get_from_ref_yaml(required_data):
    yaml_path = os.path.join('.', 'source', 'financial.yaml')
    with open(yaml_path, "r") as yaml_file:
        data = yaml.load(yaml_file, Loader=yaml.FullLoader)
    return data[0]['Ref_data'][required_data]


class Purchase:
    def __init__(self, date, description, card_info, value, tags=None):
        if tags is None:
            tags = []
        self.date = date
        self.description = description
        self.card_info = card_info
        self.value = value
        self.tags = tags


def get_text_from_pdf():
    pdf_path = os.path.join('.', 'source', 'Meliuz', 'Meliuz_statement.pdf')
    secret = get_from_ref_yaml('pdf_secret')
    pdf_text = extract_text(pdf_path, password=secret)
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
    uber_occurrences = 0
    for purchase in purchase_list(purchases_txt):
        if uber_pattern.match(purchase.description):
            uber_occurrences += 1
            sum_uber += float(purchase.value.replace(',', '.'))
    print("total uber({0}): R${1}".format(str(uber_occurrences), str(round(sum_uber, 2))))


def csv_creation(purchases_txt: str):
    db_path = os.path.join('.', 'source', 'data_base.csv')
    if not os.path.exists(db_path):
        with open(db_path, 'w', encoding='UTF-8') as db_f:
            purchases_writer = csv.writer(db_f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            purchases_writer.writerow(["card_info", "date", "description", "value", "tags"])
            for purchase in purchase_list(purchases_txt):
                purchases_writer.writerow([purchase.card_info, purchase.date, purchase.description,
                                           purchase.value, purchase.tags])
    else:
        print("db.csv already exists!")


def seller_total(purchases_txt: str, seller_name: str):
    uber_pattern = re.compile(seller_name, re.IGNORECASE)
    seller_sum = 0.0
    seller_occurrences = 0
    for purchase in purchase_list(purchases_txt):
        if uber_pattern.match(purchase.description):
            seller_occurrences += 1
            seller_sum += float(purchase.value.replace(',', '.'))
    print("total {2}({0}): R${1}".format(str(seller_occurrences), str(round(seller_sum, 2)), seller_name))


def load_data_from_csv():
    db_path = os.path.join('.', 'source', 'data_base.csv')
    purchase_csv_list = []
    if os.path.exists(db_path):
        with open(db_path, 'r', encoding='UTF-8') as db_f:
            csv_reader = csv.DictReader(db_f)
            for row in csv_reader:
                if row["tags"] == '[]':
                    purchase_csv_list.append(
                        Purchase(row["date"], row["description"], row["card_info"], row["value"], []))
                else:
                    purchase_csv_list.append(Purchase(row["date"], row["description"], row["card_info"], row["value"], ast.literal_eval(row["tags"])))
    return purchase_csv_list


def read_and_print_csv():
    db_path = os.path.join('.', 'source', 'data_base.csv')
    if os.path.exists(db_path):
        with open(db_path, 'r', encoding='UTF-8') as db_f:
            csv_reader = csv.DictReader(db_f)
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    print(f'Column names are {", ".join(row)}')
                    line_count += 1
                print(
                    f'\t{row["card_info"]} : {row["date"]} : {row["description"]} : {row["value"]} : {row["tags"]}.')
                line_count += 1
            print(f'Processed {line_count} lines.')


def add_uber_tag(purchase_obj_list: list):
    for purchase in purchase_obj_list:
        if 'uber' not in purchase.description.lower():
            pass
        elif 'uber' not in purchase.tags:
            purchase.tags.append('uber')


def add_ifood_tag(purchase_obj_list: list):
    for purchase in purchase_obj_list:
        if 'ifood' not in purchase.description.lower():
            pass
        elif 'ifood' not in purchase.tags:
            purchase.tags.append('ifood')
            purchase.tags.append('food')


def update_csv_file(purchase_obj_list: list):
    db_path = os.path.join('.', 'source', 'data_base.csv')
    with open(db_path, 'w', encoding='UTF-8') as db_f:
        purchases_writer = csv.writer(db_f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        purchases_writer.writerow(["card_info", "date", "description", "value", "tags"])
        for purchase in purchase_obj_list:
            purchases_writer.writerow([purchase.card_info, purchase.date, purchase.description,
                                       purchase.value, purchase.tags])

def total_by_tag(purchase_obj_list: list, tag: str):
    tag_occurrences = 0
    value_sum = 0
    for purchase in purchase_obj_list:
        if tag in purchase.tags:
            tag_occurrences += 1
            value_sum += float(purchase.value.replace(',', '.'))
    print("total tag - {2} - ({0}): R${1}".format(str(tag_occurrences), str(round(value_sum, 2)), tag))
    return value_sum


def total_without_tag(purchase_obj_list: list):
    tag_occurrences = 0
    value_sum = 0
    for purchase in purchase_obj_list:
        if not purchase.tags:
            tag_occurrences += 1
            value_sum += float(purchase.value.replace(',', '.'))
    print("total no tag ({0}): R${1}".format(str(tag_occurrences), str(round(value_sum, 2))))
    return value_sum


def purchases_without_tag(purchase_obj_list: list):
    ret_list = []
    for purchase in purchase_obj_list:
        if not purchase.tags:
            ret_list.append(purchase)
    return ret_list


def if_tag_add_tag(purchase_obj_list: list, ref_tag: str, new_add: str):
    for purchase in purchase_obj_list:
        if ref_tag.lower() not in purchase.tags:
            pass
        elif new_add.lower() not in purchase.tags:
            purchase.tags.append(new_add.lower())


if __name__ == '__main__':
    yaml_path = os.path.join('.', 'source', 'financial.yaml')
    if not os.path.exists(yaml_path):
        create_yaml_file()
    pdf_text = get_text_from_pdf()
    purchase_txt = purchases_block(pdf_text)
    csv_creation(purchase_txt)
    read_and_print_csv()
    purchase_obj_list = load_data_from_csv()
    add_uber_tag(purchase_obj_list)
    add_ifood_tag(purchase_obj_list)
    if_tag_add_tag(purchase_obj_list, 'uber', 'transport')

    update_csv_file(purchase_obj_list)

    total_uber(purchases_block(pdf_text))
    seller_total(purchase_txt, "ifood")
    sum = 0
    sum += total_by_tag(purchase_obj_list, 'food')
    sum += total_by_tag(purchase_obj_list, 'health')
    sum += total_by_tag(purchase_obj_list, 'supermarket')
    sum += total_by_tag(purchase_obj_list, 'transport')
    sum += total_by_tag(purchase_obj_list, 'housing')
    sum += total_by_tag(purchase_obj_list, 'entertainment')
    sum += total_without_tag(purchase_obj_list)
    print("Total statement: R${0}".format(str(sum.__round__(2))))
    for purchase in purchases_without_tag(purchase_obj_list):
        print(purchase.description)
    #text_file_from_statement(pdf_text)