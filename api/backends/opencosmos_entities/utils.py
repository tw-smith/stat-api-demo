from datetime import datetime


def convert_datetime_to_iso8601_with_z(date: datetime) -> str:
    """Convert a datetime object to an ISO8601 string with Z at the end"""

    return f"{datetime.isoformat(date)}Z"


def convert_datetime_string_to_datetime(date: str) -> datetime:
    """Convert a datetime string to a datetime object. We use this rather than
    the `datetime.fromisoformat` method because it does not handle the Z at the
    end and the MSD returns the super high precision milliseconds.
    """
    date = date.split(".")[0]
    date = f"{date}Z"
    return datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")