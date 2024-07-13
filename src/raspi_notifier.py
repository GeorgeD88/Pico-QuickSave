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
        self.success_led = LED(gpio_pins['led_success'])
        self.alert_led = LED(gpio_pins['led_alert'])
        self.error_led = LED(gpio_pins['led_error'])

        # FIXME: maybe move the red (error) LED uses to yellow (alert) LED and then red is for app errors, like FileNotFound

    def start_notifier(self):
        """ Starts the notifier by waiting for signals. """
        self.trigger_ready_lights()
        pause()  # signal pause for RasPi to wait for inputs

    def _flash_led(self, flashing_led: LED, duration: float):
        """ Flashes the given LED for the specified duration. """
        # TODO: check if the following is the most efficient way to do this,
        # * or if there's a function for this
        flashing_led.on()
        sleep(duration)
        flashing_led.off()

    def _quick_flash_led_repeatedly(self, flashing_led: LED, flash_count: int,
                                    flash_speed: float = 0.126):
                                    # 0.115 is very good for looking quick
        """ Repeatedly flashes the given LED for the specified number of times. """
        for _ in range(flash_count-1):
            self._flash_led(flashing_led, flash_speed)
            sleep(flash_speed)  # Flashes off for the same time
        self._flash_led(flashing_led, flash_speed)


    def trigger_song_saved_success(self, duration: float = DURATION):
        """ Flashes the success LED to indicate that a song was saved. """
        self._flash_led(self.success_led, duration)

    def trigger_duplicate_song_warning(self, duration: float = DURATION):
        """ Flashes the alert LED to warn that a duplicate song was attempted to be added. """
        self._flash_led(self.alert_led, duration)

    def trigger_max_undo_warning(self, duration: float = DURATION):
        """ Flashes the alert LED to warn that only one undo is allowed per save. """
        self._flash_led(self.alert_led, duration)

    def trigger_os_error(self):
        """ Flashes the error LED repeatedly to indicate an OS error was received. """
        # TODO: flash the error LED 4 times (total 1 sec)
        # Time for each individual flash (maybe for strictly the on time, or for the total on/off time)
        # ?flash_time = None #0.25
        # flash as many times needed for given duration
        # ?for _ in range(duration // flash_time):  # FIXME: maybe 'ceiling' the number instead of floor??
        # because floor might reduce the number a lot if duration and/or flash time are small
            # ?self._flash_led(self.error_led, flash_time)
            # ?sleep(0)  # TODO
        self.self._quick_flash_led_repeatedly(self.error_led, 4)

    def trigger_unexpected_os_error(self, duration: float = DURATION):
        """ Flashes the __ to indicate an unexpected OS error was received. """
        pass

    def trigger_critical_error(self):
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

    def trigger_wifi_connecting_status(self, flash_speed: float = 0.09):
        """ Triggers a single wave animation w/ all LEDs (that can be called repeatedly)
            to indicate that the device is connecting to Wi-Fi. """
        self.success_led.on()
        sleep(flash_speed)
        self.alert_led.on()
        self.success_led.off()
        sleep(flash_speed)
        self.error_led.on()
        self.alert_led.off()
        sleep(flash_speed)
        self.error_led.off()

    def trigger_wifi_connection_failed(self):
        """ Flashes the error LED repeatedly to indicate the Wi-Fi failed to connect. """
        self._quick_flash_led_repeatedly(self.error_led, 3)

    def trigger_ready_lights(self, blink_count: int = 6, blink_time: float = 0.1):
        """ Triggers a sequence w/ all LEDs to indicate that the app is ready. """

        # Initiate blinking of the success and error LEDs
        self.success_led.blink(on_time=blink_time)
        self.error_led.blink(on_time=blink_time)

       # Let the LEDs blink once, then start blinking the alert LED
        sleep(blink_time)
        self.alert_led.blink(on_time=blink_time)

        # Let the sequence continue for the remaining blink count, then turn off all LEDs
        sleep(blink_time*(blink_count-1))
        self.success_led.off()
        self.error_led.off()
        self.alert_led.off()
