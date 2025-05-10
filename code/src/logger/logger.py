import logging
import os

from src.logger.formatter import Formatter


class Logger(logging.Formatter):
    """
    A utility class for setting up logging with a custom formatter.
    This class provides functionality to configure the logging system and
    attach a custom formatter to console output.
    """

    @staticmethod
    def setup() -> None:
        """
        Sets up the logger with a minimum logging level and attaches a console handler with a custom formatter.

        Workflow:
        1. Configures the logger to use the DEBUG level as the minimum threshold for logging messages.
        2. Creates a console handler for logging messages to the console (stdout).
        3. Attaches a custom formatter (CustomFormatter) to the console handler.
        4. Adds the configured console handler to the logger.

        Raises:
            AttributeError: If CustomFormatter is not defined or raises an error during instantiation.

        Returns:
            None
        """
        logger = logging.getLogger()
        # Set the minimum logging level
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        logger.setLevel(log_level)
        # Create a console handler
        console_handler = logging.StreamHandler()
        # Attach the custom formatter to the console handler
        console_handler.setFormatter(Formatter())
        # Add the handler to the logger
        logger.addHandler(console_handler)
