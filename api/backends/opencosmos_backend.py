import datetime
from email import header
from math import prod
from operator import ge
from os import link
from re import A
from click import Option
import geojson_pydantic
from pystac import Collection
from typing import Optional, Any
from pydantic import BaseModel, Field
from geojson_pydantic.features import Feature
from api.models import Geometry, Opportunity, Product, ProductConstraints, Provider, Link
import requests
import json


OC_STAC_API_URL = "https://test.app.open-cosmos.com/api/data/v0/stac"
OC_MTO_URL = "https://test.app.open-cosmos.com/api/data/v1/tasking"


class ManualTaskingSearchRequest(BaseModel):
    instruments: list[dict[str, str]]
    areas_of_interest: list[dict[str, str | Feature]]
    #constraints: Optional[ProductConstraints]
    constraints: list
    start: datetime.datetime
    stop: datetime.datetime

    def to_json(self, **kwargs: Any):
        return self.json(by_alias=True, exclude_unset=True, **kwargs)
    
class ManualTaskingSwathRequest(BaseModel):
    instrument: dict[str, str]
    area_of_interest: dict[str, str | Feature]
    roll_angle: float
    start: datetime.datetime
    stop: datetime.datetime

    def to_json(self, **kwargs: Any):
        return self.json(by_alias=True, exclude_unset=True, **kwargs)


def oc_stac_collection_to_product(collection: dict) -> Product:
    # Validate the STAC collection, set defaults etc
    if "providers" not in collection:
        collection["providers"] = [Provider(name="OpenCosmos")]
    else:
        collection["providers"] = [Provider.parse_obj(provider) for provider in collection["providers"]]
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


def opportunity_to_mto_search_request(opportunity: Opportunity) -> ManualTaskingSearchRequest:
    return ManualTaskingSearchRequest(
        instruments=[
            {
                'mission_id': '55',
                'sensor_id': 'MultiScape100 CIS'
            }
        ],
        areas_of_interest=[
            {
                'name': 'aoi_name',
                'geojson': Feature(geometry=opportunity.geometry, type="Feature", properties={'test': 'test'})
            }
        ],
        #constraints=opportunity.constraints, #TODO implement constraints
        constraints = list(),
        start=opportunity.start_date,
        stop=opportunity.end_date,
    )


def mto_search_response_to_opportunity_collection(response: dict, geometry: Geometry) -> list[Opportunity]:
    opportunities = []
    for opportunity in response["data"]:
        start = str(opportunity["start"].split(".")[0])
        stop = str(opportunity["stop"].split(".")[0])
        opportunities.append(Opportunity(
            id="id",
            geometry=geometry,
            # TODO implement constraints
            datetime=f"{start}/{stop}",
            product_id="hard coded opp product id",
            constraints=None,
            )
        )
    return opportunities


def get_swath(opp: Opportunity, token: str) -> dict:
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    payload = ManualTaskingSwathRequest(
        instrument={
            'mission_id': '55',
            'sensor_id': 'MultiScape100 CIS'
        },
        area_of_interest={
            'name': 'aoi_name',
            'geojson': Feature(geometry=opp.geometry, type="Feature", properties={'test': 'test'})
        },
        roll_angle=41.0, #TODO get from constraints
        start=opp.start_date,
        stop=opp.end_date,
    )

    mto_swath_response = requests.post(
        f"{OC_MTO_URL}/swath", 
        data=json.dumps(payload.dict(), default=str, indent=4),
        headers=headers
    )

    return mto_swath_response.json()


class OpenCosmosBackend:
    async def find_opportunities(self, search: Opportunity, token: str) -> list[Opportunity]:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        mto_search_response = requests.post(
            f"{OC_MTO_URL}/search", 
            data=json.dumps(opportunity_to_mto_search_request(search).dict(), default=str, indent=4),
            headers=headers
        )
        
        opportunities = mto_search_response_to_opportunity_collection(mto_search_response.json(), search.geometry)
        test = get_swath(opportunities[0], token)
        return opportunities
    
    async def find_products(self, token: str) -> list[Product]:
        headers = {
            "Authorization": f"Bearer {token}"
        }

        stac_collection_response = requests.get(
            f"{OC_STAC_API_URL}/collections", 
            headers=headers
        )
        
        products = []
        for collection in stac_collection_response.json():
            products.append(oc_stac_collection_to_product(collection))

        return products

