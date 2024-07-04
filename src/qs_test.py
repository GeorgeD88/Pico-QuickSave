# 2024 George Doujaiji
# Clean version of qs_main.py that I can actually run to be able to test

from quicksaver import QuickSaver
from console_listener import ConsoleListener
from console_notifier import ConsoleNotifier
import ujson
import os

CONFIG = "config.json"


def main():
    # Load config file and get playlist IDs
    if CONFIG not in os.listdir():
        # ERROR: file does not exist
        print('\'oly moly')
        return None

    with open('config.json', 'r') as infile:
        plist_config = ujson.load(infile)['playlists']

    main_playlist = plist_config['main_playlist']
    other_playlist = plist_config['other_playlist']

    # Initialize the main quick saver component and start the input listener
    print('starting QuickSaver!')
    quicksaver = QuickSaver(ConsoleListener, ConsoleNotifier, main_playlist, other_playlist)


if __name__ == "__main__":
    main()
