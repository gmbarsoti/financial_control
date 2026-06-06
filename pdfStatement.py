from datetime import datetime
import os
import time
from pdfminer.high_level import extract_text
from pdfPassword import get_from_ref_yaml
from creditCardStatement import CreditCardStatement
import database

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
            payment_date = payment_date.replace(' ', '')
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
                value_to_pay = value_to_pay.replace(' ', '')
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

def iterate_over_a_year_of_statements(credit_card_institution):
    match credit_card_institution.lower():
        case "meliuz":
            for i in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]:
                month = str(i) if len(str(i)) > 1 else ''.join(['0', str(i)])
                pdf_file = f'statementSource/{credit_card_institution}/2025/2025-{month}.pdf'
                pdf_text = get_text_from_pdf(pdf_file, credit_card_institution)
                statement_payment_date = get_statement_payment_date(pdf_text, credit_card_institution)
                statement_value_to_pay = get_statement_value_to_pay(pdf_text, credit_card_institution)
                statement_object = CreditCardStatement(credit_card_institution, statement_payment_date, statement_value_to_pay, pdf_text)
                purchases_list = statement_object.purchase_list()
                database.add_credit_card_operation_to_database(purchases_list)