from typing import Literal
from datetime import datetime

LOG_FILE_PATH = "album.log"
log_file = None

def _get_log_file():
    """Initialize the log file if it hasn't been opened yet and returns the file handle."""

    global log_file
    if log_file is None:
        log_file = open(LOG_FILE_PATH, "a")
    return log_file

def log(headline: str, details: str = "", level: Literal["debug", "info", "warning", "error"] = "info"):
    """
    Log a message to the log file with a timestamp, level, headline, and optional details.

    Args:
        headline (str): The main headline for the log entry.
        details (str, optional): Additional details for the log entry.
        level (Literal["debug", "info", "warning", "error"], optional): The severity level of the log entry.
            Must be one of "debug", "info", "warning", "error". Defaults to "info".
    """

    # Get the current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Pad to 7 characters for alignment
    level_str = level.upper().ljust(7)
    
    # Format the log message
    if details:
        log_message = f"{timestamp} | {level_str} | {headline} | {details}"
    else:
        log_message = f"{timestamp} | {level_str} | {headline}"
    
    # Write the log message to the log file
    _get_log_file().write(log_message + "\n")

def close_log():
    """Close the log file if it is open."""

    global log_file
    if log_file:
        log_file.close()
        log_file = None
