from pdfminer.high_level import extract_text
import os
import time
import re
import yaml
import csv
import pandas as pd
import ast
import database
from datetime import datetime

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
    yaml_path = os.path.join('.', 'statementSource', 'financial.yaml')
    with open(yaml_path, 'w') as yaml_file:
        data = yaml.dump(article_info, yaml_file)
        print("Write successful")


def update_ref_yaml(data_to_update, value):
    yaml_path = os.path.join('.', 'statementSource', 'financial.yaml')
    with open(yaml_path, "r") as yaml_file:
        data = yaml.load(yaml_file, Loader=yaml.FullLoader)
        data[0]['Ref_data'][data_to_update] = value
    with open(yaml_path, "w") as yaml_file:
        yaml.dump(data, yaml_file)


def get_from_ref_yaml(required_data: str, institution: str):
    yaml_path = os.path.join('.', 'statementSource', 'financial.yaml')
    with open(yaml_path, "r") as yaml_file:
        data = yaml.load(yaml_file, Loader=yaml.FullLoader)
    match institution.lower():
        case "inter":
            return data[0]['Ref_data'][required_data][:6]
        case "meliuz":
            return data[0]['Ref_data'][required_data]
    return data[0]['Ref_data'][required_data]


class CreditCardStatement:
    def __init__(self, issuer, payment_date, total_value, statement_text):
        self.issuer = issuer
        self.payment_date = payment_date
        self.total_value = total_value
        self.statement_text = statement_text

    def purchases_block(self):
        full_block = ''
        match institution.lower():
            case "meliuz":
                start_ref_string = "Valor em R\\$"
                end_ref_string = "\f"
                start_ref_indexes = [m.start() for m in re.finditer(start_ref_string, self.statement_text)]
                start_ref_indexes = [m + len(start_ref_string) + 1 for m in
                                     start_ref_indexes]  # removing start_ref_string
                end_ref_indexes = [m.start() for m in re.finditer(end_ref_string, self.statement_text)][2:]
                for i in range(len(start_ref_indexes)):
                    full_block += self.statement_text[start_ref_indexes[i]:end_ref_indexes[i]]
            case "inter":
                start_ref_string = "Beneficiário"
                end_ref_string = "\f"
                start_ref_indexes = [m.start() for m in re.finditer(start_ref_string, self.statement_text)]
                start_ref_indexes = [m + len(start_ref_string) + 1 for m in
                                     start_ref_indexes]  # removing start_ref_string
                initial_pages_to_skip = 2
                last_pages_to_skip = -3
                end_ref_indexes = [m.start() for m in re.finditer(end_ref_string, self.statement_text)][
                                  initial_pages_to_skip:last_pages_to_skip]
                for i in range(len(start_ref_indexes)):
                    full_block += self.statement_text[start_ref_indexes[i]:end_ref_indexes[i]]

        return full_block.replace('\n\n', '\n')

    def purchase_list(self):
        match institution.lower():
            case "meliuz":
                card_pattern1 = re.compile(r"5458 •{4} [0-9]{4}", re.IGNORECASE)
                card_pattern2 = re.compile(r"7605", re.IGNORECASE)
                date_pattern = re.compile(r"[0-9]{2} [A-Z][a-z]{2}")
                date, description, card_info, value, purchase_list = [], [], [], [], []
                for line in self.purchases_block().split('\n')[:-1]:
                    if date_pattern.match(line):
                        if is_date_and_description_in_one_line(line):
                            description.append(line.split(' ')[3])
                        converted_date = self.convert_date_day_month_name_to_suitable_pattern(line)
                        date.append(converted_date)
                    # elif card_pattern1.match(line) or card_pattern2.match(line):
                    elif ('•••• 5458' in line) or ('•••• 7605' in line):
                        card_info.append(line)
                    # elif ('R$' in line) and (u'\xa0' in line):
                    elif ('R$' in line):
                        if (not '+' in line):
                            value.append(line[3:])
                    elif (not 'Pagamento efetuado' in line):
                        description.append(line)
                    elif ('Pagamento efetuado' in line):
                        del date[-1]

                # Removing payment data
                # if description:
                #     payment_index = description.index('Pagamento')
                #     del description[payment_index]
                #     del value[payment_index]
                #     del date[payment_index]

                if len(value) != len(date) or len(date) != len(card_info) or len(card_info) != len(description):
                    raise ("Parsing purchases ERROR!")

                for i in range(len(date)):
                    purchase_list.append(Purchase(date[i], description[i], card_info[i], value[i]))
            case "inter":
                date_pattern = re.compile(r"[0-9]{2} de [a-z]{3}\. [0-9]{4}")  # example: 21 de nov. 2024
                dates, descriptions, recipients, values, purchase_list = [], [], [], [], []
                next_line_is_description = False
                getting_dates_and_descriptions = False
                for line in self.purchases_block().split('\n')[:-1]:
                    if getting_values_for_purchase(line, getting_dates_and_descriptions, values, dates):
                        values.append(line.replace('R$ ', ''))
                    elif next_line_is_description:
                        line = line.replace('\x00', '')  # removing nul character
                        descriptions.append(line)
                        next_line_is_description = False
                    elif date_pattern.match(line):
                        getting_dates_and_descriptions = True
                        next_line_is_description = True
                        dates.append(line)
                    elif line == '-':
                        getting_dates_and_descriptions = False

                # Removing payment data
                statement_payment_pattern = r'^\+'
                payment_index = find_index_by_regex(statement_payment_pattern, values)
                del descriptions[payment_index]
                del values[payment_index]
                del dates[payment_index]

                if len(values) != len(dates) or len(dates) != len(descriptions):
                    raise ("Parsing purchases ERROR!")

                for i in range(len(dates)):
                    purchase_list.append(Purchase(dates[i], descriptions[i], '', values[i]))

        return purchase_list

    def get_operation_year(self, operation_month_number):
        payment_date_month = self.payment_date.month
        january_month = 1
        december_month = 12
        if payment_date_month == january_month and operation_month_number == december_month:
            the_year_before = str(int(self.payment_date.year) - 1)
            return the_year_before
        else:
            return str(self.payment_date.year)

    def convert_date_day_month_name_to_suitable_pattern(self, date_to_convert):
        day_and_month_name = date_to_convert[:-1].split(' ')
        day = day_and_month_name[0]
        month_name = day_and_month_name[1]
        month_number = convert_month_prefix_to_number(month_name)
        year = self.get_operation_year(month_number)
        return day + '-' + str(month_number) + '-' + year


class Purchase:
    def __init__(self, date, description, card_info, value, tags=None):
        if tags is None:
            tags = []
        self.date = date
        self.description = description
        self.card_info = card_info
        self.value = value
        self.tags = tags


def get_statement_payment_date(statement_text, institution_name):
    match institution_name.lower():
        case "meliuz":
            start_ref_string = "Dia de vencimento"
            end_ref_string = "Limite de crédito total"
            start_pos = statement_text.find(start_ref_string)
            end_pos = statement_text.find(end_ref_string)
            if start_pos != -1 and end_pos != -1:
                payment_date = statement_text[start_pos + len(start_ref_string): end_pos]
            payment_date = payment_date.replace('\n', '')
            return datetime.strptime(payment_date, "%d/%m/%Y")


def get_statement_value_to_pay(statement_text, institution_name):
    match institution_name.lower():
        case "meliuz":
            start_ref_string = "fechou no valor total de:"
            end_ref_string = "Escolha como deseja pagar:"
            start_pos = statement_text.find(start_ref_string)
            end_pos = statement_text.find(end_ref_string)
            if start_pos != -1 and end_pos != -1:
                value_to_pay = statement_text[start_pos + len(start_ref_string): end_pos]
                value_to_pay = value_to_pay.replace('\n', '')
                return value_to_pay


def get_text_from_pdf(pdf_path, institution):
    secret = get_from_ref_yaml('pdf_secret', institution)
    pdf_text = extract_text(pdf_path, password=secret)
    return pdf_text


def text_file_from_statement(statement_text):
    outputdir_path = os.path.join('.', 'output')
    timestr = time.strftime("%Y%m%d-%H%M%S")
    output_f_name = 'output_pdf_text-' + timestr + '.txt'
    output_txt_file_path = os.path.join(outputdir_path, output_f_name)
    with open(output_txt_file_path, 'w', encoding='UTF-8') as f_text_output:
        f_text_output.writelines(statement_text)


def is_date_and_description_in_one_line(line_to_check):
    if len(line_to_check) > 7:
        return True


def convert_month_prefix_to_number(month_prefix):
    match month_prefix.lower():
        case "jan":
            return 1
        case "fev":
            return 2
        case "mar":
            return 3
        case "abr":
            return 4
        case "mai":
            return 5
        case "jun":
            return 6
        case "jul":
            return 7
        case "ago":
            return 8
        case "set":
            return 9
        case "out":
            return 10
        case "nov":
            return 11
        case "dez":
            return 12


def getting_values_for_purchase(line, getting_dates_and_descriptions, values, dates):
    if 'R$' not in line:
        return False
    if getting_dates_and_descriptions:
        return False
    if len(values) < len(dates):
        return True


def find_index_by_regex(pattern, lst):
    regex = re.compile(pattern)
    for index, element in enumerate(lst):
        if regex.search(element):  # Check for a match
            return index
    return None  # Return None if no match is found




    # start_ref_index = statement_text.find(start_ref_string) + len(start_ref_string) + additional_lines
    # end_ref_index = statement_text[start_ref_index:].find(end_ref_string) + start_ref_index
    # purchases_first_block = statement_text[start_ref_index:end_ref_index].replace('\n\n', '\n')


def total_uber(purchases):
    uber_pattern = re.compile(r"uber", re.IGNORECASE)
    sum_uber = 0.0
    uber_occurrences = 0
    for purchase in purchases:
        if uber_pattern.match(purchase.description):
            uber_occurrences += 1
            sum_uber += float(purchase.value.replace(',', '.'))
    print("total uber({0}): R${1}".format(str(uber_occurrences), str(round(sum_uber, 2))))


def csv_creation(purchases_to_add):
    db_path = os.path.join('.', 'statementSource', 'data_base.csv')
    with open(db_path, 'w', encoding='UTF-8') as db_f:
        purchases_writer = csv.writer(db_f, delimiter=',', quotechar='"', escapechar='\\', quoting=csv.QUOTE_MINIMAL)
        purchases_writer.writerow(["card_info", "date", "description", "value", "tags"])
        for purchase in purchases_to_add:
            purchases_writer.writerow([purchase.card_info, purchase.date, purchase.description,
                                       purchase.value, purchase.tags])


def seller_total(purchases: list, seller_name: str):
    uber_pattern = re.compile(seller_name.lower(), re.IGNORECASE)
    seller_sum = 0.0
    seller_occurrences = 0
    for purchase in purchases:
        if uber_pattern.match(purchase.description.lower()):
            seller_occurrences += 1
            seller_sum += float(purchase.value.replace(',', '.'))
    print("total {2}({0}): R${1}".format(str(seller_occurrences), str(round(seller_sum, 2)), seller_name))


def load_data_from_csv():
    db_path = os.path.join('.', 'statementSource', 'data_base.csv')
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
    db_path = os.path.join('.', 'statementSource', 'data_base.csv')
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
        if not (('ifood' in purchase.description.lower()) or ('ifd*' in purchase.description.lower())):
            pass
        elif 'ifood' not in purchase.tags:
            purchase.tags.append('ifood')
            purchase.tags.append('food')


def update_csv_file(purchase_obj_list: list):
    db_path = os.path.join('.', 'statementSource', 'data_base.csv')
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
            value = purchase.value.replace(',', '.')
            value_sum += float(value.replace('R$ ', ''))
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


def add_tag_based_on_description(purchase_obj_list: list, description, tag_to_add):
    for purchase in purchase_obj_list:
        if description.lower() not in purchase.description.lower():
            pass
        elif tag_to_add.lower() not in purchase.tags:
            purchase.tags.append(tag_to_add.lower())


if __name__ == '__main__':
    yaml_path = os.path.join('.', 'statementSource', 'financial.yaml')
    if not os.path.exists(yaml_path):
        create_yaml_file()
    institution = 'Meliuz'
    # institution = 'Inter'

    for i in [1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12]:
        month = str(i) if len(str(i)) > 1 else ''.join(['0', str(i)])
        pdf_file = f'statementSource/{institution}/2025/2025-{month}.pdf'
        # pdf_file = 'statementSource/Inter/inter_statement_nov_dec_2024.pdf'
        pdf_text = get_text_from_pdf(pdf_file, institution)
        statement_payment_date = get_statement_payment_date(pdf_text, institution)
        statement_value_to_pay = get_statement_value_to_pay(pdf_text, institution)
        statement_object = CreditCardStatement(institution, statement_payment_date, statement_value_to_pay, pdf_text)
        purchases_txt = statement_object.purchases_block()
        purchases_list = statement_object.purchase_list()
        database.add_credit_card_operation_to_database(purchases_list)


    pdf_file = 'statementSource/Meliuz/2025/2025-01.pdf'
    # pdf_file = 'statementSource/Inter/inter_statement_nov_dec_2024.pdf'
    pdf_text = get_text_from_pdf(pdf_file, institution)
    statement_payment_date = get_statement_payment_date(pdf_text, institution)
    statement_value_to_pay = get_statement_value_to_pay(pdf_text, institution)
    statement_object = CreditCardStatement(institution, statement_payment_date, statement_value_to_pay, pdf_text)
    purchases_txt = statement_object.purchases_block()
    purchases_list = statement_object.purchase_list()
    csv_creation(purchases_list)
    read_and_print_csv()
    purchase_obj_list = load_data_from_csv()
    add_uber_tag(purchase_obj_list)
    add_ifood_tag(purchase_obj_list)
    if_tag_add_tag(purchase_obj_list, 'uber', 'transport')
    add_tag_based_on_description(purchase_obj_list, 'gift card', 'food')
    add_tag_based_on_description(purchase_obj_list, 'gift card', 'ifood')
    add_tag_based_on_description(purchase_obj_list, 'MerceariaRosalina', 'supermarket')
    add_tag_based_on_description(purchase_obj_list, 'ASSAI ATACADISTA', 'supermarket')
    add_tag_based_on_description(purchase_obj_list, 'LIMA PET SHOP', 'pet')
    add_tag_based_on_description(purchase_obj_list, 'AUTO POSTO TAK', 'fuel')
    add_tag_based_on_description(purchase_obj_list, 'AUTO POSTO CASSIANO', 'fuel')
    add_tag_based_on_description(purchase_obj_list, 'MERCADOLIVRE', 'mercadolivre')
    add_tag_based_on_description(purchase_obj_list, 'MOVIDA', 'transport')

    update_csv_file(purchase_obj_list)

    total_uber(purchases_list)
    seller = "ifood"
    seller_total(purchases_list, seller)
    sum = 0
    sum += total_by_tag(purchase_obj_list, 'food')
    sum += total_by_tag(purchase_obj_list, 'health')
    sum += total_by_tag(purchase_obj_list, 'supermarket')
    sum += total_by_tag(purchase_obj_list, 'transport')
    sum += total_by_tag(purchase_obj_list, 'housing')
    sum += total_by_tag(purchase_obj_list, 'entertainment')
    sum += total_by_tag(purchase_obj_list, 'fuel')
    total_by_tag(purchase_obj_list, 'ifood')
    sum += total_by_tag(purchase_obj_list, 'mercadolivre')
    sum += total_without_tag(purchase_obj_list)
    print("Total statement: R${0}".format(str(sum.__round__(2))))
    for purchase in purchases_without_tag(purchase_obj_list):
        print(purchase.description + ' - ' + purchase.value)



    #text_file_from_statement(pdf_text)
