# 2024 George Doujaiji

import utils as utl

CONFIG_FILE = "config.json"
EMPTY_CONFIG = {
    "spotify": {
        "client_id": None,
        "client_secret": None,
        "redirect_uri": "http://localhost:8888/callback"
    },
    "playlists": {"main_playlist": None, "other_playlist": None},
    "log_filename": "quicksaver.log",
    "gpio_pins": {
        "led_save": 0,
        "led_alert": 0,
        "led_error": 0,
        "button_save_lib": 0,
        "button_save_main": 0,
        "button_save_other": 0,
        "button_undo_save": 0
    },
    # List of WiFi details starting with the highest priority network
    "wlan": [{"ssid": None, "password": None, "mdns": None}]
}


def create_empty_config():
    """ Writes a template config to the config file. """
    utl.write_json(EMPTY_CONFIG, CONFIG_FILE)

def init_config():
    """ Creates an empty config file if it doesn't already exist
        and returns True if it was able to create it, otherwise False. """
    if utl.file_exists(CONFIG_FILE) is False:
        create_empty_config()
        return True
    return False

def set_config(config: dict):
    """ Writes the given configuration dict to the config file. """
    utl.write_json(config, CONFIG_FILE)

def get_config() -> dict:
    """ Reads the config file and returns the configuration dict. """
    utl.file_exists_error(CONFIG_FILE)
    return utl.read_json(CONFIG_FILE)

def get_config_value(key: str) -> dict | list:
    """ Retrieves and returns the value associated
        with the given key from the config file. """
    utl.file_exists_error(CONFIG_FILE)
    config = get_config()

    if key not in config:
        raise KeyError('Key not found in config: ' + key)

    return config[key]

def set_config_value(key: str, new_value):
    """ Stores or updates the given value for
        the specified key in the config file. """
    utl.file_exists_error(CONFIG_FILE)
    config = get_config()
    config[key] = new_value
    set_config(config)

def get_spotify_creds() -> dict:
    """ Retrieves and returns the spotify creds from the config file. """
    return get_config_value('spotify')

def get_playlist_ids() -> dict:
    """ Retrieves and returns the playlist IDs from the config file. """
    return get_config_value('playlists')

# TODO: continue rewriting the handler for the config file
def get_access_token() -> str:
    """ Retrieves and returns the access token from the config file. """
    return get_token_cache_value('access_token')

def set_access_token(new_access_token: str):
    """ Stores or updates the given access token in the config file. """
    set_token_cache_value('access_token', new_access_token)

def get_refresh_token() -> str:
    """ Retrieves and returns the refresh token from the config file. """
    return get_token_cache_value('refresh_token')

def set_refresh_token(new_refresh_token: str):
    """ Stores or updates the given refresh token in the config file. """
    set_token_cache_value('refresh_token', new_refresh_token)

# TODO: brainstorm how to approach setters/getters of all parts of the config.
# ex. write a wifi_dict to the wlan list in the config, or get the first priority wifi.
# for the other stuff, I feel like it makes the most sense to have regular getters,
# such as getting the entire dict under the "spotify" key.