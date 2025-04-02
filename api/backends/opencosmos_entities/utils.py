from datetime import datetime
import re
from typing import Self

from pydantic import BaseModel, Field, model_validator


def convert_datetime_to_iso8601(date: datetime) -> str:
    """Convert a datetime object to an ISO8601 string with a Z at the end"""

    return f"{datetime.isoformat(date)}Z"


def convert_datetime_string_to_datetime(date: str) -> datetime:
    """Convert a datetime string to a datetime object. We use this rather than
    the `datetime.fromisoformat` method because it does not handle the Z at the
    end and the MSD returns the super high precision milliseconds.
    """

    date = date.split(".")[0]
    date = f"{date}Z"
    return datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")

def datetime_parser(dict_: dict) -> dict:
    for key, value in dict_.items():
        if isinstance(value, str) and re.search("start|stop", key):
            dict_[key] = convert_datetime_string_to_datetime(value)
    return dict_


class Range(BaseModel):
    """ Base class for range validation """
    
    minimum: float = Field(ge=-180)
    maximum: float = Field(le=180)

    @model_validator(mode="after")
    def validate_range(self) -> Self:
        if self.minimum > self.maximum:
            raise ValueError("range minimum cannot be greater than maximum")
        return self

class OffNadirRange(BaseModel):
    minimum: float = Field(ge=0, le=45)
    maximum: float = Field(ge=0, le=45)

    @model_validator(mode="after")
    def validate_range(self) -> Self:
        if self.minimum > self.maximum:
            raise ValueError("range minimum cannot be greater than maximum")
        return self