import re
from typing import Literal
from datetime import datetime
from time import time_ns

turkish_months = {
    "ocak": 1,
    "şubat": 2,
    "mart": 3,
    "nisan": 4,
    "mayıs": 5,
    "haziran": 6,
    "temmuz": 7,
    "ağustos": 8,
    "eylül": 9,
    "ekim": 10,
    "kasım": 11,
    "aralık": 12
}

months_in_turkish = {
    1: "ocak",
    2: "şubat",
    3: "mart",
    4: "nisan",
    5: "mayıs",
    6: "haziran",
    7: "temmuz",
    8: "ağustos",
    9: "eylül",
    10: "ekim",
    11: "kasım",
    12: "aralık"
}

turkish_weekdays = {
    "pazartesi": 0,
    "salı": 1,
    "çarşamba": 2,
    "perşembe": 3,
    "cuma": 4,
    "cumartesi": 5,
    "pazar": 6
}

weekdays_in_turkish = {
    0: "pazartesi",
    1: "salı",
    2: "çarşamba",
    3: "perşembe",
    4: "cuma",
    5: "cumartesi",
    6: "pazar"
}

turkish_uppercase_map = str.maketrans({
    "i": "İ",  # Convert 'i' to 'İ'
    "ı": "I",  # Convert 'ı' to 'I'
})


def turkish_upper(text) -> str:
    translated_text = text.translate(turkish_uppercase_map)
    return translated_text.upper()

def is_valid_people(people_str):
    # Define a regex pattern for Turkish full names with newline separation
    pattern = r"^(?:[A-ZÇĞİÖŞÜ][a-zçğıöşü]*\s)+(?:[A-ZÇĞİÖŞÜ]+)$"
    people_list = people_str.split(",")
    
    # Split the input by lines and check each line
    for person in people_list:
        # Trim whitespace and check if each line matches the full name pattern
        if not re.match(pattern, person):
            return False
    
    return True


def date_to_julian(date_str: str) -> float:
    date_obj = datetime.strptime(date_str, "%d.%m.%Y")
    julian_day = date_obj.toordinal() + 1721424.5
    return julian_day


def current_time_in_unix_subsec() -> float:
    time_ms = time_ns() / 1000000
    return time_ms / 1000


def legacy_time_in_unix_subsec(legacy_time_str: str) -> float:
    dt = datetime.strptime(legacy_time_str, "%d.%m.%Y %H:%M:%S")
    return dt.timestamp()


def normalize_date(date_str: str) -> str:
    date_str = date_str.strip().lower()

    # Check if the date is in "DD.MM.YYYY" format directly.
    try:
        # Try parsing as "DD.MM.YYYY".
        return datetime.strptime(date_str, "%d.%m.%Y").strftime("%d.%m.%Y")
    except ValueError:
        pass

    # Check for "Month YYYY" or "DD Month YYYY"
    parts = date_str.split()
    if len(parts) == 2:
        # Assume format "Month YYYY"
        month_str, year = parts
        month = turkish_months.get(month_str.capitalize(), 1)
        return f"01.{month:02d}.{year}"
    elif len(parts) == 3:
        # Assume format "DD Month YYYY"
        day, month_str, year = parts
        day = int(day)
        month = turkish_months.get(month_str.capitalize(), 1)
        return f"{day:02d}.{month:02d}.{year}"

    # Check for "MM.YYYY"
    if "." in date_str and len(date_str.split(".")) == 2:
        month, year = date_str.split(".")
        return f"01.{int(month):02d}.{year}"

    # Check for "YYYY" only.
    if date_str.isdigit() and len(date_str) == 4:
        return f"01.01.{date_str}"

    return ""


def date_includes(date_str: str, precision: int, input_list: list[str],
                  mode: Literal["day", "month", "year", "weekday"]):
    """
    Check if a given date includes at least one of the specified values based on precision and mode.

    Parameters:
    date_str (str): Date in "DD.MM.YYYY" format.
    precision (int): Precision level (7, 3, 1).
    input_list (list of str): List of values to check (days, months, years, or weekdays).
    mode (str): Mode to specify the type of input ('day', 'month', 'year', 'weekday').

    Returns:
    bool: True if the date includes at least one of the given values based on the mode, False otherwise.
    """

    # Parse the date string
    try:
        day, month, year = date_str.lower().split(".")
    except ValueError:
        raise ValueError("Date must be in 'DD.MM.YYYY' format.")

    # Mode-based logic
    if mode == "day":
        if precision != 7:
            return False
        # Strip leading zeros from the day for comparison
        day_without_leading_zeros = str(int(day))
        return day in input_list or day_without_leading_zeros in input_list

    elif mode == "month":
        if precision not in [3, 7]:
            return False
        month_number = int(month)
        month_without_leading_zeros = str(month_number)
        month_name = months_in_turkish[month_number]
        return (
                month_without_leading_zeros in input_list or
                month_name in input_list or
                month in input_list
        )

    elif mode == "year":
        if precision not in [1, 3, 7]:
            return False
        return year in input_list

    elif mode == "weekday":
        if precision != 7:
            return False
        try:
            date_obj = datetime(int(year), int(month), int(day))
        except ValueError:
            raise ValueError("Invalid date provided.")
        weekday_number = date_obj.weekday()
        weekday_name = weekdays_in_turkish[weekday_number]
        weekday_number_in_input_format = str(weekday_number + 1)
        return (
                weekday_name in input_list or
                weekday_number_in_input_format in input_list or
                weekday_number_in_input_format.zfill(2) in input_list
        )

    else:
        raise ValueError("Mode must be 'day', 'month', 'year', or 'weekday'.")
