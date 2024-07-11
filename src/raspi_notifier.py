# Raspberry Pi
from picozero import LED
from signal import pause
from time import sleep

DURATION = 1  # Duration for standard indicators and warnings


""" NOTE: Pulled from the OG QuickSave. I'm going to convert this to work with the Pico,
    as well as add functions or refactor as needed. """

class RasPiNotifier:
    """ RasPi notifier class that allows the app to trigger LED responses on the Pi. """

    def __init__(self, gpio_pins: dict):
        # Set GPIO pin numbers
        self.success_led = gpio_pins['led_success']
        self.alert_led = gpio_pins['led_alert']
        self.error_led = gpio_pins['led_error']

        # FIXME: maybe move the red (error) LED uses to yellow (alert) LED and then red is for app errors, like FileNotFound

    def start_notifier(self):
        """ Starts the notifier by waiting for signals. """
        self.trigger_ready_lights()
        pause()  # signal pause for RasPi to wait for inputs

    def flash_led(self, triggering_led: LED, duration: int):
        """ Triggers the given LED to flash for the specified duration. """
        # TODO: check if the following is the most efficient way to do this,
        # * or if there's a function for this
        triggering_led.on()
        sleep(duration)
        triggering_led.off()

    def trigger_song_saved_indicator(self, duration: int = DURATION):
        """ Flashes the success LED to indicate that a song was saved. """
        self.flash_led(self.success_led, duration)

    def trigger_duplicate_song_warning(self, duration: int = DURATION):
        """ Flashes the alert LED to warn that a duplicate song was attempted to be added. """
        self.flash_led(self.error_led, duration)

    def trigger_max_undo_warning(self, duration: int = DURATION):
        """ Flashes the alert LED to warn that only one undo is allowed per save. """
        self.flash_led(self.error_led, duration)

    def trigger_os_error(self, duration: int = DURATION):
        """ Flashes the error LED repeatedly to indicate an OS error was received. """
        # TODO: flash the error LED 4 times (total 1 sec)
        # Time for each individual flash (maybe for strictly the on time, or for the total on/off time)
        flash_time = None #0.25
        # flash as many times needed for given duration
        for _ in range(duration // flash_time):  # FIXME: maybe 'ceiling' the number instead of floor??
        # because floor might reduce the number a lot if duration and/or flash time are small
            self.flash_led(self.error_led, flash_time)
            sleep(0)  # TODO

    def trigger_unexpected_os_error(self, duration: int = DURATION):
        """ Flashes the __ to indicate an unexpected OS error was received. """
        pass

    def trigger_critical_error(self, duration: int = DURATION):
        """ Triggers a sequence w/ all LEDs to indicate a critical error and program shutdown. """
        # TODO idea: do the same flash as file_not_found_error but with all the LEDs,
        # and then hold them on for half a sec or something.
        # most importantly flash them a few times and then hold them

        # Flash all the LEDs repeatedly for half the duration

        # Hold all the LEDs on for half the duration
        self.error_led.on()
        self.alert_led.on()
        self.success_led.on()
        sleep(duration/2)
        self.error_led.off()
        self.alert_led.off()
        self.success_led.off()

    def trigger_ready_lights(self, duration: int = 1.5, blink_time=0.1):
        """ Triggers a sequence w/ all LEDs to indicate that the app is ready. """
        self.success_led.blink(on_time=blink_time, off_time=blink_time)
        sleep(blink_time)
        self.duplicate_led.blink(on_time=blink_time, off_time=blink_time)
        sleep(duration-blink_time)
        self.success_led.off()
        self.duplicate_led.off()
        # TODO: will need to include the 3rd light I want to add
