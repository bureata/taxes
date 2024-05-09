# Simple Tax Calculator for Romanian Self-Employed Individuals (PFA) - 2024

## Overview
This app is intended to be a very simple tool for income and expense visualization and basic tax calculation.  
Since it doesn't include complex VAT features besides marking expenses as VAT generators (for international purchases), this app is only suitable for the Self-Employed Individuals that don't collect VAT.

It's an app developed for the purpose of learning the basics of Kivy (https://kivy.org/).

#### Note: You will notice a "Reload" button at the bottom of the window that restarts the app when pressed. Its function is to facilitate quick reloading of the app whenever code changes are made during development.

## Functionality
### Note: Some functionalities may not be implemented yet.

- record income
    - edit income
    - delete income
- record expense
    - edit expense
    - delete expense
- attach a file to each income or expense
- display the incomes and expenses in a list format
- generate and display a tax report

The data is saved in a sqlite3 file named "tax.db".

## Requirements

- Python 3
- Kivy 2.3.0

## Running the app

- create a virtual environment AND ACTIVATE IT
- install Kivy
    - for both steps above you can find OS specific instructions on the kivy docs page: https://kivy.org/doc/stable/gettingstarted/installation.html
- clone the repository
- run the app from command line (with the virtual environment activated)  
    `$ python3 tax.py (or just 'python' for windows)`

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.