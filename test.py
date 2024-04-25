from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.event import EventDispatcher

# Define a custom widget that contains an EventDispatcher
class CustomEventDispatcher(EventDispatcher, BoxLayout):
    message = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type('on_button_click')

    def update_message(self, new_message):
        self.message = new_message

    # Define a method to be triggered by the button click
    def custom_method(self):
        self.update_message("Button clicked!")
        self.dispatch('on_button_click')

# Define another custom widget
class AnotherWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    # Define a method that will be triggered by a button click
    def another_custom_method(self, *args):
        custom_widget_instance.update_message("Button in AnotherWidget clicked!")

# Load the kv file
Builder.load_string('''
<CustomEventDispatcher>:
    orientation: 'vertical'
    Label:
        text: root.message
    Button:
        text: 'Click Me'
        on_release: root.custom_method()
''')

# Create an instance of CustomEventDispatcher
custom_widget_instance = CustomEventDispatcher()

# Create an instance of AnotherWidget
another_widget_instance = AnotherWidget()

# Bind the custom method of AnotherWidget to the on_button_click event of CustomEventDispatcher
custom_widget_instance.bind(on_button_click=another_widget_instance.another_custom_method)

# Define the app
class MyApp(App):
    def build(self):
        return custom_widget_instance

if __name__ == '__main__':
    MyApp().run()
