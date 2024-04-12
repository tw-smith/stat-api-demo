from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel
from geojson_pydantic.features import Feature
from api.models import (
    Geometry,
    Opportunity,
    Order,
    Product,
    Provider,
    Link,
)
import requests
import json


OC_STAC_API_URL = "https://test.app.open-cosmos.com/api/data/v0/stac"
OC_MTO_URL = "https://test.app.open-cosmos.com/api/data/v1/tasking"
OC_TASKING_REQUESTS_URL = "https://test.app.open-cosmos.com/api/data/v1"


def convert_datetime_to_iso8601(date: datetime) -> str:
    return date.strftime("%Y-%m-%dT%H:%M:%SZ")


def convert_datetime_string_to_datetime(date: str) -> datetime:
    date = date.split(".")[0]
    date = f"{date}Z"
    return datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")


class ManualTaskingSearchRequest(BaseModel):
    instruments: list[dict[str, str]]
    areas_of_interest: list[dict[str, str | Feature]]
    # constraints: Optional[ProductConstraints]
    constraints: list
    start: datetime
    stop: datetime

    def to_json(self, **kwargs: Any):
        return self.json(by_alias=True, exclude_unset=True, **kwargs)


class ManualTaskingSwathRequest(BaseModel):
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
    platform: dict[str, float]
    imager: dict[str, str]


class Activity(BaseModel):
    mission_id: str
    start_date: datetime
    end_date: datetime
    type: str
    parameters: ActivityParameters

    class Config:
        json_encoders = {datetime: convert_datetime_to_iso8601}


class TaskingRequestRequest(BaseModel):
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


def oc_stac_collection_to_product(collection: dict) -> Product:
    # Validate the STAC collection, set defaults etc
    if "providers" not in collection:
        collection["providers"] = [Provider(name="OpenCosmos")]
    else:
        collection["providers"] = [
            Provider.parse_obj(provider) for provider in collection["providers"]
        ]
    if "keywords" not in collection:
        collection["keywords"] = []
    if "constraints" not in collection:
        collection["constraints"] = {}
    if "parameters" not in collection:
        collection["parameters"] = {}
    if collection["links"] is None:
        collection["links"] = []
    else:
        collection["links"] = [Link.parse_obj(link) for link in collection["links"]]

    return Product(
        id=collection["id"],
        title=collection["title"],
        description=collection["description"],
        constraints=collection["constraints"],
        parameters=collection["parameters"],
        license=collection["license"],
        links=collection["links"],
        keywords=collection["keywords"],
        providers=collection["providers"],
    )


def opportunity_to_mto_search_request(
    opportunity: Opportunity,
) -> ManualTaskingSearchRequest:
    return ManualTaskingSearchRequest(
        instruments=[{"mission_id": "55", "sensor_id": "MultiScape100 CIS"}],
        areas_of_interest=[
            {
                "name": "aoi_name",
                "geojson": Feature(
                    geometry=opportunity.geometry,
                    type="Feature",
                    properties={"test": "test"},
                ),
            }
        ],
        # constraints=opportunity.constraints, #TODO implement constraints
        constraints=list(),
        start=opportunity.start_date,
        stop=opportunity.end_date,
    )


def mto_search_response_to_opportunity_collection(
    response: dict, geometry: Geometry
) -> list[Opportunity]:
    opportunities = []
    for opportunity in response["data"]:
        start = str(opportunity["start"].split(".")[0])
        stop = str(opportunity["stop"].split(".")[0])
        opportunities.append(
            Opportunity(
                id="id",
                geometry=geometry,
                # TODO implement constraints
                datetime=f"{start}/{stop}",
                product_id="hard coded opp product id",
                constraints=None,
            )
        )
    return opportunities


def get_swath(oc_opp: dict, aoi: Geometry, token: str) -> dict:
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    payload = ManualTaskingSwathRequest(
        instrument={"mission_id": "55", "sensor_id": "MultiScape100 CIS"},
        area_of_interest={
            "name": "aoi_name",
            "geojson": Feature(
                geometry=aoi, type="Feature", properties={"test": "test"}
            ),
        },
        roll_angle=3.2,  # TODO get from constraints
        start=convert_datetime_string_to_datetime(oc_opp["data"][0]["start"]),
        stop=convert_datetime_string_to_datetime(oc_opp["data"][0]["stop"]),
    )

    mto_swath_response = requests.post(
        f"{OC_MTO_URL}/swath",
        data=json.dumps(payload.dict(), default=str, indent=4),
        headers=headers,
        timeout=10
    )

    return mto_swath_response.json()


def get_oc_opportunity(opportunity: Opportunity, token: str) -> dict:
    request_body = opportunity_to_mto_search_request(opportunity)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    response = requests.post(
        f"{OC_MTO_URL}/search",
        data=json.dumps(request_body.dict(), default=str, indent=4),
        headers=headers,
        timeout=10
    )
    return response.json()


def build_tasking_request_request(
    opportunity: Opportunity, token: str
) -> TaskingRequestRequest:
    oc_opp = get_oc_opportunity(opportunity, token)

    activity_parameters = ActivityParameters(
        platform={
            "roll_angle": 3.2,  # TODO get from constraints
        },
        imager={"name": "MultiScape100 CIS"},
    )

    activity = Activity(
        type="IMAGE_ACQUISITION",
        mission_id="55",
        start_date=convert_datetime_string_to_datetime(oc_opp["data"][0]["start"]),
        end_date=convert_datetime_string_to_datetime(oc_opp["data"][0]["stop"]),
        parameters=activity_parameters,
    )

    return TaskingRequestRequest(
        type="MANUAL",
        region_name="region_name",
        region=Feature(
            geometry=opportunity.geometry, type="Feature", properties={"test": "test"}
        ),
        parameters=None,
        activities=[activity],
        constraints=list(),
        instruments=[{"mission_id": "55", "sensor_id": "MultiScape100 CIS"}],
    )


class OpenCosmosBackend:
    async def find_opportunities(
        self, search: Opportunity, token: str
    ) -> list[Opportunity]:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        mto_search_response = requests.post(
            f"{OC_MTO_URL}/search",
            data=json.dumps(
                opportunity_to_mto_search_request(search).dict(), default=str, indent=4
            ),
            headers=headers,
            timeout=10
        )

        opportunities = mto_search_response_to_opportunity_collection(
            mto_search_response.json(), search.geometry
        )
        return opportunities

    async def find_products(self, token: str) -> list[Product]:
        headers = {"Authorization": f"Bearer {token}"}

        stac_collection_response = requests.get(
            f"{OC_STAC_API_URL}/collections", headers=headers
        )

        products = []
        for collection in stac_collection_response.json():
            products.append(oc_stac_collection_to_product(collection))

        return products

    async def place_order(self, order: Opportunity, token: str) -> Order:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        # swath = get_swath(order, token)

        tasking_request = build_tasking_request_request(order, token)

        project_id = "d4ecc3b7-d72c-4c5f-80c9-0f60d9755e6d"

        tasking_request_response = requests.post(
            f"{OC_TASKING_REQUESTS_URL}/projects/{project_id}/tasking/requests",
            data=tasking_request.to_json(),
            headers=headers,
            timeout=10
        )

        print(tasking_request_response.json())
        return Order(id=tasking_request_response.json()["data"]["id"])
