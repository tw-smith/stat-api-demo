from datetime import datetime
from typing import Any, Optional
from geojson_pydantic.features import Feature
from pydantic import BaseModel
from api.backends.opencosmos_entities.utils import convert_datetime_to_iso8601


class ManualTaskingOrchestrationSearchRequest(BaseModel):
    """Represents the request body for a MTO opportunity search request"""

    instruments: list[dict[str, str]]
    areas_of_interest: list[dict[str, str | Feature]]
    constraints: list
    start: datetime
    stop: datetime

    def to_json(self, **kwargs: Any):
        return self.json(by_alias=True, exclude_unset=True, **kwargs)
    

class ManualTaskingOrchestrationSwathRequest(BaseModel):
    """Represents the request body for a MTO swath search request"""

    instrument: dict[str, str]
    area_of_interest: dict[str, str | Feature]
    roll_angle: float
    start: datetime
    stop: datetime

    def to_json(self, **kwargs: Any):
        return self.json(by_alias=True, exclude_unset=True, **kwargs)

    class Config:
        json_encoders = {datetime: convert_datetime_to_iso8601}


class ActivityParameters(BaseModel):
    """Represents the parameters for an activity in a tasking request"""

    platform: dict[str, float]
    imager: dict[str, str]


class Activity(BaseModel):
    """Represents an activity in a tasking request"""

    mission_id: str
    start_date: datetime
    end_date: datetime
    type: str
    parameters: ActivityParameters


class CreateTaskingRequestRequest(BaseModel):
    """Represents the request body for a tasking request"""

    type: str
    region_name: str
    region: Feature
    parameters: Optional[dict[str, Any]]
    activities: list[Activity]
    constraints: list
    instruments: list[dict[str, str]]

    def to_json(self, **kwargs: Any):
        return self.json(by_alias=True, exclude_unset=True, **kwargs)

    class Config:
        json_encoders = {datetime: convert_datetime_to_iso8601}

