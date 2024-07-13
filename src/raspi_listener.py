# Raspberry Pi
from picozero import Button
from signal import pause  # from regular Pi, TODO: check if Pico uses the same

# Constants
from actions import TOGGLE_LIKE, SAVE_MAIN, SAVE_OTHER, UNDO_SAVE, QUIT_APP

""" NOTE: Pulled from the OG QuickSave. I'm going to convert this to work with the Pico,
    as well as add functions or refactor as needed. """

class RasPiListener:

    def __init__(self, button_callback, gpio_pins: dict):

        self.callback = button_callback

        # Set GPIO pin numbers
        self.toggle_like_button = Button(gpio_pins['button_save_lib'])
        self.save_main_button = Button(gpio_pins['button_save_main'])
        self.save_other_button = Button(gpio_pins['button_save_other'])
        self.undo_last_button = Button(gpio_pins['button_undo_save'])

        # Map the buttons to the actions
        self.toggle_like_button.when_pressed = self.toggle_like
        self.save_main_button.when_pressed = self.save_main
        self.save_other_button.when_pressed = self.save_other
        self.undo_last_button.when_pressed = self.undo_last

    def start_listener(self):
        """ Starts the listener by waiting for signals. """
        print('start saving! 🎧🥧\n')
        pause()  # Tells the RasPi to wait for signals (from buttons)

    def stop_listener(self):
        """ Placeholder because the parent component has to call this function to work. """
        print('thanks for stopping by! hopefully I was helpful :)')

    def toggle_like(self):
        self.callback(TOGGLE_LIKE)

    def save_main(self):
        self.callback(SAVE_MAIN)

    def save_other(self):
        self.callback(SAVE_OTHER)

    def undo_last(self):
        self.callback(UNDO_SAVE)
