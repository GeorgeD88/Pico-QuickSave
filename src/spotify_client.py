# Standard library imports: built-in Python modules
pass

# Third-party imports: installed separately
pass

# Local application specific imports: specific to your application
pass

# TODO: organize the below imports into the categories above
from micropython import const, mem_info
import token_cache_handler as cache
import config_handler as config
import uasyncio as asyncio
from machine import Pin
import spotify_api
import network
import ujson
import errno
import time
import gc
# import Tiny-JSON; this is also available if needed for whatever reason

REFRESH_INTERVAL = 20 * 60  # Refresh tokens every 20 minutes (1200 seconds)
RETRY_INTERVAL = 10 * 60  # Retries refreshing every 10 minutes (600 seconds)
SCOPES = [
    "user-read-playback-state",     # Get current playback
    "user-read-currently-playing",  # Get current user playing track
    "user-library-read",            # Check user's saved tracks (user library)
    "user-library-modify",          # Add/remove saved tracks (user library)
    "playlist-read-private",        # Read user's private playlists
    "playlist-modify-public",       # Add/remove user playlist tracks
    "playlist-modify-private"       # Add/remove user playlist tracks
]

"""
TODO: What we're going to do is use the guy's Spotify API and Spotify files.
This file will be a wrapper to clean up the complexity of the Spotify API,
and the way I need to do it is by copying the exact usage in spotify.py,
which for the original developer is actually the main file where his thing operated
(meaning it included the screen code there too).

creds = {"client_id": "30772e8117e044d4b5b3806b78a55724","client_secret": "ee09bfd69a484a1bb5a4cd1db62121cf","redirect_uri": "http://localhost:8888/callback"}
tokens = {"refresh_token": "AQC7SGjscCIOdzLgbUkHPkjVB4IeD5z1zjqyWnTuY5_r_dqMIZ8ZZrl4Eqn4PtglRBmLwlYK6DxtZyRZEbKldjaQG9ZooArZisF_IknxIOItZpNRw-NpBXNOr7LBa-jLVWQ"}
refresh_access_token(tokens, creds['client_id'], creds['client_secret'])
tokens = {'access_token': 'BQBr902s5WTPROwUYHhklYr6AMN1s-dZy1lSSiWNFHPkOLN7c6QdW7PoC-n41j2ebaW23nymAC7D_35gQcJy7u7Gk4UZciI99NQST5aR1VpEkkvu5QUORDazW67qrTTVr1xG0KF2b2vrakRZNkL9xaFEkzmjW2rSioix5zitHq9g0hzd46CtsVxmJNAvibJEsnSJXKdqcL2nfa-cJrPN19P8K8o9YP4v9PoohniVzgKDIXCWbWqN34KrRuraTe2nLcBZ6Wt5qc2Vgn8y-eD2ezaL9wq-xfY'}
playlist_id, track_id = '4FwqKchnDzE9kK5ATaj7kk', '4MDdpjdcb3sRfeGGZ5qYEx'

TODO: we have to figure out how to check for token expiration and automatically refresh and replace.

* something different from how I usually make the spotify client file is that we have to
handle the refreshing access token and such because we're not using a wrapper like Spotipy.
"""

class SpotifyClient:

    def __init__(self, notifier, logger):
        self._load_cache_tokens()
        self._load_api_creds()
        self.notifier = notifier
        self.logger = logger
        # self._refresh_access_token()  # Make initial refresh of access tokens

    def _load_cache_tokens(self):
        """ Loads the access and refresh tokens from the cache file. """
        cache_tokens = self._except_os_error(cache.get_token_cache)
        self.api_tokens = {
            'access_token': cache_tokens['access_token'],
          'refresh_token': cache_tokens['refresh_token']
        }

    def _load_api_creds(self):
        """ Loads the Spotify API credentials from the config file. """
        config_file = self._except_os_error(config.get_spotify_creds)
        self.client_id = config_file['client_id']
        self.client_secret = config_file['client_secret']
        self.redirect_uri = config_file['redirect_uri']

    def _except_os_error(self, try_func):
        """ Tries to run the given the function while catching OS errors. """
        try:
            return try_func()
        except OSError as e:
            # FIXME: probably add time to print statements, '[XX:XX:XX] error received'
            print(f'[{errno.errorcode[e.errno]}] error received, handling accordingly...')
            # Handle FileNotFoundError
            if e.errno == errno.ENOENT:
                self._handle_enoent_error(e)
            # elif, TODO: OSError: -6
            # e.errno == -6, seems to always be no wifi error

            # elif, [error 12] ENOMEM (memory error)

            # Unexpected error
            else:
                self._handle_unexpected_error(e)

    # TODO: this can probably be changed to handle_os_error (expected error),
    # if we don't end up adding anything that's specific to FileNotFoundErrors
    def _handle_enoent_error(self, e: OSError):
        """ Handles ENOENT errors that were safely caught (FileNotFoundError). """
        print(f'[{errno.errorcode[e.errno]}]', e.args[1], e.args[2])
        self.notifier.trigger_os_error()
        # TODO: log to a file w/ time
        # TODO: figure out if I need a teardown procedure
        self.notifier.trigger_critical_error()
        # TODO: close app

    def _handle_unexpected_error(self, e: OSError):
        """ Handles unexpected errors that were safely caught. """
        print('Unexpected error received:')
        self.notifier.trigger_unexpected_os_error()
        # Unknown error, output it and log, close app, teardown, etc.
        print('|'.join(e.args))
        print('closing QuickSaver...')
        self.notifier.trigger_critical_error()
        # TODO: close app

    def _validate_api_reply(self, api_call_name, api_reply, ok_status_list = [],
                            warn_status_list = [], raise_status_list = []):
        """ Validates API response based on provided statuses (ok, warn, raise). """
        # TODO: switch all prints to logs
        print("{} status received: {}".format(api_call_name, api_reply['status_code']))

        # Status code is ok
        if api_reply['status_code'] in ok_status_list:
            return True

        # Status code is bad
        if api_reply['status_code'] in warn_status_list:
            warning_text = "{} api {}: {}".format(api_call_name, api_reply['status_code'], api_reply['text'])
            print(warning_text)
            return False

        if len(raise_status_list) == 0 or api_reply['status_code'] in raise_status_list:
            raise RuntimeError("{} api error {} - {}".format(api_call_name, api_reply['status_code'], api_reply['text']))

        raise RuntimeError("{} api unhandled status_code {} - {}".format(api_call_name, api_reply['status_code'], api_reply['text']))

    def _get_api_tokens(self, auth_code):
        """ Retrieves API tokens using an auth code and saves
            the access and refresh tokens to the cache file. """

        # Make request to Spotify API to get API tokens and validate the response
        r = spotify_api.get_api_tokens(auth_code, self.redirect_uri, self.client_id, self.client_secret)
        self._validate_api_reply("token", r, ok_status_list = [200])
        print("api tokens received")

        # Add current time to token dict then save to cache file
        api_tokens = r['json']
        api_tokens['timestamp'] = time.time()
        cache.set_token_cache(api_tokens)

        self.api_tokens['access_token'] = api_tokens['access_token'],
        self.api_tokens['refresh_token'] = api_tokens['refresh_token'],

    def _refresh_access_token(self) -> bool:
        """ Refreshes the Spotify API access token, updates the refresh token if changed,
            updates the cache file, and returns whether the tokens were successfully refreshed. """

        r = spotify_api.refresh_access_token(self.api_tokens, self.client_id, self.client_secret)

        # Validate the response
        warn_status_list = []
        if 'timestamp' in self.api_tokens:
            warn_status_list.append(0)
        if not self._validate_api_reply("refresh", r, ok_status_list = [200], warn_status_list = warn_status_list):
            return False

        print("refreshed api tokens received")
        new_api_tokens = r['json']
        print("tokens received: {}".format(new_api_tokens))
        new_api_tokens['timestamp'] = time.time()

        # If a new refresh token was not provided, use the current one
        if 'refresh_token' not in new_api_tokens:
            new_api_tokens['refresh_token'] = self.api_tokens['refresh_token']
        else:
            print('NEW REFRESH TOKEN WAS PROVIDED !!')
            self.api_tokens['refresh_token'] = new_api_tokens['refresh_token']

        # Update the token cache and tokens in current client instance
        cache.set_token_cache(new_api_tokens)
        self.api_tokens['access_token'] = new_api_tokens['access_token'],

        return True

    def start_access_token_refresh_loop(self):
        """ Starts a loop that refreshes the Spotify access tokens
            every 20 minutes and retries upon failures. """

        last_refresh_time = time.time()

        while True:
            curr_time = time.time()

            # Refresh tokens every 20 minutes
            if curr_time - last_refresh_time >= REFRESH_INTERVAL:
                # Retry every 10 minutes if the access tokens fails to refresh
                if self._refresh_access_token() is False:
                    curr_time = self.start_retry_token_refresh_loop(curr_time)
                last_refresh_time = curr_time

            # Sleep to reduce CPU usage
            time.sleep(60)

    def start_retry_token_refresh_loop(self, failed_refresh_time: int) -> int:
        """ Starts a loop that retries to refresh the Spotify access tokens every 10 minutes
            until it is successful, and returns the time of the successful refresh. """
        last_refresh_time = failed_refresh_time

        while True:
            curr_time = time.time()

            # Retry to refresh tokens every 10 minutes
            if curr_time - last_refresh_time >= RETRY_INTERVAL:
                # Return the time of the token refresh if it's successful
                if self._refresh_access_token() is True:
                    return curr_time
                last_refresh_time = curr_time

            # Sleep to reduce CPU usage
            time.sleep(60)

    def get_playback_state(self):
        """ Gets information about the user's current playback state. """
        r = spotify_api.get_playback_state(self.api_tokens)
        self._validate_api_reply("player", r, ok_status_list = [200, 204],
                                 warn_status_list = [202, 401, 403, 429])
        print("playback state received")

        return r['json']

    def get_current_device_id(self):
        """ Gets the currently playing device ID. """
        player_status = self.get_playback_state(self.api_tokens)
        device_id = None

        if 'device' in player_status and 'id' in player_status['device']:
            if player_status['device']['id'] is not None and len(player_status['device']['id']) > 8:
                device_id = player_status['device']['id']
                print("current device id: {}".format(device_id))

        return device_id

    def get_currently_playing(self):
        """ Gets the currently playing track ID. """
        r = spotify_api.get_currently_playing(self.api_tokens)

        # Validate the response
        if not self._validate_api_reply("c-playing", r, ok_status_list = [200, 202, 204],
                                        warn_status_list = [0, 401, 403, 429]):
            return {'warn_shown': 1}
        if r['status_code'] != 200:
            return None

        # If no session is active, return None
        if len(r['json']) == 0 or 'item' not in r['json']:
            return None

        return r['json']['item']['id']

    def save_track(self, track_id):
        """ Saves the given track to the user's library. """
        r = spotify_api.save_track(self.api_tokens, track_id)
        self._validate_api_reply("save track", r, ok_status_list = [200, 202, 204],
                                 warn_status_list = [0, 401, 403, 429])
        print("track saved")

    def remove_track(self, track_id):
        """ Removes the given track from the user's library. """
        r = spotify_api.remove_track(self.api_tokens, track_id)
        self._validate_api_reply("remove track", r, ok_status_list = [200, 202, 204],
                                 warn_status_list = [0, 401, 403, 429])
        print("track removed")

    def is_track_saved(self, track_id):
        """ Checks whether the given track is saved to the user's library. """
        r = spotify_api.is_track_saved(self.api_tokens, track_id)
        self._validate_api_reply("remove track", r, ok_status_list = [200, 202, 204],
                                 warn_status_list = [0, 401, 403, 429])

        track_status = r['json'][0]
        print(f"track {track_id} is {'not ' if track_status is False else ''}saved")

        return track_status

    def add_to_playlist(self, playlist_id: str, track_id: str):
        """ Adds given track to the given playlist. """
        r = spotify_api.add_track_to_playlist(self.api_tokens, playlist_id, track_id)
        # *NOTE: I believe if this doesn't raise any errors, then we should be fine to assume it worked
        self._validate_api_reply("add to playlist", r, ok_status_list = [200, 202, 204],
                                 warn_status_list = [0, 401, 403, 429])
        print(f'track {track_id} was saved to playlist {playlist_id}')

    def remove_from_playlist(self, playlist_id: str, track_id: str):
        """ Removes given track from the given playlist. """
        r = spotify_api.remove_track_from_playlist(self.api_tokens, playlist_id, track_id)
        self._validate_api_reply("remove from playlist", r, ok_status_list = [200, 202, 204],
                                 warn_status_list = [0, 401, 403, 429])
        print(f'track {track_id} was removed from playlist {playlist_id}')

    def get_playlist_tracks(self, playlist_id: str) -> list[str]:
        """ Gets all the tracks in the given playlist. """

        # Make initial request and validate reply
        r = spotify_api.get_playlist_tracks(self.api_tokens, playlist_id)
        self._validate_api_reply("get playlist tracks", r, ok_status_list = [200, 202, 204],
                                 warn_status_list = [0, 401, 403, 429])

        # Get playlist tracks until no next page exists
        plist_tracks = []
        while True:

            # Extract playlist tracks and next page URL from the response
            plist_items = r['json']['items']
            next_page_url = r['json']['next']

            # Append track IDs to the master list
            for track in plist_items:
                plist_tracks.append(track['track']['id'])

            # Break if next page URL doesn't exist
            if next_page_url is None:
                break

            # Make request for next page of tracks
            print("fetching next page of tracks")
            r = spotify_api.next_playlist_tracks(self.api_tokens, next_page_url)
            self._validate_api_reply("get next page playlist tracks", r, ok_status_list = [200, 202, 204], warn_status_list = [0, 401, 403, 429])

        print(f'{len(plist_tracks)} tracks were from fetched from playlist {playlist_id}')

        return plist_tracks

    # async def _wait_for_button_press_ms(self, milliseconds):
    #     interval_begins = time.ticks_ms()
    #     button_pressed = self._check_button_presses()

    #     while not button_pressed and time.ticks_diff(time.ticks_ms(), interval_begins) < milliseconds:
    #         await asyncio.sleep_ms(50)
    #         button_pressed = self._check_button_presses()

    #     return button_pressed
"""
    async def _standby(self):
        print("standby")
        self._reset_button_presses()
        button_pressed = self._check_button_presses()

        standby_start = time.time()

        while not button_pressed:
            if not self.config['blank_oled_on_standby']:
                if time.time() >= oled_updated + 10:
                    self.oled.standby()
                    oled_updated = time.time()
            button_pressed = await self._wait_for_button_press_ms(1000)
            if self.config['standby_status_poll_interval_minutes'] > 0:
                if time.time() >= standby_start + ( 60 * self.config['standby_status_poll_interval_minutes'] ):
                    print("standby status poll")
                    break

        if button_pressed:
            if not self.button_playpause.was_pressed():
                self._reset_button_presses()
            self.oled.show(_app_name, "resuming operations", separator = False)
            return True
        else:
            return False

    async def _start_standby(self, last_playing):
        loop_begins = time.time()

        while loop_begins + (self.config['status_poll_interval_seconds'] - 1) > time.time():

            standby_time = last_playing + self.config['idle_standby_minutes'] * 60
            progress = (standby_time - time.time()) / (self.config['idle_standby_minutes'] * 60) * 100

            if time.time() >= standby_time:
                return True

            self.oled.show("Spotify", "not playing", progress = progress, ticks = False)

            if await self._wait_for_button_press_ms(1000):
                return False

        return False
 """

    # TODO: figure out how to implement token checking and refreshing
    # NOTE: This is the main loop of the original guy's app.
    # this will be important reference for deciding how to periodically refresh the token
    # async def _looper(self):
    #     # self.oled.show(_app_name, "start", separator = False)

    #     api_tokens = None

    #     try:
    #         refresh_token_file = open('refresh_token.txt', 'r')
    #     except OSError:
    #         refresh_token_file = None

    #     if refresh_token_file is None:
    #         self._initial_token_request()
    #     else:
    #         refresh_token = refresh_token_file.readline().strip()
    #         refresh_token_file.close()
    #         api_tokens = self._refresh_access_token({ 'refresh_token': refresh_token })

    #     # self.oled.show(_app_name, "tokenized", separator = False)
    #     print("api_tokens content: {}".format(api_tokens))

    #     playing = False
    #     last_playing = time.time()
    #     self._reset_button_presses()

    #     while True:
    #         gc.collect()
    #         gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())
    #         if self.memdebug:
    #             mem_info()

    #         self._wait_for_connection()

    #         if 'expires_in' not in api_tokens or 'access_token' not in api_tokens or time.time() >= api_tokens['timestamp'] + api_tokens['expires_in'] - 30:
    #             api_tokens = self._refresh_access_token(api_tokens)
    #             if 'expires_in' not in api_tokens or 'access_token' not in api_tokens:
    #                 time.sleep_ms(1000)
    #                 continue

    #         self._handle_buttons(api_tokens, playing)

    #         currently_playing = self._get_currently_playing(api_tokens)

    #         if currently_playing is not None:
    #             if 'warn_shown' in currently_playing:
    #                 continue
    #             playing = True
    #             last_playing = time.time()
    #             if self.device_id is None:
    #                 self.device_id = self._get_current_device_id(api_tokens)
    #         else:
    #             playing = False
    #             self.pause_after_current = False
    #             # self.oled.disable_status_dot()

    #         if playing:
    #             await self._show_play_progress_for_seconds(api_tokens, currently_playing, self.config['status_poll_interval_seconds'])
    #         else:
    #             if await self._start_standby(last_playing):
    #                 if await self._standby():
    #                     last_playing = time.time()
    #                 continue

    # def start(self):
    #     loop = asyncio.get_event_loop()
    #     try:
    #         loop.run_until_complete(self._looper())
    #     except KeyboardInterrupt:
    #         print("keyboard interrupt received, stopping")
    #         self.oled.clear()
    #     except RuntimeError:
    #         raise
    #     except Exception as e:
    #         self.oled.show(e.__class__.__name__, str(e))
    #         raise
