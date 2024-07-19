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

        # TODO: improve the multiple calls to config by only loading it once

        # Set the playlist IDs
        plist_ids = config.get_playlist_ids()
        self.main_playlist_id = plist_ids['main_playlist']
        self.other_playlist_id = plist_ids['other_playlist']

        # Initialize all components of the QuickSaver application
        print('initializing input listener, controller, and notifier...')
        self.input_listener = RasPiListener(self.process_input,
                                            config.get_gpio_pin_numbers())
        self.notifier = RasPiNotifier(config.get_gpio_pin_numbers())
        self.logger = Logger(config.get_log_filename(), to_console=True)
        self.controller = QuickSaveController(self.main_playlist_id, self.other_playlist_id,
                                              self.notifier, self.logger, self.stop_quicksaver)

    def start_quicksaver(self):
        """ Starts running QuickSaver by starting the Spotify token refresh loop. """
        self.notifier.trigger_ready_lights()
        # TODO: start spotify_client refreshing loop (prevents the program from closing)
        self.logger.info('QuickSaver is ready, starting Spotify access token refresh loop')
        self.controller.start_access_token_refresh_loop()

    def stop_quicksaver(self):
        # NOTE: we can't really trigger this or run it when unplugging, but we'll still keep the code here
        # maybe we can figure out how to trigger this by holding multiple buttons down
        self.log_quitting_app()
        # TODO: figure out what cleanup needs to be done
        # TODO: stop SpotifyClient token refreshing loop
        # LEDs signalling quicksaver stopping
        self.notifier.clean_up_leds()
        self.logger.close()

    def toggle_like(self) -> tuple[str, bool]:
        """ Toggles the currently playing track's library save (likes/unlikes track). """

        # Toggle like of currently playing track and save result
        result = self.controller.toggle_like()

        # Terminate function if there was no track currently playing
        if result is None:
            self.log_no_track_playing(TOGGLE_LIKE)
            self.notifier.trigger_no_song_playing_warning()
            return None

        # Since result isn't None, it's a tuple of the track ID and like status
        track_id, like_status = result

        # Song was successfully liked/saved to library after toggling
        if like_status is True:
            self.notifier.trigger_song_saved_success()
        # Song was successfully unliked/removed from library after toggling
        else:
            self.notifier.trigger_song_unlike_success()

        self.log_toggle_like_success(track_id, like_status)

        return result

    def quick_save(self, playlist_id: str) -> tuple[str, str]:
        """ Quick saves currently playing track to given playlist and user library. """

        # Quick save currently playing track and save result
        result = self.controller.quick_save(playlist_id)

        # Terminate function if there was no track currently playing
        if result is None:
            self.log_no_track_playing(self.get_playlist_action(playlist_id))
            self.notifier.trigger_no_song_playing_warning()
            return None

        # Result contains the track_id with either the IS_DUPE status or playlist_id
        track_id, dupe_status = result

        # Trigger a duplicate song warning if the track is already in the playlist
        if dupe_status is IS_DUPE:
            self.log_duplicate_song_attempt(track_id, playlist_id)
            self.notifier.trigger_duplicate_song_warning()
            return None
        # Song was successfully saved
        else:
            self.log_quicksave_success(track_id, playlist_id)
            self.notifier.trigger_song_saved_success()

        return result

    def undo_last_save(self) -> tuple[str, str]:
        """ Undoes last quick save by removing the track from the playlist and user library. """

        # Undo last quick saved track and save result
        result = self.controller.undo_last_save()

        # Terminate function if there was no last save to undo
        if result is None:
            self.log_max_undo_attempt()
            self.notifier.trigger_max_undo_warning()
            return None

        # Otherwise log and notify the successful undo
        self.log_undo_success(*result)
        self.notifier.trigger_undo_save_success()

        return result

    def process_input(self, button_pressed: str):
        """ Executes the corresponding action based on the callback received. """

        # Saves only to user's library (likes track)
        if button_pressed is TOGGLE_LIKE:
            result = self.toggle_like()[1]  # Whether track was saved/removed
        # Quick saves to the main playlist
        elif button_pressed is SAVE_MAIN:
            result = self.quick_save(self.main_playlist_id)
        # Quick saves to the other playlist
        elif button_pressed is SAVE_OTHER:
            result = self.quick_save(self.other_playlist_id)
        # Undoes the last quick save
        elif button_pressed is UNDO_SAVE:
            result = self.undo_last_save()
        # Quits the app
        elif button_pressed is QUIT_APP:
            self.stop_quicksaver()

    def get_playlist_action(self, playlist_id: str) -> str:
        """ Gets the corresponding playlist label (Main/Other) based on the given playlist ID. """
        return SAVE_MAIN if playlist_id is self.main_playlist_id else SAVE_OTHER

    def get_playlist_label(self, playlist_id: str) -> str:
        """ Gets the corresponding playlist label (Main/Other) based on the given playlist ID. """
        return self.get_playlist_action(playlist_id)[5:]

    def log_toggle_like_success(self, track_id: str, like_status: bool):
        like_string = 'SAVED' if like_status is True else 'UNSAVED'
        self.logger.info(f'Successfully toggled like of track <{track_id}> to <{like_string}>')

    def log_quicksave_success(self, track_id: str, playlist_id: str):
        playlist_label = self.get_playlist_label(playlist_id)
        self.logger.info(f'Successfully QuickSaved track <{track_id}> to playlist <{playlist_id}> ({playlist_label} playlist)')

    def log_undo_success(self, track_id: str, playlist_id: str):
        playlist_label = self.get_playlist_label(playlist_id)[5:]
        self.logger.info(f'Successfully undid save of track <{track_id}> from playlist <{playlist_id}> ({playlist_label} playlist)')

    def log_no_track_playing(self, attempted_action: str):
        self.logger.info(f'No track is currently playing, the following action was attempted <{attempted_action}>')

    def log_duplicate_song_attempt(self, track_id: str, playlist_id: str):
        playlist_label = self.get_playlist_label(playlist_id)[5:]
        self.logger.info(f'Duplicate track attempted to be added, track <{track_id}> to playlist <{playlist_id}> ({playlist_label} playlist)')

    def log_max_undo_attempt(self):
        self.logger.info('Undo last saved track attempted, max undo warning')

    def log_quitting_app(self):
        self.logger.info('Quitting QuickSaver app')
