# from sys.stdin import readline
from actions import TOGGLE_LIKE, SAVE_MAIN, SAVE_OTHER, UNDO_SAVE, QUIT_APP


class ConsoleListener:
    """ Listener that triggers events based on hotkeys pressed by the user. """

    def __init__(self, console_callback, toggle_like_char: str = 'T', save_main_char: str = 'S', save_other_char: str = 'O', undo_save_char: str = 'U', quit_app_char: str = 'Q'):
        # raises ValueError if the same character is used for more than one hotkey
        if save_main_char.upper() == save_other_char.upper() or save_other_char.upper() == undo_save_char.upper() or undo_save_char.upper() == quit_app_char.upper() or quit_app_char.upper() == save_main_char.upper():
            raise ValueError('Cannot use the same character for more than one hotkey, each character has to be unique.')

        self.callback = console_callback  # callback that sends response back to QuickSaver

        # characters used for each hotkey
        self.toggle_like_char = toggle_like_char.upper()
        self.save_main_char = save_main_char.upper()
        self.save_other_char = save_other_char.upper()
        self.undo_save_char = undo_save_char.upper()
        self.quit_app_char = quit_app_char.upper()
        self.all_keys = {
            self.toggle_like_char,
            self.save_main_char,
            self.save_other_char,
            self.undo_save_char,
            self.quit_app_char
        }

    def start_listener(self):
        """ Initializes the console input listener loop and starts listening. """
        print('start adding!\n')
        while True:
            inputted_key = input().strip().upper()
            if len(inputted_key) != 1 or not inputted_key.isalpha():
                print('Error: input should only be one letter.')
            elif not self.is_valid_key(inputted_key):
                print('Error: invalid input, key is not defined.')
            elif inputted_key == self.toggle_like_char:
                self.callback(TOGGLE_LIKE)
            elif inputted_key == self.save_main_char:
                self.callback(SAVE_MAIN)
            elif inputted_key == self.save_other_char:
                self.callback(SAVE_OTHER)
            elif inputted_key == self.undo_save_char:
                self.callback(UNDO_SAVE)
            elif inputted_key == self.quit_app_char:
                self.callback(QUIT_APP)
                break
            else:
                print(f'Character {inputted_key} was passed, which is odd because it should\'ve been caught earlier.')

    def stop_listener(self):
        """ Placeholder because the parent component has to call this function to work. """
        print('thanks for stopping by! hopefully I was helpful :)')

    # === Helpers ===
    def is_valid_key(self, key: str) -> bool:
        """ Returns whether the inputted key is one of the defined input options. """
        return key in self.all_keys
