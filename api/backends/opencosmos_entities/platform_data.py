from typing import Any, List
from pydantic import BaseModel


class OCPlatform(BaseModel):
    name: str
    constraints: List[dict[str, Any]]


def get_available_oc_platforms() -> List[OCPlatform]:
    """
    Returns a list of available OpenCosmos platforms.
    """
    return [
        OCPlatform(
            name="menut",
            constraints=[
                {
                    "roll_angle": [-15, 45]
                }
            ]
        ),
        OCPlatform(
            name="alisio",
            constraints=[
                {
                    "roll_angle": [-15, 45]
                }
            ]
        ),
        OCPlatform(
            name="hammer",
            constraints=[
                {
                    "roll_angle": [-15, 45]
                }
            ]
        ),
        OCPlatform(
            name="platero",
            constraints=[
                {
                    "roll_angle": [-15, 45]
                }
            ]
        ),
        OCPlatform(
            name="mantis",
            constraints=[
                {
                    "roll_angle": [-20, 20]
                }
            ]
        ),
        OCPlatform(
            name="phisat-2",
            constraints=[
                {
                    "roll_angle": [-15, 45]
                }
            ]
        ),
    ]
