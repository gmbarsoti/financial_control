import re
from datetime import datetime


class CreditCardStatement:
    def __init__(self, issuer, payment_date, total_value, statement_text):
        self.issuer = issuer
        self.payment_date = payment_date
        self.total_value = total_value
        self.statement_text = statement_text

    def purchases_block(self):
        full_block = ''
        match self.issuer.lower():
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

    def is_date_and_description_in_one_line(self, line_to_check):
        if len(line_to_check) > 7:
            return True

    def getting_values_for_purchase(self, line, getting_dates_and_descriptions, values, dates):
        if 'R$' not in line:
            return False
        if getting_dates_and_descriptions:
            return False
        if len(values) < len(dates):
            return True


    def find_index_by_regex(self, pattern, lst):
        regex = re.compile(pattern)
        for index, element in enumerate(lst):
            if regex.search(element):  # Check for a match
                return index
        return None  # Return None if no match is found

    def purchase_list(self):
        match self.issuer.lower():
            case "meliuz":
                card_pattern1 = re.compile(r"5458 •{4} [0-9]{4}", re.IGNORECASE)
                card_pattern2 = re.compile(r"7605", re.IGNORECASE)
                date_pattern = re.compile(r"[0-9]{2} [A-Z][a-z]{2}")
                date, description, card_info, value, purchase_list = [], [], [], [], []
                for line in self.purchases_block().split('\n')[:-1]:
                    if line[0] == ' ':
                        line = line[1:]
                    if date_pattern.match(line):
                        if self.is_date_and_description_in_one_line(line):
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
                    if self.getting_values_for_purchase(line, getting_dates_and_descriptions, values, dates):
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
                payment_index = self.find_index_by_regex(statement_payment_pattern, values)
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

    def convert_month_prefix_to_number(self, month_prefix):
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

    def convert_date_day_month_name_to_suitable_pattern(self, date_to_convert):
        day_and_month_name = date_to_convert[:-1].split(' ')
        day = day_and_month_name[0]
        month_name = day_and_month_name[1]
        month_number = self.convert_month_prefix_to_number(month_name)
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