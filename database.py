import sqlite3
from datetime import datetime
import re

date_pattern_hyphen = re.compile(r'\b\d{4}-\d{2}-\d{2}\b')
date_pattern_underscore = re.compile(r'\b\d{4}_\d{2}_\d{2}\b')
date_pattern_period = re.compile(r'\b\d{4}\.\d{2}\.\d{2}\b')

class Database():
    
    def __init__(self):
        con = sqlite3.connect("tax.db")
        cursor = con.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS income(
            id INTEGER PRIMARY KEY,
            amount REAL NOT NULL CHECK(amount > 0),
            date DATE NOT NULL,
            serialnr TEXT UNIQUE,
            details TEXT,
            document TEXT UNIQUE
            );
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS expense(
            id INTEGER PRIMARY KEY,
            amount REAL NOT NULL CHECK(amount > 0),
            date DATE NOT NULL,
            deduct_percent REAL DEFAULT 100.0,
            serialnr TEXT UNIQUE,
            id_expense INTEGER,
            id_income INTEGER,
            vat_check INTEGER NOT NULL DEFAULT 0,
            details TEXT,
            document TEXT UNIQUE,
            FOREIGN KEY (id_expense) REFERENCES expense(id),
            FOREIGN KEY (id_income) REFERENCES income(id)
            );
            """
        )

        con.commit()
        con.close()

    def check_date_format(self, date):
        if date is None:
            date = datetime.now().date()
        else:
            if date_pattern_hyphen.match(date):
                date = datetime.strptime(date, "%Y-%m-%d").date()
            elif date_pattern_underscore.match(date):
                datetime.strptime(date, "%Y_%m_%d").date()
            elif date_pattern_period.match(date):
                date = datetime.strptime(date, "%Y.%m.%d").date()
        return date

    def record_income(self, amount, date=None, serialnr=None, details=None, document=None):
        con = sqlite3.connect("tax.db")
        cursor = con.cursor()

        query = """
        INSERT INTO income(amount, date, serialnr, details, document)
        VALUES(?, ?, ?, ?, ?)
        """
        date = self.check_date_format(date)

        params = (amount, date, serialnr, details, document)

        # print(params)

        cursor.execute(query, params)
        con.commit()
        con.close()

    def record_expense(
            self, amount,
            date=None,
            deduct_percent=100,
            serialnr=None,
            id_expense=None,
            id_income=None,
            vat_check = 0,
            document=None,
            details=''
            ):
        con = sqlite3.connect("tax.db")
        cursor = con.cursor()

        query = """
        INSERT INTO expense(amount, date, deduct_percent, serialnr, id_expense, id_income, vat_check, details, document)
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        date = self.check_date_format(date)

        params = (amount, date, deduct_percent, serialnr, id_expense, id_income, vat_check, details, document)

        # print(params)

        cursor.execute(query, params)
        con.commit()
        con.close()

    def get_incomes(self, start_date=None, end_date=None):
        con = sqlite3.connect("tax.db")
        cursor = con.cursor()

        query = "SELECT * FROM income;"
        cursor.execute(query)
        incomes = cursor.fetchall()

        con.close()

        return incomes

    def get_expenses(self, start_date=None, end_date=None):
        con = sqlite3.connect("tax.db")
        cursor = con.cursor()

        query = "SELECT * FROM expense;"
        cursor.execute(query)
        expenses = cursor.fetchall()

        con.close()

        return expenses

    def update_income(self, income_id, amount=None, date=None, serialnr=None, details=None, document=None):
        con = sqlite3.connect("tax.db")
        cursor = con.cursor()

        date = self.check_date_format(date)

        # Construct the UPDATE query dynamically based on provided parameters
        query = "UPDATE income SET "
        updates = []

        if amount is not None:
            updates.append(f"amount = {amount}")
        if date is None:
            updates.append(f"date = NULL")
        else:
            updates.append(f"date = '{date}'")
        if serialnr is None:
            updates.append(f"serialnr = NULL")
        else:
            updates.append(f"serialnr = '{serialnr}'")
        if details is None:
            updates.append(f"details = NULL")
        else:
            updates.append(f"details = '{details}'")
        if document is None:
            updates.append(f"document = NULL")
        else:
            updates.append(f"document = '{document}'")

        # print(f'updates: {updates}')

        query += ", ".join(updates)
        query += f" WHERE id = {income_id};"

        cursor.execute(query)
        con.commit()
        con.close()

    def update_expense(
            self,
            expense_id,
            amount=None,
            date=None,
            deduct_percent=None,
            serialnr=None,
            id_expense=None,
            id_income=None,
            vat_check=0,
            details=None,
            document=None
            ):
        con = sqlite3.connect("tax.db")
        cursor = con.cursor()

        date = self.check_date_format(date)

        # Construct the UPDATE query dynamically based on provided parameters
        query = "UPDATE expense SET "
        updates = []

        if amount is not None:
            updates.append(f"amount = {amount}")
        if date is None:
            updates.append(f"date = NULL")
        else:
            updates.append(f"date = '{date}'")
        if deduct_percent is None:
            updates.append(f"deduct_percent = NULL")
        else:
            updates.append(f"deduct_percent = {deduct_percent}")
        if serialnr is None:
            updates.append(f"serialnr = NULL")
        else:
            updates.append(f"serialnr = '{serialnr}'")
        if id_expense is None:
            updates.append(f"id_expense = NULL")
        else:
            updates.append(f"id_expense = '{id_expense}'")
        if id_income is None:
            updates.append(f"id_income = NULL")
        else:
            updates.append(f"id_income = '{id_income}'")
        if vat_check is None:
            updates.append(f"vat_check = NULL")
        else:
            updates.append(f"vat_check = {vat_check}")
        if details is None:
            updates.append(f"details = NULL")
        else:
            updates.append(f"details = '{details}'")
        if document is None:
            updates.append(f"document = NULL")
        else:
            updates.append(f"document = '{document}'")
        # print(f'updates: {updates}')

        query += ", ".join(updates)
        query += f" WHERE id = {expense_id};"

        # print(query)
        cursor.execute(query)
        con.commit()
        con.close()

    def del_income(self, income_id):
        con = sqlite3.connect("tax.db")
        cursor = con.cursor()

        query = f"DELETE FROM income WHERE id = {income_id};"
        cursor.execute(query)

        con.commit()
        con.close()

    def del_expense(self, expense_id):
        con = sqlite3.connect("tax.db")
        cursor = con.cursor()

        query = f"DELETE FROM expense WHERE id = {expense_id};"
        cursor.execute(query)

        con.commit()
        con.close()

    def nuke_db(self):
        con = sqlite3.connect("tax.db")
        cursor = con.cursor()

        cursor.execute("DELETE FROM income;")
        cursor.execute("DELETE FROM expense;")

        con.commit()
        con.close()

if __name__ == "__main__":

    db = Database()

    db.record_income(12, serialnr='23usf32', details='test income added')
    db.record_expense(235, serialnr='fsdh93', details='test expense')

    strdate = '2024-02-10'
    date = datetime.strptime(strdate, '%Y-%m-%d').date()

    incomes = db.get_incomes()
    for income in incomes:
        print(income)
    db.update_income(1, details="date and details updated", date=date)
    print('   modified:')
    incomes = db.get_incomes()
    for income in incomes:
        print(income)
    print('\n')
    expenses = db.get_expenses()
    for expense in expenses:
        print(expense)
    db.update_expense(1, amount=150.0, details="price and details updated")
    print('   modified:')
    expenses = db.get_expenses()
    for expense in expenses:
        print(expense)
    print('\n')

    db.nuke_db()

    print('   deleted:')
    incomes = db.get_incomes()
    for income in incomes:
        print(income)
    print('   deleted:')
    expenses = db.get_expenses()
    for expense in expenses:
        print(expense)
