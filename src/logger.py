import time
import sys
import os

INFO = "INFO"
WARNING = "WARNING"
ERROR = "ERROR"


class Logger:

    SPACES = {INFO: 4, WARNING: 1, ERROR: 3}

    # keep `to_console` false and save to pi. when running on computer, manually pass `to_console=True`
    def __init__(self, filename, to_console=False):
        self.filename = filename
        self.to_console = to_console
        self.console_available = self.check_console()
        self.file = open(self.filename, 'a')  # Keep the file open

    def check_console(self):
        # Check if stdout is redirected or not, meaning there should
        # FIXME: find another way to do this
        # return os.isatty(sys.stdout.fileno())
        pass

    def _log(self, level: str, msg: str, to_file: bool = True, to_console: bool = False):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        log_entry = f"{timestamp} [{level}]{self._spacing(level)}{msg}\n"

        # Write to file if required and flush
        if to_file is True:
            self.file.write(log_entry)
            self.file.flush()

        # Optionally print to console
        if to_console is True and self.console_available is True:
            print(log_entry, end='')

    def _spacing(self, level: str):
        return self.SPACES[level] * ' '

    def info(self, msg: str):
        """ Log the given info message to console if available. """
        self._log(INFO, msg, to_file=False, to_console=True)

    def warning(self, msg: str):
        """ Log the given warning message to file, and console if available. """
        self._log(WARNING, msg, to_file=True, to_console=True)

    def error(self, msg: str):
        """ Log the given error message to file, and console if available. """
        self._log(ERROR, msg, to_file=True, to_console=True)

    def close(self):
        # Ensure the file is properly closed
        if self.file:
            self.file.close()

# Example usage
logger = Logger('logfile.txt')

logger.error('Critical error')          # goes to file, and to console if available
logger.info('song saved successfully!') # only goes to console if available

logger.close()  # ! Don't forget to close the logger when done
