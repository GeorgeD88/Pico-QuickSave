# 2024 George Doujaiji

import utils as utl

TKN_FILE = "cache.json"


def create_empty_cache():
    """ Writes an empty dict to the cache file. """
    utl.write_json({}, TKN_FILE)

def init_cache():
    """ Creates an empty cache file if it doesn't already exist
        and returns True if it was able to create it, otherwise False. """
    if utl.file_exists(TKN_FILE) is False:
        create_empty_cache()
        return True
    return False

def set_token_cache(token_cache: dict):
    """ Writes the given token dict to the cache file. """
    utl.write_json(token_cache, TKN_FILE)

def get_token_cache() -> dict:
    """ Reads the cache file and returns the token dict. """
    utl.file_exists_error(TKN_FILE)
    return utl.read_json(TKN_FILE)

def get_token_cache_value(key: str) -> str | int:
    """ Retrieves and returns the value associated
        with the given key from the cache file. """
    utl.file_exists_error(TKN_FILE)
    token_cache = get_token_cache()

    if key not in token_cache:
        raise KeyError('Key not found in token cache: ' + key)

    return token_cache[key]

def set_token_cache_value(key: str, new_value):
    """ Stores or updates the given value for
        the specified key in the cache file. """
    utl.file_exists_error(TKN_FILE)
    token_cache = get_token_cache()
    token_cache[key] = new_value
    set_token_cache(token_cache)

def get_access_token() -> str:
    """ Retrieves and returns the access token from the cache file. """
    return get_token_cache_value('access_token')

def set_access_token(new_access_token: str):
    """ Stores or updates the given access token in the cache file. """
    set_token_cache_value('access_token', new_access_token)

def get_refresh_token() -> str:
    """ Retrieves and returns the refresh token from the cache file. """
    return get_token_cache_value('refresh_token')

def set_refresh_token(new_refresh_token: str):
    """ Stores or updates the given refresh token in the cache file. """
    set_token_cache_value('refresh_token', new_refresh_token)
