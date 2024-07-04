# Raspberry Pi
from picozero import LED
from signal import pause
from time import sleep

DURATION = 1  # Duration for standard indicators and warnings


""" NOTE: Pulled from the OG QuickSave. I'm going to convert this to work with the Pico,
    as well as add functions or refactor as needed. """

class RasPiNotifier:
    """ RasPi notifier class that allows the app to trigger LED responses on the Pi. """

    def __init__(self):
        # Set GPIO pin numbers
        self.success_led = LED(16)  # Green
        self.warning_led = LED(20)  # Yellow
        # ! I want to add that yellow LED to provide more detail and because there's room
        # currently it's still just green and red LED, but later I can add more info using the yellow LED.
        # NOTE: maybe move the red LED uses to yellow LED and then red is for app errors, like FileNotFound
        self.error_led = LED(20)    # Red

    def start_notifier(self):
        """ Starts the notifier by waiting for signals. """
        self.trigger_ready_lights()
        pause()  # signal pause for RasPi to wait for inputs

    def trigger_led(self, triggering_led: LED, duration: int):
        """ Triggers the given LED to flash for the specified duration. """
        # TODO: check if the following is the most efficient way to do this,
        # * or if there's a function for this
        triggering_led.on()
        sleep(duration)
        triggering_led.off()

    # TODO: we need to write functions for app errors and stuff, like for FileNotFoundError

    def trigger_song_saved_indicator(self, duration: int = DURATION):
        """ Flashes the success LED to indicate that a song was saved. """
        self.trigger_led(self.success_led, duration)

    def trigger_duplicate_song_warning(self, duration: int = DURATION):
        """ Flashes the __ LED to warn that a duplicate song was attempted to be added. """
        self.trigger_led(self.error_led, duration)

    def trigger_max_undo_warning(self, duration: int = DURATION):
        """ Triggers a red LED flash to warn that only one undo is allowed per save. """
        self.trigger_led(self.error_led, duration)

    def trigger_ready_lights(self, duration: int = 1.5, blink_time=0.1):
        self.success_led.blink(on_time=blink_time, off_time=blink_time)
        sleep(blink_time)
        self.duplicate_led.blink(on_time=blink_time, off_time=blink_time)
        sleep(duration-blink_time)
        self.success_led.off()
        self.duplicate_led.off()
