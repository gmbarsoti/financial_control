import os
from pdfPassword import create_yaml_file
from creditCardStatement import CreditCardStatement
from pdfStatement import (
    get_statement_payment_date,
    get_statement_value_to_pay,
    get_text_from_pdf,
    iterate_over_a_year_of_statements,
)
from categorization import (
    total_uber,
    seller_total,
    add_uber_tag,
    add_ifood_tag,
    add_related_tag,
    add_tag_based_on_description,
    total_by_tag,
    total_without_tag,
    purchases_without_tag,
)
from csvManipulation import csv_creation, load_data_from_csv, read_and_print_csv, update_csv_file


if __name__ == '__main__':
    yaml_path = os.path.join('.', 'statementSource', 'financial.yaml')
    if not os.path.exists(yaml_path):
        create_yaml_file()
    issuerInstitution = 'Meliuz'
    # institution = 'Inter'

    iterate_over_a_year_of_statements(issuerInstitution)

    pdf_file = 'statementSource/Meliuz/2025/2025-09.pdf'
    # pdf_file = 'statementSource/Inter/inter_statement_nov_dec_2024.pdf'
    pdf_text = get_text_from_pdf(pdf_file, issuerInstitution)
    statement_payment_date = get_statement_payment_date(pdf_text, issuerInstitution)
    statement_value_to_pay = get_statement_value_to_pay(pdf_text, issuerInstitution)
    statement_object = CreditCardStatement(issuerInstitution, statement_payment_date, statement_value_to_pay, pdf_text)
    purchases_txt = statement_object.purchases_block()
    purchases_list = statement_object.purchase_list()
    csv_creation(purchases_list)
    read_and_print_csv()
    purchase_obj_list = load_data_from_csv()
    add_uber_tag(purchase_obj_list)
    add_ifood_tag(purchase_obj_list)
    add_related_tag(purchase_obj_list, 'uber', 'transport')
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
