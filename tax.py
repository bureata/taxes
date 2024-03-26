from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty

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
    amount_prop = StringProperty()
    date_prop = StringProperty()
    serialnr_prop = StringProperty()

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
                self.income_data = edited_data
                self.update_props()
                self.parent.parent.parent.db.update_income(*self.income_data)

        # Create and open the input popup
        input_popup = EditIncomePopup(income_data=self.income_data, callback=handle_edit, title='Input Popup')
        input_popup.open()

    def delete_income(self):
        def confirmed_deletion():
            # Delete the income record from the database
            # Implement your logic to delete the record
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

    def nuke(self):
        self.db.nuke_db()


class ExpenseLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(ExpenseLayout, self).__init__(**kwargs)
        self.db = Database()
       
    def add_expense(self):
        amount = self.ids.amount_input.text
        date = self.ids.date_input.text
        deduct_percent = self.ids.deduct_percent_input.text
        serialnr = self.ids.serialnr_input.text
        if serialnr == '':
            serialnr = None
        if deduct_percent == '':
            deduct_percent = None
        self.db.record_expense(amount, date, deduct_percent, serialnr)
        self.update_expense_display()
        self.clear_input()

    def update_expense_display(self):
        expenses = self.db.get_expenses()
        expenses_text = '\n'.join(str(expense) for expense in expenses)
        self.ids.expenses_label.text = expenses_text
    
    def clear_input(self):
        self.ids.amount_input.text = ''
        self.ids.date_input.text = ''
        self.ids.deduct_percent_input.text = ''
        self.ids.serialnr_input.text = ''

class MainWindow(BoxLayout):
    pass


from kivy.properties import ObjectProperty
class MyFirstWidget(BoxLayout):

    txt_inpt = ObjectProperty(None)

    def check_status(self, btn):
        print('button state is: {state}'.format(state=btn.state))
        print('text input text is: {txt}'.format(txt=self.txt_inpt))

if __name__ == '__main__':
    TaxApp().run()
