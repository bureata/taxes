from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty, NumericProperty, BooleanProperty
from kivy.uix.textinput import TextInput

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

    def __init__(
            self,
            id,
            amount,
            date,
            serial_nr,
            callback,
            **kwargs):
        super(EditIncomePopup, self).__init__(**kwargs)
        self.callback = callback
        self.id_prop = str(id)
        self.ids.amount_input.text = str(amount) if amount is not None else ''
        self.ids.date_input.text = str(date) if date is not None else ''
        self.ids.serialnr_input.text = str(serial_nr) if serial_nr is not None else ''
    
    def save(self):
        updated_data = (
            self.id_prop,
            self.ids.amount_input.text,
            self.ids.date_input.text,
            self.ids.serialnr_input.text
        )
        updated_data = [attr or None for attr in updated_data]
        self.callback(*updated_data)
        self.dismiss()


class IncomeWidget(BoxLayout):
    id_prop = StringProperty()
    amount_prop = StringProperty()
    date_prop = StringProperty()
    serialnr_prop = StringProperty()

    def __init__(
            self,
            id,
            amount,
            date=None,
            serial_nr=None,
            details=None,
            document=None,
            **kwargs
            ):
        super(IncomeWidget, self).__init__(**kwargs)
        # self.income_data = income_data
        # self.update_props()
        self.update_props(id, amount, date, serial_nr)

    def update_props(self, id, amount, date, serial_nr):
        self.id_prop = str(id) if id else ''
        self.amount_prop = str(amount) if amount else ''
        self.date_prop = str(date) if date else ''
        self.serialnr_prop = str(serial_nr) if serial_nr else ''

    def edit_income(self):
        # method that handles the data returned by the popup
        def handle_edit(id, amount, date, serial_nr):
            if amount:
                self.update_props(id, amount, date, serial_nr)
                id = int(id)
                amount = float(amount)
                self.parent.parent.parent.db.update_income(id, amount, date, serial_nr)
                self.parent.parent.parent.parent.parent.ids.taxes_layout.update_widget()

        # Create and open the input popup
        input_popup = EditIncomePopup(self.id_prop, self.amount_prop, self.date_prop, self.serialnr_prop, callback=handle_edit, title='Input Popup')
        input_popup.open()        

    def delete_income(self):
        def confirmed_deletion():
            # Delete the income record from the database
            self.parent.parent.parent.db.del_income(self.id_prop)
            self.parent.parent.parent.parent.parent.ids.taxes_layout.update_widget()
            self.parent.remove_widget(self)
        
        # Create and open the confirmation popup
        confirmation_popup = DeletePopup(
            message="Are you sure you want to delete this income?",
            callback=confirmed_deletion,
            details=f"Income of <{self.amount_prop}> with id <{self.id_prop}> and serial nr <{self.serialnr_prop}> will be deleted!"
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
            amount = float(amount)
            date = str(date) if date != '' else None
            self.db.record_income(amount, date, serialnr)
            self.update_income_display()
        self.clear_input()
        self.parent.parent.ids.taxes_layout.update_widget()

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
            custom_income_widget = IncomeWidget(*income_data)
            income_entries_layout.add_widget(custom_income_widget)


class EditExpensePopup(Popup):
    id_prop = StringProperty()
    check_vat_prop = BooleanProperty()

    def __init__(self, expense_data, callback, **kwargs):
        super(EditExpensePopup, self).__init__(**kwargs)
        self.callback = callback
        self.expense_data = expense_data
        self.id_prop = str(expense_data[0])
        self.ids.amount_input.text = str(expense_data[1])
        self.ids.date_input.text = str(expense_data[2]) if self.expense_data[2] else ''
        self.ids.deduct_percent_input.text = str(expense_data[3]) if self.expense_data[3] else ''
        self.ids.serialnr_input.text = str(expense_data[4]) if self.expense_data[4] else ''
        self.ids.id_expense_input.text = str(expense_data[5]) if self.expense_data[5] else ''
        self.ids.id_income_input.text = str(expense_data[6]) if self.expense_data[6] else ''
        self.check_vat_prop = expense_data[7]

    def save(self):
        check_vat = True if self.ids.vat_check.active else False
        updated_data = (
            self.id_prop,
            self.ids.amount_input.text,
            self.ids.date_input.text,
            self.ids.deduct_percent_input.text,
            self.ids.serialnr_input.text,
            self.ids.id_expense_input.text,
            self.ids.id_income_input.text,
        )
        updated_data = [attr or None for attr in updated_data]
        updated_data.append(check_vat)
        self.callback(updated_data)
        self.dismiss()


class ExpenseWidget(BoxLayout):
    id_prop = StringProperty()
    amount_prop = StringProperty()
    date_prop = StringProperty()
    deduct_percent_prop = StringProperty()
    serialnr_prop = StringProperty()
    id_expense_prop = StringProperty()
    id_income_prop = StringProperty()
    check_vat_prop = BooleanProperty()

    def __init__(self, expense_data, **kwargs):
        super(ExpenseWidget, self).__init__(**kwargs)
        self.expense_data = expense_data
        self.update_props()

    def update_props(self):
        self.id_prop = str(self.expense_data[0])
        self.amount_prop = str(self.expense_data[1]) if self.expense_data[1] else ''
        self.date_prop = str(self.expense_data[2]) if self.expense_data[2] else ''
        self.deduct_percent_prop = str(self.expense_data[3]) if self.expense_data[3] else ''
        self.serialnr_prop = str(self.expense_data[4]) if self.expense_data[4] else ''
        self.id_expense_prop = str(self.expense_data[5]) if self.expense_data[5] else ''
        self.id_income_prop = str(self.expense_data[6]) if self.expense_data[6] else ''
        self.check_vat_prop = self.expense_data[7]

    def edit_expense(self):
        # method that handles the data returned by the popup
        def handle_edit(edited_data):
            if self.expense_data != edited_data:
                self.expense_data = edited_data
                self.update_props()
                self.parent.parent.parent.db.update_expense(*self.expense_data)
                self.parent.parent.parent.parent.parent.ids.taxes_layout.update_widget()

        # Create and open the input popup
        expense_popup = EditExpensePopup(expense_data=self.expense_data, callback=handle_edit, title='Expense Popup')
        expense_popup.open()

    def delete_expense(self):
        def confirmed_deletion():
            # Delete the expense record from the database
            self.parent.parent.parent.db.del_expense(self.expense_data[0])
            self.parent.parent.parent.parent.parent.ids.taxes_layout.update_widget()
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
        vat_check = True if self.ids.vat_check.active else False
        attrs = [attr if attr != '' else None for attr in [date, deduct_percent, serialnr, id_expense, id_income]]
        if amount != '':
            if not attrs[1]:
                attrs[1] = 100
            payload = [amount] + attrs + [vat_check]
            self.db.record_expense(*payload)
            self.update_expense_display()
        self.clear_input()
        self.ids.deduct_percent_input.text = '100'
        self.parent.parent.ids.taxes_layout.update_widget()

    def update_expense_display(self, dt=None):
        expense_entries_layout = self.ids.expense_entries
        expense_entries_layout.clear_widgets()
        expenses = self.db.get_expenses()
        for expense_data in expenses:
            expense_entry_widget = ExpenseWidget(expense_data=expense_data)
            expense_entries_layout.add_widget(expense_entry_widget)
    
    def clear_input(self):
        self.ids.amount_input.text = ''
        self.ids.date_input.text = ''
        self.ids.deduct_percent_input.text = ''
        self.ids.id_expense_input.text = ''
        self.ids.id_income_input.text = ''
        self.ids.serialnr_input.text = ''
        self.ids.vat_check.active = False


class TaxesLayout(BoxLayout):
    min_income = 3300
    min_cass_threshold = 6 * min_income
    max_cass_threshold = 60 * min_income
    min_cas_threshold = 12 * min_income
    max_cas_threshold = 24 * min_income

    def __init__(self, **kwargs):
        super(TaxesLayout, self).__init__(**kwargs)
        self.db = Database()
        self.get_data()
        self.calculate()

    def update_widget(self):
        self.get_data()
        self.calculate()
        self.ids.income.text = f'{self.income:.2f}'
        self.ids.expense.text = f'{self.expense:.2f}'
        self.ids.deductible.text = f'{self.deductible:.2f}'
        self.ids.cass.text = f'{self.cass:.2f}'
        self.ids.cas.text = f'{self.cas:.2f}'
        self.ids.income_tax.text = f'{self.income_tax:.2f}'
        self.ids.total_tax.text = f'{self.total_tax:.2f}'
        self.ids.profit.text = f'{self.profit:.2f}'

    def get_data(self):
        self.incomes = self.db.get_incomes()
        self.expenses = self.db.get_expenses()

    def calculate_income(self):
        self.income = 0
        for income in self.incomes:
            self.income += income[1]

    def calculate_expense(self):
        self.expense = 0
        for expense in self.expenses:
            self.expense += expense[1]

    def calculate_deductible(self):
        self.deductible = 0
        for expense in self.expenses:
            self.deductible += expense[1] * expense[3] / 100

    def calculate_cass(self):
        cass = (self.income - self.expense) * 0.1
        if cass < self.min_cass_threshold:
            self.cass = self.min_cass_threshold * 0.1
        elif self.min_cass_threshold <= cass <= self.max_cass_threshold:
            self.cass = cass
        else:
            self.cass = self.max_cass_threshold
        return self.cass
    
    def calculate_cas(self):
        income_net = self.income - self.expense
        if income_net < self.min_cas_threshold:
            self.cas = 0
        elif self.min_cas_threshold <= income_net <= self.max_cas_threshold:
            self.cas = 9900
        else:
            self.cas = 19800
        return self.cas
    
    def calculate_income_tax(self):
        net = self.income - self.deductible - self.cass - self.cas
        if net > 0:
            self.income_tax = net * 0.1
        else:
            self.income_tax = 0
        return self.income_tax
    
    def calculate_total_tax(self):
        self.total_tax = self.income_tax + self.cass + self.cas
    
    def calculate_profit(self):
        self.profit = self.income - self.expense - self.cass - self.cas - self.income_tax
        return self.profit
    
    def calculate(self):
        self.calculate_income()
        self.calculate_expense()
        self.calculate_deductible()
        self.calculate_cass()
        self.calculate_cas()
        self.calculate_income_tax()
        self.calculate_total_tax()
        self.calculate_profit()


class MainWindow(BoxLayout):
    pass


if __name__ == '__main__':
    TaxApp().run()
