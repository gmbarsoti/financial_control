import os
import csv


class FinancialTransaction:
    def __int__(self, date, recipient, depositor, description, value, type, tags=None):
        if tags is None:
            tags = []
        self.date = date
        self.recipient = recipient
        self.depositor = depositor
        self.description = description
        self.value = value
        self.type = type
        self.tags = tags


class Pix(FinancialTransaction):
    def __init__(self, message, received, institution):
        self.message = message
        self.received = received
        self.institution = institution


def csv_to_obj():
    nu_csv_path = os.path.join('.', 'source', 'Nu', 'nu.csv')
    pix_list = []
    with open(nu_csv_path, 'r', encoding='UTF-8') as nu_csv:
        nu_csv_dict = csv.DictReader(nu_csv)
        line_count = 0
        for row in nu_csv_dict:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            print(
                f'\t{row["date"]} - {row["value"]} - {row["description"]}.')
            line_count += 1
            #getting pixs
            if "Pix" in row["description"]:
                pix_list.append(Pix(row["description"], ))
        print(f'Processed {line_count} lines.')


if __name__ == '__main__':
    csv_to_obj()