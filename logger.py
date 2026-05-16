import os
import re
from typing import Literal
from datetime import datetime

LOG_DIR = "logs"
MAX_BYTES_PER_FILE = 2 * 1024 * 1024
_LOG_FILE_PATTERN = re.compile(r"^(\d{3})\.log$")

log_file = None


def _resolve_log_file_path() -> str:
    os.makedirs(LOG_DIR, exist_ok=True)

    highest_index = 0
    highest_name = ""
    for name in os.listdir(LOG_DIR):
        match = _LOG_FILE_PATTERN.match(name)
        if match and int(match.group(1)) > highest_index:
            highest_index = int(match.group(1))
            highest_name = name

    if highest_index == 0:
        return os.path.join(LOG_DIR, "001.log")

    current_path = os.path.join(LOG_DIR, highest_name)
    if os.path.getsize(current_path) >= MAX_BYTES_PER_FILE:
        return os.path.join(LOG_DIR, f"{highest_index + 1:03d}.log")
    return current_path


def _get_log_file():
    """Initialize the log file if it hasn't been opened yet and returns the file handle."""

    global log_file
    if log_file is None:
        log_file = open(_resolve_log_file_path(), "a", encoding="utf-8")
    return log_file


def log(
    headline: str,
    details: str = "",
    level: Literal["debug", "info", "warning", "error"] = "info",
):
    """
    Log a message to the log file with a timestamp, level, headline, and optional details.

    Args:
        headline (str): The main headline for the log entry.
        details (str, optional): Additional details for the log entry.
        level (Literal["debug", "info", "warning", "error"], optional): The severity level of the log entry.
            Must be one of "debug", "info", "warning", "error". Defaults to "info".
    """

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    level_str = level.upper().ljust(7)

    if details:
        log_message = f"{timestamp} | {level_str} | {headline} | {details}"
    else:
        log_message = f"{timestamp} | {level_str} | {headline}"

    _get_log_file().write(log_message + "\n")


def close_log():
    """Close the log file if it is open."""

    global log_file
    if log_file:
        log_file.close()
        log_file = None
