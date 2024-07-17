from picozero import Button
from machine import Pin

from actions import TOGGLE_LIKE, SAVE_MAIN, SAVE_OTHER, UNDO_SAVE, QUIT_APP

""" NOTE: Pulled from the OG QuickSave. I'm going to convert this to work with the Pico,
    as well as add functions or refactor as needed. """


class RasPiListener:

    def __init__(self, button_callback, gpio_pins: dict):

        self.callback = button_callback

        # Initialize GPIO pins
        self.toggle_like_button = Pin(gpio_pins['button_toggle_like'], Pin.IN, Pin.PULL_UP)
        self.save_main_button = Pin(gpio_pins['button_save_main'], Pin.IN, Pin.PULL_UP)
        self.save_other_button = Pin(gpio_pins['button_save_other'], Pin.IN, Pin.PULL_UP)
        self.undo_save_button = Pin(gpio_pins['button_undo_save'], Pin.IN, Pin.PULL_UP)

        # Set up the buttons' triggers and handlers (callback)
        self.toggle_like_button.irq(trigger=Pin.IRQ_FALLING, handler=self.toggle_like)
        self.save_main_button.irq(trigger=Pin.IRQ_FALLING, handler=self.save_main)
        self.save_other_button.irq(trigger=Pin.IRQ_FALLING, handler=self.save_other)
        self.undo_save_button.irq(trigger=Pin.IRQ_FALLING, handler=self.undo_save)
        # TODO: wiggling buttons triggers multiple times. maybe add bounce back or something?

    def start_listener(self):
        """ Starts the listener by waiting for signals. """
        print('start saving! 🎧🥧\n')
        # TODO: refactor to use interrupts, because micro python can't signal.pause

    def stop_listener(self):
        """ Placeholder because the parent component has to call this function to work. """
        print('thanks for stopping by! hopefully I was helpful :)')

    def toggle_like(self, pin):
        self.callback(TOGGLE_LIKE)

    def save_main(self, pin):
        self.callback(SAVE_MAIN)

    def save_other(self, pin):
        self.callback(SAVE_OTHER)

    def undo_save(self, pin):
        self.callback(UNDO_SAVE)
