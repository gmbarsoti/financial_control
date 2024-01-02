import os
import csv


class Pix:
    def __init__(self, date, description, card_info, value, tags=None):
        if tags is None:
            tags = []
        self.date = date
        self.description = description
        self.card_info = card_info
        self.value = value
        self.tags = tags

def csv_to_obj():
    nu_csv_path = os.path.join('.', 'source', 'Nu', 'nu.csv')

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
        print(f'Processed {line_count} lines.')


if __name__ == '__main__':
    csv_to_obj()