from quicksave_controller import QuickSaveController, IS_DUPE
import utils

# Constants
from actions import TOGGLE_LIKE, SAVE_MAIN, SAVE_OTHER, UNDO_SAVE, QUIT_APP
EXPORT_FILENAME = "session_exports"


class QuickSaver:
    """ The main central component that connects all the components together that make the app.  """

    def __init__(self, input_listener, notifier, main_playlist_id: str, other_playlist_id: str):

        # Initializes the separate components
        print('initializing input listener, controller, and notifier...')
        self.input_listener = input_listener(self.process_input)  # Frontend
        self.notifier = notifier()  # Triggers notifiers/responses (such as notifications/LEDs)
        self.controller = QuickSaveController(main_playlist_id, other_playlist_id)  # Backend

        # Playlist IDs
        self.main_playlist_id = main_playlist_id
        self.other_playlist_id = other_playlist_id

        # Get references to local record of playlist contents from QuickSaver controller
        self.main_plist_tracks = self.controller.main_plist_tracks
        self.other_plist_tracks = self.controller.other_plist_tracks

    def start_quicksaver(self):
        """ Starts running QuickSaver by starting
            the input listener and notifier loops. """
        # Start input listener and notifier
        self.input_listener.start_listener()
        # TODO: start notifier as well
        # TODO: start spotify_client refreshing loop (this is what will keep the program was closing)
        # self.controller.start_refresh_smthn

    # === Quick Saving ===
    def toggle_like(self) -> tuple[str, str]:
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

        # NOTE: if the value of last_save was a duplicate, then it wasn't actually added and is only there to give the user
        # A chance to remove it. that's why we have to check if the track is in the log before attempting to remove it.

        # Removes last added track from respective playlist log if it's not empty and matches the removed track
        track_list = self.get_local_track_list(result[1])
        # FIXME: Check this line if you're having problems, it was switched from track log
        if len(track_list) > 0 and result[0] in track_list:
            track_list.remove(result[0])

        return result

    # === Input Listener ===
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

    # === Helpers ===
    def get_local_track_list(self, playlist_id: str) -> set[str]:
        """ Gets the corresponding local track list based on the given playlist ID. """
        return self.main_plist_tracks if playlist_id is self.main_playlist_id else self.other_plist_tracks
