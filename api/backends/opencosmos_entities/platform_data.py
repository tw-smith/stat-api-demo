from typing import Any, List
from pydantic import BaseModel


class OCPlatform(BaseModel):
    name: str
    mission_id: str
    sensor_id: str
    constraints: List[dict[str, Any]]


def get_available_oc_platforms() -> List[OCPlatform]:
    """
    Returns a list of available OpenCosmos platforms.
    """
    return [
        OCPlatform(
            name="menut",
            mission_id="55",
            sensor_id="MultiScape100 CIS"
            constraints=[
                {
                    "roll_angle": [-15, 45]
                }
            ]
        ),
        OCPlatform(
            name="alisio",
            sensor_id="DRAGO-2",
            mission_id="60",
            constraints=[
                {
                    "roll_angle": [-15, 45]
                }
            ]
        ),
        OCPlatform(
            name="hammer",
            mission_id="57",
            sensor_id="HyperScape100",
            constraints=[
                {
                    "roll_angle": [-15, 45]
                }
            ]
        ),
        OCPlatform(
            name="platero",
            mission_id="64",
            sensor_id="MultiScape100 CIS"
            constraints=[
                {
                    "roll_angle": [-15, 45]
                }
            ]
        ),
        OCPlatform(
            name="mantis",
            mission_id="63",
            sensor_id="HRI",
            constraints=[
                {
                    "roll_angle": [-20, 20]
                }
            ]
        ),
        OCPlatform(
            name="phisat-2",
            mission_id="56",
            sensor_id="MultiScape100 CIS",
            constraints=[
                {
                    "roll_angle": [-15, 45]
                }
            ]
        ),
    ]
