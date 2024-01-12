import os
import csv
from enum import Enum


class TransactionType(Enum):
    PIX = 1
    PAYMENT = 2


class FinancialTransaction:
    def __init__(self, date, recipient, depositor, value, type, tags=None):
        if tags is None:
            tags = []
        self.date = date
        self.recipient = recipient
        self.depositor = depositor
        self.value = value
        self.type = type
        self.tags = tags


class Pix(FinancialTransaction):
    def __init__(self, date, recipient, depositor, value, type, received, institution, message="", tags=None):
        if tags is None:
            tags = []
        super().__init__(date, recipient, depositor, value, type, tags)
        self.received = received
        self.institution = institution
        self.message = message



def parse_pix_description(description, received):
    elements = description.split(" - ")

    recipient = ""
    depositor = ""
    if received:
        recipient = "Account owner"
        depositor = elements[1]
    else:
        recipient = elements[1]
        depositor = "Account owner"

    if len(elements) >4:
        elements[3] += elements[4]

    pix_description = {
        "General": elements[0],
        "Recipient": recipient,
        "Depositor": depositor,
        "key piece": elements[2],
        "Institution": elements[3],
        "Received": received
    }
    return pix_description


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
            pix_pattern = " Pix -"
            if pix_pattern in row["description"]:
                #parse pix description
                received = True
                if float(row["value"]) < 0.0:
                    received = False
                pix_description = parse_pix_description(row["description"], received)
                pix_list.append(Pix(row["date"], pix_description["Recipient"],
                                    pix_description["Depositor"], float(row["value"]),
                                    TransactionType.PIX, pix_description["Received"],
                                    pix_description["Institution"], ""))
        print(f'Processed {line_count} lines.')


if __name__ == '__main__':
    csv_to_obj()
    #pix_obj = Pix("eu", "Nu", "selva")
    pass