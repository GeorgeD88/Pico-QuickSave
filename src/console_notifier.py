class ConsoleNotifier:
    """ Notifier class that allows the app to trigger system notifications. """

    def __init__(self):
        # Don't need any code here anymore, but I kept the start_notifier
        self.start_notifier()

    def start_notifier(self):
        """ Prints to the console that QuickSave is up and running. """
        # ! This is not needed anymore, but it used to be necessary for the other notifiers,
        # ! such as RasPi notifier (w/ leds). Leaving the code here for the future
        # ! because it might become necessary again when we implement the hardware.
        print('Spotify-QuickSave is up and running!')

    def trigger_song_saved_indicator(self, track_name: str = None):
        """ Prints to the console that a song was saved. """
        if track_name is None:
            print('Currently playing track was saved')
        else:
            print('Track saved:', track_name)

    def trigger_duplicate_song_warning(self):
        """ Prints a warning to the console that a duplicate song
            was attempted to be added. """
        print('Duplicate track: track is already in your playlist, press [Undo] to remove it')

    def trigger_max_undo_warning(self):
        """ Prints a warning to the console that only one undo is allowed per save. """
        print('Max undo: you cannot undo more than once in a row')

    def trigger_custom_notification(self, message: str):
        """ Prints the given message to the console. """
        print(message)
