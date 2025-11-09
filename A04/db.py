import sys
import os
import sqlite3
import csv


class WorldDBApp:
    DB_NAME = "db.sqlite"

    def __init__(self, argv):
        self.argv = argv
        self.conn = sqlite3.connect(self.DB_NAME)
        self.conn.row_factory = sqlite3.Row

        try:
            self.load_csv_files()
            self.answer_question()
        finally:
            self.conn.close()

    def load_csv_files(self):
        """
        Create tables and import data from CSV files given as command-line parameters.
        If no parameters are given, assume database already exists.
        """
        if not self.argv:
            # No CSVs given: use existing DB (required by assignment)
            if not os.path.exists(self.DB_NAME):
                print(
                    "No CSV files specified and database db.sqlite does not exist.",
                    file=sys.stderr,
                )
                sys.exit(1)
            return

        for path in self.argv:
            if not os.path.isfile(path):
                print(f"CSV file not found: {path}", file=sys.stderr)
                continue

            table_name = self._get_table_name_from_path(path)

            if self.table_exists(table_name):
                # Do not recreate existing tables
                continue

            self.create_table_from_csv(path, table_name)

    def _get_table_name_from_path(self, path):
        filename = os.path.basename(path)
        name, _ext = os.path.splitext(filename)
        return name

    def table_exists(self, table_name):
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type='table' AND name=?
            """,
            (table_name,),
        )
        return cur.fetchone() is not None

    def create_table_from_csv(self, csv_path, table_name):
        with open(csv_path, newline="", encoding="utf-8") as f:
            # Read a small sample to detect delimiter
            sample = f.read(4096)
            f.seek(0)

            # Detect delimiter (handles , or ;)
            try:
                dialect = csv.Sniffer().sniff(sample, delimiters=",;")
            except csv.Error:
                # Fallback: assume comma
                dialect = csv.get_dialect("excel")

            reader = csv.reader(f, dialect)

            try:
                header = next(reader)
            except StopIteration:
                print(f"CSV file is empty: {csv_path}", file=sys.stderr)
                return

            # Strip whitespace + possible BOM
            cleaned_header = []
            for col in header:
                col = col.strip()
                if col.startswith("\ufeff"):
                    col = col.lstrip("\ufeff")
                cleaned_header.append(col)

            columns = cleaned_header

            # Build CREATE TABLE (all TEXT is fine for this assignment)
            columns_sql = ", ".join(f'"{col}" TEXT' for col in columns)
            create_sql = f'CREATE TABLE "{table_name}" ({columns_sql});'
            self.conn.execute(create_sql)

            # Prepare INSERT
            placeholders = ", ".join("?" for _ in columns)
            insert_sql = f'INSERT INTO "{table_name}" VALUES ({placeholders});'

            rows_to_insert = []
            for row in reader:
                # Skip completely empty lines
                if not any(field.strip() for field in row):
                    continue

                # If row has different length, try to fix or skip
                if len(row) != len(columns):
                    # You can log this if needed; for now we skip malformed rows
                    continue

                rows_to_insert.append(row)

            if rows_to_insert:
                self.conn.executemany(insert_sql, rows_to_insert)
                self.conn.commit()

    def answer_question(self):
        """
        Question for student 4:

        In what countries is used the Spanish language?
        Provide their full names, sorted alphabetically.
        """

        question = (
            "In what countries is used the Spanish language? "
            "Provide their full names, sorted alphabetically."
        )

        query = """
            SELECT DISTINCT c.Name
            FROM country AS c
            JOIN countrylanguage AS cl
              ON c.Code = cl.CountryCode
            WHERE cl.Language = 'Spanish'
            ORDER BY c.Name;
        """

        try:
            cur = self.conn.cursor()
            cur.execute(query)
            rows = cur.fetchall()
        except sqlite3.OperationalError as e:
            print(
                "Error while executing the query. Make sure the tables "
                "'country' and 'countrylanguage' were correctly created "
                "from the CSV files.",
                file=sys.stderr,
            )
            print(f"Details: {e}", file=sys.stderr)
            sys.exit(1)

        print(question)
        for row in rows:
            print(row[0])


if __name__ == "__main__":
    # argv[1:] = list of CSV files
    WorldDBApp(sys.argv[1:])