from spotify_client import SpotifyClient
import token_cache_handler as cache
import ujson

# Constants
IS_DUPE = "IS_DUPLICATE"  # Status code for duplicate track
CONFIG = "config.json"


class QuickSaveController:
    """ Controller that handles the main quick saving functionality of the app (backend). """

    def __init__(self, main_playlist_id: str, other_playlist_id: str, notifier, logger):
        """
        Args:
            main_playlist_id (str): The main playlist to quick save tracks to.
            other_playlist_id (str): The playlist for tracks that do not belong in the main playlist.
        """

        # TODO: organize/group all the class variables better
        self.client = SpotifyClient(notifier, logger)
        self.main_playlist_id = main_playlist_id
        self.other_playlist_id = other_playlist_id

        # Keep local record of playlist contents to avoid adding duplicate songs
        self.main_plist_tracks = set(self.client.get_playlist_tracks(main_playlist_id))
        self.other_plist_tracks = set(self.client.get_playlist_tracks(other_playlist_id))

        # Holds the last saved track and its playlist in a tuple (track_id, playlist_id)
        self.last_save = None

    def toggle_like(self) -> tuple[str, bool]:
        """ Toggles currently playing track's library save (likes/unlikes track).

        Returns:
            tuple[str, bool]: Returns the ID of the currently playing track, and whether it's saved now.
        """

        track_id = self.client.get_currently_playing(self.api_tokens)

        # Terminate the function if no track is currently playing
        if track_id is None:
            return None

        # Check if the track is saved to the library
        is_saved = self.client.is_track_saved(self.api_tokens, track_id)

        # Toggle the track's "liked" status
        if is_saved:
            self.client.remove_track(self.api_tokens, track_id)
        else:
            self.client.save_track(self.api_tokens, track_id)

        return track_id, not is_saved

    def quick_save(self, playlist_id: str) -> str:
        """ Quick saves currently playing track to given playlist and user library, and stores details in last save. """

        # Get the currently playing track
        track_id = self.client.get_currently_playing(self.api_tokens)

        # Terminate the function if no track is currently playing
        if track_id is None:
            return None

        # Record the saved track and its corresponding playlist in last_save
        self.last_save = (track_id, playlist_id)

        # Save the track to the library (likes song)
        self.client.save_track(self.api_tokens, track_id)

        # Get the reference to the respective playlist's local track list
        playlist_tracks = self.get_local_track_list(playlist_id)

        # Terminate the function if the track is already in the playlist (duplicate track)
        if track_id in playlist_tracks:
            return IS_DUPE

        # Add the track to the Spotify playlist and the local track list
        self.client.add_to_playlist(self.api_tokens, playlist_id, track_id)
        playlist_tracks.add(track_id)

        return self.last_save

    def undo_last_save(self) -> tuple[str, str]:
        """ Undoes last quick save by removing the track from the playlist and user library. """

        # Check if the last save exists before attempting to undo it
        if self.last_save is None:
            return None

        # Get the last save details and update the last save to None
        (track_id, playlist_id), self.last_save = self.last_save, None

        # Remove the track from the user's library, the playlist, and the local track list
        self.client.remove_track(self.api_tokens, track_id)
        self.client.remove_from_playlist(self.api_tokens, playlist_id, track_id)
        self.get_local_track_list(playlist_id).remove(track_id)

        return track_id, playlist_id

    def get_local_track_list(self, playlist_id: str) -> set[str]:
        """ Gets the corresponding local track list based on the given playlist ID. """
        return self.main_plist_tracks if playlist_id is self.main_playlist_id else self.other_plist_tracks
