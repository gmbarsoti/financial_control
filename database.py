import sqlite3


def connect_to_database(database_file):
    return sqlite3.connect(database_file)


if __name__ == '__main__':

    database_file_path = r".\source\application_database.db"
    sql_statements = [
        """CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY, 
                name text NOT NULL, 
                begin_date DATE, 
                end_date DATE
            );""",

        """CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY, 
                name TEXT NOT NULL, 
                priority INT, 
                project_id INT NOT NULL, 
                status_id INT NOT NULL, 
                begin_date DATE NOT NULL, 
                end_date DATE NOT NULL, 
                FOREIGN KEY (project_id) REFERENCES projects (id)
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

