import sqlite3
from datetime import datetime

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
            document TEXT UNIQUE,
            details TEXT
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
            related_to_expense INTEGER,
            related_to_income INTEGER,
            document TEXT UNIQUE,
            details TEXT,
            FOREIGN KEY (related_to_expense) REFERENCES expense(id),
            FOREIGN KEY (related_to_income) REFERENCES income(id)
            );
            """
        )

        con.commit()
        con.close()

    def record_income(self, amount, date=None, serialnr=None, document=None, details=''):
        con = sqlite3.connect("tax.db")
        cursor = con.cursor()

        query = """
        INSERT INTO income(amount, date, serialnr, document, details)
        VALUES(?, ?, ?, ?, ?)
        """
        if date is None:
            date = datetime.now().date()

        params = (amount, date, serialnr, document, details)

        cursor.execute(query, params)
        con.commit()
        con.close()

    def record_expense(self, amount, date=None, deduct_percent=100, serialnr=None, related_to_expense=None, related_to_income=None, document=None, details=''):
        con = sqlite3.connect("tax.db")
        cursor = con.cursor()

        query = """
        INSERT INTO expense(amount, date, deduct_percent, serialnr, related_to_expense, related_to_income, document, details)
        VALUES(?, ?, ?, ?, ?, ?, ?, ?)
        """
        if date is None:
            date = datetime.now().date()

        params = (amount, date, deduct_percent, serialnr, related_to_expense, related_to_income, document, details)

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

    def update_income(self, income_id, amount=None, date=None, serialnr=None, document=None, details=None):
        con = sqlite3.connect("tax.db")
        cursor = con.cursor()

        # Construct the UPDATE query dynamically based on provided parameters
        query = "UPDATE income SET "
        updates = []

        if amount is not None:
            updates.append(f"amount = {amount}")
        if date is not None:
            updates.append(f"date = '{date}'")
        if serialnr is not None:
            updates.append(f"serialnr = '{serialnr}'")
        if document is not None:
            updates.append(f"document = '{document}'")
        if details is not None:
            updates.append(f"details = '{details}'")

        query += ", ".join(updates)
        query += f" WHERE id = {income_id};"

        cursor.execute(query)
        con.commit()
        con.close()

    def update_expense(self, expense_id, amount=None, date=None, deduct_percent=None, serialnr=None, related_to_expense=None, related_to_income=None, document=None, details=None):
        con = sqlite3.connect("tax.db")
        cursor = con.cursor()

        # Construct the UPDATE query dynamically based on provided parameters
        query = "UPDATE expense SET "
        updates = []

        if amount is not None:
            updates.append(f"amount = {amount}")
        if date is not None:
            updates.append(f"date = '{date}'")
        if deduct_percent is not None:
            updates.append(f"deduct_percent = {deduct_percent}")
        if serialnr is not None:
            updates.append(f"serialnr = '{serialnr}'")
        if related_to_expense is not None:
            updates.append(f"related_to_expense = {related_to_expense}")
        if related_to_income is not None:
            updates.append(f"related_to_income = {related_to_income}")
        if document is not None:
            updates.append(f"document = '{document}'")
        if details is not None:
            updates.append(f"details = '{details}'")

        query += ", ".join(updates)
        query += f" WHERE id = {expense_id};"

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
