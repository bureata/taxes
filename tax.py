from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty, NumericProperty

from kivy.config import Config
Config.set('graphics', 'width', '1680')
Config.set('graphics', 'height', '1050')
# Config.set('graphics', 'fullscreen', '0')

Config.write()
# print("Width:", Config.get('graphics', 'width'))
# print("Height:", Config.get('graphics', 'height'))


import os
import sys

from database import Database

class TaxApp(App):

    def build(self):
    
        return MainWindow()
    
    def reload_app(self, instance):
        print("Reloading...")
        # Restart the application
        os.execv(sys.executable, ['python'] + sys.argv)


class DeletePopup(Popup):
    message_prop = StringProperty()
    details_prop = StringProperty()

    def __init__(self, message, callback, details=None, **kwargs):
        super().__init__(**kwargs)
        self.title = "Confirmation"
        self.message_prop = message
        self.details_prop = details
        self.callback = callback

    def confirm(self):
        self.callback()
        self.dismiss()


class EditIncomePopup(Popup):
    id_prop = StringProperty()

    def __init__(self, income_data, callback, **kwargs):
        super(EditIncomePopup, self).__init__(**kwargs)
        self.callback = callback
        self.income_data = income_data
        self.id_prop = str(income_data[0])
        self.ids.amount_input.text = str(income_data[1])
        self.ids.date_input.text = str(income_data[2])
        self.ids.serialnr_input.text = str(income_data[3])
    
    def save(self):
        updated_data = (
            self.id_prop,
            self.ids.amount_input.text,
            self.ids.date_input.text,
            self.ids.serialnr_input.text
        )
        self.callback(updated_data)
        self.dismiss()


class IncomeWidget(BoxLayout):
    id_prop = StringProperty()
    amount_prop = StringProperty()
    date_prop = StringProperty()
    serialnr_prop = StringProperty()

    def __init__(self, income_data, **kwargs):
        super(IncomeWidget, self).__init__(**kwargs)
        self.income_data = income_data
        self.update_props()

    def update_props(self):
        self.id_prop = str(self.income_data[0])
        self.amount_prop = str(self.income_data[1])
        self.date_prop = str(self.income_data[2])
        self.serialnr_prop = str(self.income_data[3])

    def edit_income(self):
        # method that handles the data returned by the popup
        def handle_edit(edited_data):
            if self.income_data != edited_data:
                if edited_data[1] != '':
                    self.income_data = edited_data
                    self.update_props()
                    print(self.income_data)
                    self.parent.parent.parent.db.update_income(*self.income_data)

        # Create and open the input popup
        input_popup = EditIncomePopup(income_data=self.income_data, callback=handle_edit, title='Input Popup')
        input_popup.open()

    def delete_income(self):
        def confirmed_deletion():
            # Delete the income record from the database
            print(f"Deleting income with id {self.id_prop}:\n{self.income_data}")
            self.parent.parent.parent.db.del_income(self.income_data[0])
            self.parent.remove_widget(self)
        
        # Create and open the confirmation popup
        confirmation_popup = DeletePopup(
            message="Are you sure you want to delete this income?",
            callback=confirmed_deletion,
            details=f"This will be deleted from the database:\n{str(self.income_data)}"
            )
        confirmation_popup.open()


class IncomeLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.db = Database()
        Clock.schedule_once(self.update_income_display)

    def add_income(self):
        amount = self.ids.amount_input.text
        date = self.ids.date_input.text
        serialnr = self.ids.serialnr_input.text
        if serialnr == '':
            serialnr = None
        if amount != '':
            self.db.record_income(amount, date, serialnr)
            self.update_income_display()
        self.clear_input()

    def clear_input(self):
        self.ids.amount_input.text = ''
        self.ids.date_input.text = ''
        self.ids.serialnr_input.text = ''

    def nuke(self):
        self.db.nuke_db()

    def update_income_display(self, dt=None):
        income_entries_layout = self.ids.income_entries
        income_entries_layout.clear_widgets()
        incomes = self.db.get_incomes()
        for income_data in incomes:
            custom_income_widget = IncomeWidget(income_data=income_data)
            income_entries_layout.add_widget(custom_income_widget)


class EditExpensePopup(Popup):
    id_prop = StringProperty()
    check_vat_prop = NumericProperty()

    def __init__(self, expense_data, callback, **kwargs):
        super(EditExpensePopup, self).__init__(**kwargs)
        self.callback = callback
        self.expense_data = expense_data
        self.id_prop = str(expense_data[0])
        self.ids.amount_input.text = str(expense_data[1])
        self.ids.date_input.text = str(expense_data[2])
        self.ids.deduct_percent_input.text = str(expense_data[3])
        self.ids.serialnr_input.text = str(expense_data[4])
        self.ids.id_expense_input.text = str(expense_data[5])
        self.ids.id_income_input.text = str(expense_data[6])
        self.check_vat_prop = expense_data[7]

    
    def save(self):
        check_vat = 1 if self.ids.vat_check.active else 0
        updated_data = (
            self.id_prop,
            self.ids.amount_input.text,
            self.ids.date_input.text,
            self.ids.deduct_percent_input.text,
            self.ids.serialnr_input.text,
            self.ids.id_expense_input.text,
            self.ids.id_income_input.text,
            check_vat,
            None,
            None
        )
        self.callback(updated_data)
        self.dismiss()


class ExpenseWidget(BoxLayout):
    id_prop = StringProperty()
    amount_prop = StringProperty()
    date_prop = StringProperty()
    deduct_percent_prop = StringProperty()
    id_expense_prop = StringProperty()
    id_income_prop = StringProperty()
    serialnr_prop = StringProperty()
    check_vat_prop = NumericProperty()

    def __init__(self, expense_data, **kwargs):
        super(ExpenseWidget, self).__init__(**kwargs)
        self.expense_data = expense_data
        self.update_props()

    def update_props(self):
        self.id_prop = str(self.expense_data[0])
        self.amount_prop = str(self.expense_data[1])
        self.date_prop = str(self.expense_data[2])
        self.deduct_percent_prop = str(self.expense_data[3])
        self.serialnr_prop = str(self.expense_data[4])
        self.id_expense_prop = str(self.expense_data[5])
        self.id_income_prop = str(self.expense_data[6])
        self.check_vat_prop = self.expense_data[7]

    def edit_expense(self):
        # method that handles the data returned by the popup
        def handle_edit(edited_data):
            if self.expense_data != edited_data:
                self.expense_data = edited_data
                self.update_props()
                print('from edit expense popup:', self.expense_data)
                self.parent.parent.parent.db.update_expense(*self.expense_data)

        # Create and open the input popup
        input_popup = EditExpensePopup(expense_data=self.expense_data, callback=handle_edit, title='Expense Popup')
        input_popup.open()

    def delete_expense(self):
        def confirmed_deletion():
            # Delete the expense record from the database
            print(f"Deleting expense with id {self.id_prop}:\n{self.expense_data}")
            self.parent.parent.parent.db.del_expense(self.expense_data[0])
            self.parent.remove_widget(self)
        
        # Create and open the confirmation popup
        confirmation_popup = DeletePopup(
            message="Are you sure you want to delete this expense?",
            callback=confirmed_deletion,
            details=f"This will be deleted from the database:\n{str(self.expense_data)}"
            )
        confirmation_popup.open()


class ExpenseLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(ExpenseLayout, self).__init__(**kwargs)
        self.db = Database()
        Clock.schedule_once(self.update_expense_display)

    def add_expense(self):
        amount = self.ids.amount_input.text
        date = self.ids.date_input.text
        deduct_percent = self.ids.deduct_percent_input.text
        id_expense = self.ids.id_expense_input.text
        id_income = self.ids.id_income_input.text
        serialnr = self.ids.serialnr_input.text
        vat_check = 1 if self.ids.vat_check.active else 0
        print(f'vat check: {vat_check}')
        attrs = [attr if attr != '' else None for attr in [serialnr, deduct_percent, id_expense, id_income]]
        if amount != '':
            if not attrs[0]:
                attrs[0] = 100
            self.db.record_expense(amount, date, *attrs, vat_check=vat_check)
            self.update_expense_display()
        self.clear_input()

    def update_expense_display(self):
        expenses = self.db.get_expenses()
        expenses_text = '\n'.join(str(expense) for expense in expenses)
        self.ids.expenses_label.text = expenses_text

    def update_expense_display(self, dt=None):
        expense_entries_layout = self.ids.expense_entries
        expense_entries_layout.clear_widgets()
        expenses = self.db.get_expenses()
        for expense_data in expenses:
            custom_expense_widget = ExpenseWidget(expense_data=expense_data)
            expense_entries_layout.add_widget(custom_expense_widget)
    
    def clear_input(self):
        self.ids.amount_input.text = ''
        self.ids.date_input.text = ''
        self.ids.deduct_percent_input.text = ''
        self.ids.id_expense_input.text = ''
        self.ids.id_income_input.text = ''
        self.ids.serialnr_input.text = ''
        self.ids.vat_check.active = False


class MainWindow(BoxLayout):
    pass


if __name__ == '__main__':
    TaxApp().run()
