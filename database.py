import sqlite3


def connect_to_database(database_file):
    return sqlite3.connect(database_file)


#def add_credit_card_operation_to_database(operation_to_be_added):
def add_credit_card_operation_to_database(set_of_operations_to_add):
    database_file_path = r".\statementSource\credit_card_database.db"
    statement = "INSERT INTO meliuz_credit_card_operation (card_info, date, description, value, tags) VALUES (?, ?, ?, ?, ?)"
    try:
        with sqlite3.connect(database_file_path) as database_connection:
            print(f"Opened SQLite database with version {sqlite3.sqlite_version} successfully.")
            cursor = database_connection.cursor()
            for operation_to_add in set_of_operations_to_add:
                tags_comma_separated_string = ', '.join(operation_to_add.tags)
                cursor.execute(statement, (operation_to_add.card_info,	operation_to_add.date, operation_to_add.description, operation_to_add.value, tags_comma_separated_string))
            database_connection.commit()
            pass
    except sqlite3.OperationalError as exception:
        print("Failed to open database: ", exception)


if __name__ == '__main__':
    database_file_path = r".\statementSource\credit_card_database.db"
    sql_statements = [
        """CREATE TABLE IF NOT EXISTS meliuz_credit_card_operation (
                id INTEGER PRIMARY KEY,
                card_info TEXT NOT NULL, 
                date TEXT NOT NULL,
                description TEXT NOT NULL,
                value TEXT NOT NULL,
                tags TEXT
            );"""
    ]
    try:
        with sqlite3.connect(database_file_path) as database_connection:
            print(f"Opened SQLite database with version {sqlite3.sqlite_version} successfully.")
            cursor = database_connection.cursor()
            for statement in sql_statements:
                cursor.execute(statement)
            database_connection.commit()
            pass
    except sqlite3.OperationalError as exception:
        print("Failed to open database: ", exception)

