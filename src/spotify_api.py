import gc
import time
from micropython import const

# imports from additional files
import uurequests as requests
from helpers import b64encode, urlencode
import json

_spotify_account_api_base = const("https://accounts.spotify.com/api")
_spotify_api_base = const("https://api.spotify.com")

def _spotify_api_request(method, url, data = None, headers = None, retry = True):
    ret = {'status_code': 0, 'json': {}, 'text': 'No reply content'}
    print("{} {}".format(method, url))
    try:
        r = requests.request(method, url, data = data, headers = headers)
    except OSError as e:
        print("OSError: {}".format(e))
        ret['text'] = str(e)
        r = None

    if r is None or r.status_code < 200 or r.status_code >= 500:
        if retry:
            if r is None:
                print("failed, retrying...")
            elif r is not None:
                print("status {}, retrying...".format(r.status_code))
                r.close()
                del r
            time.sleep_ms(500)
            return _spotify_api_request(method, url, data = data, headers = headers, retry = False)
        else:
            return ret

    ret['status_code'] = r.status_code
    try:
        ret['json'] = r.json()
    except Exception as e:
        if r.status_code == 200 and method == "GET":
            print("json decoding failed: {}".format(e))
            if retry:
                if r is not None:
                    r.close()
                    del r
                print("retrying...")
                time.sleep_ms(500)
                gc.collect()
                return _spotify_api_request(method, url, data = data, headers = headers, retry = False)
            ret['status_code'] = 0
            ret['json'] = {'exception': 1}
            ret['text'] = str(e)

    if len(ret['json']) == 0:
        try:
            ret['text'] = r.text
        except:
            pass

    try:
        r.close()
    except:
        pass

    del r
    return ret

def get_api_tokens(authorization_code, redirect_uri, client_id, client_secret):
    spotify_token_api_url = "{}/token".format(_spotify_account_api_base)
    reqdata = { 'grant_type': 'authorization_code', 'code': authorization_code, 'redirect_uri': redirect_uri }

    b64_auth = "Basic {}".format(b64encode(b"{}:{}".format(client_id, client_secret)).decode())
    headers = { 'Content-Type': 'application/x-www-form-urlencoded', 'Authorization': b64_auth }

    return _spotify_api_request("POST", spotify_token_api_url, data = urlencode(reqdata), headers = headers)

def refresh_access_token(api_tokens, client_id, client_secret):
    spotify_token_api_url = "{}/token".format(_spotify_account_api_base)
    reqdata = { 'grant_type': 'refresh_token', 'refresh_token': api_tokens['refresh_token'] }

    b64_auth = "Basic {}".format(b64encode(b"{}:{}".format(client_id, client_secret)).decode())
    headers = { 'Content-Type': 'application/x-www-form-urlencoded', 'Authorization': b64_auth }

    return _spotify_api_request("POST", spotify_token_api_url, data = urlencode(reqdata), headers = headers)

def get_currently_playing(api_tokens):
    spotify_player_api_url = "{}/v1/me/player/currently-playing?additional_types=track,episode".format(_spotify_api_base)
    headers = { 'Authorization': "Bearer {}".format(api_tokens['access_token']) }

    return _spotify_api_request("GET", spotify_player_api_url, headers = headers)

def get_playback_state(api_tokens):
    spotify_player_api_url = "{}/v1/me/player".format(_spotify_api_base)
    headers = { 'Authorization': "Bearer {}".format(api_tokens['access_token']) }

    return _spotify_api_request("GET", spotify_player_api_url, headers = headers)

def pause_playback(api_tokens):
    spotify_player_api_url = "{}/v1/me/player/pause".format(_spotify_api_base)
    headers = { 'Authorization': "Bearer {}".format(api_tokens['access_token']) }

    return _spotify_api_request("PUT", spotify_player_api_url, headers = headers)

def resume_playback(api_tokens, device_id = None):
    spotify_player_api_url = "{}/v1/me/player/play".format(_spotify_api_base)
    headers = { 'Authorization': "Bearer {}".format(api_tokens['access_token']) }
    if device_id is not None:
        spotify_player_api_url += "?device_id={}".format(device_id)

    return _spotify_api_request("PUT", spotify_player_api_url, headers = headers)

def next_playback(api_tokens, device_id = None):
    spotify_player_api_url = "{}/v1/me/player/next".format(_spotify_api_base)
    headers = { 'Authorization': "Bearer {}".format(api_tokens['access_token']) }
    if device_id is not None:
        spotify_player_api_url += "?device_id={}".format(device_id)

    return _spotify_api_request("POST", spotify_player_api_url, headers = headers)

def save_track(api_tokens, track_id):
    spotify_me_api_url = "{}/v1/me/tracks?ids={}".format(_spotify_api_base, track_id)
    headers = { 'Authorization': "Bearer {}".format(api_tokens['access_token']) }

    return _spotify_api_request("PUT", spotify_me_api_url, headers = headers)

def remove_track(api_tokens, track_id):
    spotify_me_api_url = "{}/v1/me/tracks?ids={}".format(_spotify_api_base, track_id)
    headers = { 'Authorization': "Bearer {}".format(api_tokens['access_token']) }

    return _spotify_api_request("DELETE", spotify_me_api_url, headers = headers)

def is_track_saved(api_tokens, track_id):
    spotify_me_api_url = "{}/v1/me/tracks/contains?ids={}".format(_spotify_api_base, track_id)
    headers = { 'Authorization': "Bearer {}".format(api_tokens['access_token']) }

    return _spotify_api_request("GET", spotify_me_api_url, headers = headers)

def add_track_to_playlist(api_tokens, playlist_id, track_id):
    spotify_playlist_api_url = "{}/v1/playlists/{}/tracks?uris=spotify:track:{}".format(_spotify_api_base, playlist_id, track_id)
    headers = { 'Authorization': "Bearer {}".format(api_tokens['access_token']) }

    return _spotify_api_request("POST", spotify_playlist_api_url, headers = headers)

def remove_track_from_playlist(api_tokens, playlist_id, track_id):
    spotify_playlist_api_url = "{}/v1/playlists/{}/tracks".format(_spotify_api_base, playlist_id)
    reqdata = { 'tracks': [ {"uri": "spotify:track:" + track_id } ]}
    headers = { 'Authorization': "Bearer {}".format(api_tokens['access_token']), 'Content-Type': 'application/json'}

    return _spotify_api_request("DELETE", spotify_playlist_api_url, data = json.dumps(reqdata), headers = headers)

def get_playlist_tracks(api_tokens, playlist_id):
    spotify_playlist_api_url = "{}/v1/playlists/{}/tracks?fields=items(track(id)),next".format(_spotify_api_base, playlist_id)
    headers = { 'Authorization': "Bearer {}".format(api_tokens['access_token']) }

    return _spotify_api_request("GET", spotify_playlist_api_url, headers = headers)

def next_playlist_tracks(api_tokens, next_page_url):
    headers = { 'Authorization': "Bearer {}".format(api_tokens['access_token']) }

    return _spotify_api_request("GET", next_page_url, headers = headers)

def get_queue(api_tokens):
    spotify_player_api_url = "{}/v1/me/player/queue".format(_spotify_api_base)
    headers = { 'Authorization': "Bearer {}".format(api_tokens['access_token']) }

    return _spotify_api_request("GET", spotify_player_api_url, headers = headers)
