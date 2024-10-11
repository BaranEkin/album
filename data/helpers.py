from datetime import datetime
from time import time_ns


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

