import logging

from colorama import Fore, Style


class Formatter(logging.Formatter):
    """
    Custom formatter class to add colors to the log levels.
    """

    # Define colors for each log level
    LOG_COLORS = {
        "DEBUG": Fore.CYAN,
        "INFO": Fore.GREEN,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "CRITICAL": Fore.RED + Style.BRIGHT,
    }

    def format(self, record: logging.LogRecord) -> str:
        """
        Formats a logging record with custom coloring based on the log level.

        This method applies a color to the log message depending on its level
        (e.g., INFO, WARNING, ERROR) and formats the message with a custom log string
        that includes the timestamp, log level, and log message. The log color is reset
        at the end of each message to avoid color bleed.

        Args:
            record (logging.LogRecord): The log record object containing information about
                the log event, such as level, timestamp, and message.

        Returns:
            str: A formatted string for the log record, including colors based on the log level.
        """
        # Get the color for the current log level
        log_color = self.LOG_COLORS.get(record.levelname, "")
        reset = Style.RESET_ALL

        # Custom format string with color
        log_fmt = f"{log_color}%(asctime)s - %(levelname)s - %(message)s{reset}"
        formatter = logging.Formatter(log_fmt)

        # Use the standard formatter to format the record
        return formatter.format(record)
