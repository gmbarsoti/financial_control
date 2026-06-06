import os
import csv
import ast
from creditCardStatement import Purchase


def csv_creation(purchases_to_add):
    db_path = os.path.join('.', 'statementSource', 'data_base.csv')
    with open(db_path, 'w', encoding='UTF-8') as db_f:
        purchases_writer = csv.writer(db_f, delimiter=',', quotechar='"', escapechar='\\', quoting=csv.QUOTE_MINIMAL)
        purchases_writer.writerow(["card_info", "date", "description", "value", "tags"])
        for purchase in purchases_to_add:
            purchases_writer.writerow([purchase.card_info, purchase.date, purchase.description,
                                       purchase.value, purchase.tags])

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

def update_csv_file(purchase_obj_list: list):
    db_path = os.path.join('.', 'statementSource', 'data_base.csv')
    with open(db_path, 'w', encoding='UTF-8') as db_f:
        purchases_writer = csv.writer(db_f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        purchases_writer.writerow(["card_info", "date", "description", "value", "tags"])
        for purchase in purchase_obj_list:
            purchases_writer.writerow([purchase.card_info, purchase.date, purchase.description,
                                       purchase.value, purchase.tags])            