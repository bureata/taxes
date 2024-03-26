from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock

from kivy.config import Config
Config.set('graphics', 'width', '1680')
Config.set('graphics', 'height', '1050')
Config.set('graphics', 'fullscreen', '0')

Config.write()
# print("Width:", Config.get('graphics', 'width'))
# print("Height:", Config.get('graphics', 'height'))


import os
import sys

from database import Database

class TaxApp(App):
    def build(self):
        # self.layout = BoxLayout(orientation='vertical')
        # self.reload_button = Button(text='Reload')
        # self.reload_button.bind(on_press=self.reload_app)
        # self.layout.add_widget(self.reload_button)
        # # Adding MainWindow instance to the layout
        # self.main_window_layout = MainWindow()
        # self.layout.add_widget(self.main_window_layout)
        # return self.layout
    
        return MainWindow()
    
    def reload_app(self, instance):
        print("Reloading...")
        # Restart the application
        os.execv(sys.executable, ['python'] + sys.argv)


class IncomeWidget(BoxLayout):
    def __init__(self, income_data, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.padding = [10, 10]
        
        id_label = Label(text=f"{income_data[0]}")
        id_label.size_hint = (0.15, 1)
        id_label.width = 10
        amount_label = Label(text=f"{income_data[1]}")
        date_label = Label(text=f"{income_data[2]}")
        serialnr_label = Label(text=f"{income_data[3]}")
        
        self.add_widget(id_label)
        self.add_widget(amount_label)
        self.add_widget(date_label)
        self.add_widget(serialnr_label)

        edit_button = Button(text="Edit")
        edit_button.size_hint = (0.5, 1)
        edit_button.bind(on_press=lambda instance: self.edit_income())
        self.add_widget(edit_button)

        delete_button = Button(text="Delete")
        delete_button.size_hint = (0.5, 1)
        delete_button.bind(on_press=lambda instance: self.delete_income(income_data))
        self.add_widget(delete_button)

    def edit_income(self):
        pass

    def delete_income(self, income_data):
        # Delete the income record from the database
        # Implement your logic to delete the record
        print("Deleting income:", income_data)

class IncomeLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.db = Database()
        Clock.schedule_once(self.update_income_display)

    # def update_income_display(self):
    #     self.clear_widgets()
    #     incomes = self.db.get_incomes()
    #     for income_data in incomes:
    #         print(income_data)
    #         custom_income_widget = IncomeWidget(income_data)
    #         self.add_widget(custom_income_widget)


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
        income_entries_layout = self.ids.income_entries  # Accessing the BoxLayout inside the ScrollView
        income_entries_layout.clear_widgets()  # Clear existing widgets before adding new ones

        incomes = self.db.get_incomes()
        for income_data in incomes:
            custom_income_widget = IncomeWidget(income_data)
            income_entries_layout.add_widget(custom_income_widget)

    def nuke(self):
        self.db.nuke_db()


# class IncomeLayout(BoxLayout):
#     def __init__(self, **kwargs):
#         super(IncomeLayout, self).__init__(**kwargs)
#         self.db = Database()
#         # self.update_income_display()
       
#     def add_income(self):
#         amount = self.ids.amount_input.text
#         date = self.ids.date_input.text
#         serialnr = self.ids.serialnr_input.text
#         if serialnr == '':
#             serialnr = None
#         self.db.record_income(amount, date, serialnr)
#         self.update_income_display()
#         self.clear_input()

#     def update_income_display(self):
#         incomes = self.db.get_incomes()
#         incomes_text = '\n'.join(str(income) for income in incomes)
#         self.ids.incomes_label.text = incomes_text

#     def clear_input(self):
#         self.ids.amount_input.text = ''
#         self.ids.date_input.text = ''
#         self.ids.serialnr_input.text = ''

#     def nuke(self):
#         self.db.nuke_db()

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
