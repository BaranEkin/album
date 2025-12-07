import re
from typing import Final, Literal
from datetime import datetime, timedelta
from time import time_ns

from data.orm import Media

TURKISH_MONTHS: Final[dict[str, int]] = {
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
    "aralık": 12,
}
MONTHS_IN_TURKISH: Final[dict[int, str]] = {v: k for k, v in TURKISH_MONTHS.items()}
TURKISH_WEEKDAYS: Final[dict[str, int]] = {
    "pazartesi": 0,
    "salı": 1,
    "çarşamba": 2,
    "perşembe": 3,
    "cuma": 4,
    "cumartesi": 5,
    "pazar": 6,
}
WEEKDAYS_IN_TURKISH: Final[dict[int, str]] = {v: k for k, v in TURKISH_WEEKDAYS.items()}
TURKISH_UPPERCASE_MAP: Final[dict[int, str]] = str.maketrans(
    {
        "i": "İ",
        "ı": "I",
    }
)
TURKISH_LOWERCASE_MAP: Final[dict[int, str]] = str.maketrans(
    {
        "İ": "i",
        "I": "ı",
    }
)


def turkish_upper(text: str) -> str:
    translated_text = text.translate(TURKISH_UPPERCASE_MAP)
    return translated_text.upper()


def turkish_lower(text: str) -> str:
    translated_text = text.translate(TURKISH_LOWERCASE_MAP)
    return translated_text.lower()


TURKISH_I_NORMALIZE_MAP: Final[dict[int, str]] = str.maketrans(
    {
        "İ": "i",
        "I": "i",
        "ı": "i",
        # "i" stays as "i"
    }
)


def turkish_normalize(text: str | None) -> str:
    if not text:
        return ""
    # First normalize i-variants, then lowercase
    text = text.translate(TURKISH_I_NORMALIZE_MAP)
    return text.lower()


def is_valid_people(people_str: str) -> bool:
    if not people_str:
        return True
    pattern = r"^(?:[A-ZÇĞİÖŞÜ][a-zçğıöşü]*\s)+(?:[A-ZÇĞİÖŞÜ]+(?:\s[A-ZÇĞİÖŞÜ]+)*)$"
    people_list = [person.strip() for person in people_str.split(",")]

    for person in people_list:
        if not re.match(pattern, person):
            return False

    return True


def date_to_julian(date_str: str) -> float:
    date_obj = datetime.strptime(date_str, "%d.%m.%Y")
    julian_day = date_obj.toordinal() + 1721424.5
    return julian_day


def current_time_in_unix_subsec() -> float:
    return time_ns() / 1_000_000_000


def legacy_time_in_unix_subsec(legacy_time_str: str) -> float:
    dt = datetime.strptime(legacy_time_str, "%d.%m.%Y %H:%M:%S")
    return dt.timestamp()


def get_unix_time_days_ago(days: int) -> float:
    now = datetime.now()
    time_days_ago = now - timedelta(days=days)
    return time_days_ago.timestamp()


def normalize_date(date_str: str) -> str:
    date_str = date_str.strip().casefold()

    # Check if the date is in "DD.MM.YYYY" format directly.
    try:
        return datetime.strptime(date_str, "%d.%m.%Y").strftime("%d.%m.%Y")
    except ValueError:
        pass

    # Check for "Month YYYY" or "DD Month YYYY"
    parts = date_str.split()
    if len(parts) == 2:
        # Assume format "Month YYYY"
        month_str, year = parts
        month = TURKISH_MONTHS.get(month_str)
        if month is None or not (year.isdigit() and len(year) == 4):
            return ""
        return f"01.{month:02d}.{year}"
    elif len(parts) == 3:
        # Assume format "DD Month YYYY"
        day_str, month_str, year = parts
        try:
            day = int(day_str)
        except ValueError:
            return ""
        month = TURKISH_MONTHS.get(month_str)
        if month is None or not (year.isdigit() and len(year) == 4):
            return ""
        if not 1 <= day <= 31:
            return ""
        return f"{day:02d}.{month:02d}.{year}"

    # Check for "MM.YYYY"
    if "." in date_str:
        mm_yyyy_parts = date_str.split(".")
        if len(mm_yyyy_parts) == 2:
            month_str, year = mm_yyyy_parts
            try:
                month = int(month_str)
            except ValueError:
                return ""
            if not 1 <= month <= 12:
                return ""
            if not (year.isdigit() and len(year) == 4):
                return ""
            return f"01.{month:02d}.{year}"

    # Check for "YYYY" only.
    if date_str.isdigit() and len(date_str) == 4:
        return f"01.01.{date_str}"

    return ""


def date_includes(
    date_str: str,
    precision: int,
    input_list: list[str],
    mode: Literal["day", "month", "year", "weekday"],
) -> bool:
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
        month_name = MONTHS_IN_TURKISH[month_number]
        return (
            month_without_leading_zeros in input_list
            or month_name in input_list
            or month in input_list
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
        weekday_name = WEEKDAYS_IN_TURKISH[weekday_number]
        weekday_number_in_input_format = str(weekday_number + 1)
        return (
            weekday_name in input_list
            or weekday_number_in_input_format in input_list
            or weekday_number_in_input_format.zfill(2) in input_list
        )


def generate_export_filename(media: Media) -> str:
    day, month, year = media.date_text.split(".")
    return f"M{year}{month}{day}_{int(media.rank):03d}{media.extension}"
