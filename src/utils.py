import ujson
import os


def read_json(filename: str) -> dict:
    """ Reads and returns the data stored in the given JSON file. """
    file_exists_error(filename)
    with open(filename, 'r') as json_infile:
        return ujson.load(json_infile)

def write_json(data: dict, filename: str):
    """ Writes the given data to the given JSON file. """
    with open(filename, 'w+') as json_outfile:
        ujson.dump(data, json_outfile)

def format_json(data: dict) -> str:
    """ Returns the given data as a JSON formatted string. """
    return ujson.dumps(data)

def file_exists(filename: str) -> bool:
    """ Returns whether the given file exists. """
    return filename in os.listdir()

def file_exists_error(filename: str) -> bool:
    """ Raises an error if the given file doesn't exist, otherwise returns True. """
    if file_exists(filename) is False:
        raise OSError(errno.ENOENT, 'File does not exist:', filename)
    return True

def spotify_id_from_link(spotify_link: str) -> str:
    """ Extracts and returns the Spotify ID from the given Spotify link. """
    return spotify_link.split('/')[-1].split('?')[0]
