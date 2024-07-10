import time
import sys
import os


class Logger:
    def __init__(self, filename, console_output=True):
        self.filename = filename
        self.console_output = console_output
        self.console_available = self.check_console()
        self.file = open(self.filename, 'a')  # Keep the file open

    def check_console(self):
        # Check if stdout is redirected or not
        # FIXME: find another way to do this
        return os.isatty(sys.stdout.fileno())

    def _log(self, level, msg, to_file=True, to_console=False):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        log_entry = f"{timestamp} - {level} - {msg}\n"

        # Write to file if required and flush
        if to_file is True:
            self.file.write(log_entry)
            self.file.flush()

        # Optionally print to console
        if to_console is True and self.console_available is True:
            print(log_entry, end='')

    def info(self, msg):
        """ Log the given info message to console if available. """
        self._log("INFO", msg, to_file=False, to_console=True)

    def warning(self, msg):
        """ Log the given warning message to file, and console if available. """
        self._log("WARNING", msg, to_file=True, to_console=True)

    def error(self, msg):
        """ Log the given error message to file, and console if available. """
        self._log("ERROR", msg, to_file=True, to_console=True)

    def close(self):
        # Ensure the file is properly closed
        if self.file:
            self.file.close()

# Example usage
logger = Logger('logfile.txt')

logger.error('Critical error')          # goes to file, and to console if available
logger.info('song saved successfully!') # only goes to console if available

logger.close()  # ! Don't forget to close the logger when done
