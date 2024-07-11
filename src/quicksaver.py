from quicksave_controller import QuickSaveController, IS_DUPE
from raspi_listener import RasPiListener
from raspi_notifier import RasPiNotifier
import config_handler as config
from logger import Logger
import utils

# Constants
from actions import TOGGLE_LIKE, SAVE_MAIN, SAVE_OTHER, UNDO_SAVE, QUIT_APP
EXPORT_FILENAME = "session_exports"


class QuickSaver:
    """ The main central component that connects all the components together that make the app.  """

    def __init__(self):

        # Initialize all components of the QuickSaver application
        print('initializing input listener, controller, and notifier...')
        self.input_listener = RasPiListener(self.process_input,
                                            config.get_gpio_pin_numbers())
        self.notifier = RasPiNotifier(config.get_gpio_pin_numbers())
        self.logger = Logger(config.get_log_filename())
        self.controller = QuickSaveController(main_playlist_id, other_playlist_id,
                                              self.notifier, self.logger)

        # Set the playlist IDs
        plist_ids = config.get_playlist_ids()
        self.main_playlist_id = plist_ids['main_playlist']
        self.other_playlist_id = plist_ids['other_playlist']

    def start_quicksaver(self):
        """ Starts running QuickSaver by starting
            the input listener and notifier loops. """
        # Start input listener and notifier
        self.input_listener.start_listener()
        self.notifier.start_notifier()
        # TODO: start spotify_client refreshing loop (prevents the program from closing)
        # self.controller.start_refresh_smthn

    def toggle_like(self) -> tuple[str, bool]:
        """ Toggles the currently playing track's library save (likes/unlikes track). """

        # Toggle like of currently playing track and save result
        result = self.controller.toggle_like()

        # Terminate function if there was no track currently playing
        if result is None:
            return None
        # Triggers notif if song was liked/saved
        elif result[1] is True:
            self.notifier.trigger_song_saved_indicator()

        return result

    def quick_save(self, playlist_id: str) -> tuple[str, str]:
        """ Quick saves currently playing track to given playlist and user library. """

        # Quick save currently playing track and save result
        result = self.controller.quick_save(playlist_id)

        # Terminate function if there was no track currently playing
        if result is None:
            return None
        # Triggers duplicate song warning notif and terminates function if the track is already in the playlist
        elif result is IS_DUPE:
            self.notifier.trigger_duplicate_song_warning()
            return None
        # Song was successfully saved
        else:
            self.notifier.trigger_song_saved_indicator()

        return result

    def undo_last_save(self) -> tuple[str, str]:
        """ Undoes last quick save by removing the track from the playlist and user library. """

        # Undo last quick saved track and save result
        result = self.controller.undo_last_save()

        # Terminate function if there was no last save to undo
        if result is None:
            self.notifier.trigger_max_undo_warning()
            return None

        return result

    def process_input(self, button_pressed: str):
        """ Executes the corresponding action based on the callback received. """

        # Saves only to user's library (likes track)
        if button_pressed is TOGGLE_LIKE:
            result = self.toggle_like()[1]  # whether track was saved/removed
            print('saved track to library' if result is True else 'removed track from library')
        # Quick saves to the main playlist
        elif button_pressed is SAVE_MAIN:
            result = self.quick_save(self.main_playlist_id)
            if result is not None:
                print('quick saved to main playlist')
        # Quick saves to the other playlist
        elif button_pressed is SAVE_OTHER:
            result = self.quick_save(self.other_playlist_id)
            if result is not None:
                print('quick saved to other playlist')
        # Undoes the last quick save
        elif button_pressed is UNDO_SAVE:
            result = self.undo_last_save()
            if result is not None:
                print('undid last quick save')
        # Quits the app
        elif button_pressed is QUIT_APP:
            print('quitting app')
            self.input_listener.stop_listener()

    def get_local_track_list(self, playlist_id: str) -> set[str]:
        """ Gets the corresponding local track list based on the given playlist ID. """
        return self.main_plist_tracks if playlist_id is self.main_playlist_id else self.other_plist_tracks
