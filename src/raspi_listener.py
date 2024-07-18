from machine import Pin
import time

from actions import TOGGLE_LIKE, SAVE_MAIN, SAVE_OTHER, UNDO_SAVE, QUIT_APP


class Button:

    def __init__(self, pin: int, callback):
        # Define the callback and debounce variables
        self.callback = callback
        self.debounce_time = 300  # 300 milliseconds debounce time
        self.last_press_time = 0

        # Set up the button pin and interrupt request (IRQ)
        self.pin = Pin(pin, Pin.IN, Pin.PULL_UP)
        self.pin.irq(trigger=Pin.IRQ_FALLING, handler=self.handle_interrupt)

    def is_pressed(self):
        """ Checks if the button press is valid based on debounce time. """
        current_time = time.ticks_ms()
        if time.ticks_diff(current_time, self.last_press_time) > self.debounce_time:
            self.last_press_time = current_time
            return True
        return False

    def handle_interrupt(self, pin):
        """ Triggers the callback only if the button press is valid based on debounce time. """
        if self.is_pressed():
            self.callback()


class RasPiListener:

    def __init__(self, button_callback, gpio_pins: dict):
        self.callback = button_callback

        # Initialize buttons and map actions
        self.toggle_like_button = Button(gpio_pins['button_toggle_like'], self.toggle_like)
        self.save_main_button = Button(gpio_pins['button_save_main'], self.save_main)
        self.save_other_button = Button(gpio_pins['button_save_other'], self.save_other)
        self.undo_save_button = Button(gpio_pins['button_undo_save'], self.undo_save)

    def toggle_like(self):
        self.callback(TOGGLE_LIKE)

    def save_main(self):
        self.callback(SAVE_MAIN)

    def save_other(self):
        self.callback(SAVE_OTHER)

    def undo_save(self):
        self.callback(UNDO_SAVE)
