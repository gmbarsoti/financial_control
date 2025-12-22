import os
from datetime import datetime
from dateutil.rrule import rrule, MONTHLY
from pathlib import Path


def months_iterator(initial_date, final_date):
    for date in rrule(MONTHLY, dtstart=initial_date, until=final_date):
        print(date.strftime("%Y-%m"))


def create_statement_issuers_folders(statement_source_directory, statement_issuers, statement_year):
    for statement_issuer in statement_issuers:
        statement_issuer_path = os.path.join('.', statement_source_directory, statement_issuer._name, statement_year)
        Path(statement_issuer_path).mkdir(parents=True, exist_ok=True)


class StatementIssuer:
    def __init__(self, name):
        self.name = name

    @property
    def name(self):
        return self._namme

    @name.setter
    def name(self, value):
        self._name = value


def main():
    issuers_list = [StatementIssuer("Meliuz")]
    issuers_list.append(StatementIssuer("Inter"))
    issuers_list.append(StatementIssuer("Nu"))
    create_statement_issuers_folders("statementSource", issuers_list, "2025")
    for issuer in issuers_list:
        print(issuer._name)


if __name__ == "__main__":
    main()



