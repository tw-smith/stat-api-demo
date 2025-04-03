from typing import Optional
from geojson_pydantic.features import Feature
from pydantic import BaseModel, Field
from shapely import Geometry
from api.backends.opencosmos_entities.platform_data import get_available_oc_platforms
from api.backends.opencosmos_entities.utils import Range, convert_datetime_string_to_datetime
from api.models import (
    Link
)
from stapi_fastapi.models.shared import Link as StapiLink

import requests
import json
from api.backends.opencosmos_entities.transport import (
    CreateTaskingRequestRequest,
    ManualTaskingOrchestrationSearchRequest,
    ManualTaskingOrchestrationSearchResponse,
    ActivityParameters,
    Activity,
    ManualTaskingOrchestrationSwathRequest,
)
from fastapi import Request
from stapi_fastapi.models.opportunity import OpportunityPayload, Opportunity
from stapi_fastapi.models.order import OrderPayload, Order, OrderStatus, OrderStatusCode
from stapi_fastapi.models.product import (
    Product,
    Provider,
)
from pygeofilter.parsers.cql2_json import parse as parse_json

import os

from stapi_fastapi import OpportunityProperties, ProductRouter, OpportunityProperties
from returns.result import ResultE, Success, Failure
from returns.maybe import Maybe, Nothing

from api.tests_fastapi.shared import MyOrderParameters
from api.utils.filter import filter_opportunity

OC_STAC_API_URL = "https://test.app.open-cosmos.com/api/data/v0/stac"
OC_MTO_URL = "https://test.app.open-cosmos.com/api/data/v1/tasking"
OC_TASKING_REQUESTS_URL = "https://test.app.open-cosmos.com/api/data/v1"
OC_OPENAPP_PROD = ""

class MyOpportunityProperties(OpportunityProperties):
    roll_angle: float
    observational_zenith_angle: float
    sun_zenith_angle: float
    cloud_coverage: float

def extract_processing_level(product: Product) -> str | None:
    """Extracts the processing level from the STAC collection

    Args:
        collection (dict): The STAC collection
    Returns:
        str: The processing level
    """

    splits = product.id.split("-") 
    if len(splits) < 2:
        raise ValueError(f"Invalid product id {product}")
    processing_level = splits[1]
    return processing_level


def extract_platform_name(collection: dict) -> str | None:
    """Extracts the platform name from the STAC collection

    Args:
        collection (dict): The STAC collection
    Returns:
        str: The platform name
    """
    platform = collection.get("summaries", dict()).get("platform", None)
    if platform is not None:
        return platform[0]
    return None


def mission_and_sensor_id_for(product: Product) -> tuple[str, str]:
    """Returns the mission and sensor ID for a given platform

    Args:
        product (Product): The product
    Returns:
        tuple[str, str]: The mission and sensor ID
    """

    splits = product.id.split("-")
    if len(splits) < 2:
        raise ValueError(f"Invalid product id {product}")
    platform_name = splits[0]

    platform_data = next((platform for platform in get_available_oc_platforms() if platform.name.lower() == platform_name), None)
    if platform_data is None:
        raise ValueError(f"Platform data not found for {platform_name}")
    return platform_data.mission_id, platform_data.sensor_id

def oc_stac_collection_to_product(collection: dict) -> Product:
    """Converts a STAC collection to a STAPI Product
    Args:
        collection (dict): The STAC collection
    Returns:
        Product: The STAT Product
    """

    links = []
    for link in collection.get("links", []) if collection.get("links") is not None else []:
        if link["type"] != "":
            links.append(Link.model_validate(link))

    providers = []
    for provider in collection.get("providers", []):
        providers.append(Provider.model_validate(provider))

    # Add OC as a provider if not already present
    oc_provider = next((provider for provider in providers if provider.name == "Open Cosmos"), None)
    if oc_provider is None:
        providers.append(Provider(name="Open Cosmos"))


    # Get platform data
    platform_data = next((platform for platform in get_available_oc_platforms() if platform.name.lower() == extract_platform_name(collection)), None)
    if platform_data is None:
        raise ValueError(f"Platform data not found for {extract_platform_name(collection)}")

    constraints = collection.get("constraints", dict())
    if platform_data is not None:
        for constraint in platform_data.constraints:
            if constraint == "roll_angle":
                values = platform_data.constraints[constraint]
                constraints.update({constraint: values})
                
    class Constraints(BaseModel):
        roll_angle: float = Field(ge=constraints.get("roll_angle", [-45, 45])[0], le=constraints.get("roll_angle", [-45, 45])[1])
        observational_zenith_angle: float = Field(ge=0, le=60)
        sun_zenith_angle: float = Field(ge=0, le=180)
        cloud_coverage: float = Field(ge=0, le=100)

    return Product(
        id=collection.get("id", ""),
        title=collection.get("title", ""),
        description=collection.get("description", ""),
        constraints=Constraints,
        license=collection.get("license", ""),
        links=[],
        keywords=collection.get("keywords", []),
        providers=providers,
        create_order=create_order,
        search_opportunities=search_opportunities,
        search_opportunities_async=None,
        get_opportunity_collection=None,
        opportunity_properties=MyOpportunityProperties,
        order_parameters=MyOrderParameters,
    )

def opportunity_to_mto_search_request(
    opportunity: OpportunityPayload,
    product: Product
) -> ManualTaskingOrchestrationSearchRequest:
    """Converts a STAT Opportunity object into an MTO opportunity search request object

    Args:
        opportunity (Opportunity): The STAT Opportunity object

    Returns:
        ManualTaskingOrchestrationSearchRequest: The MTO opportunity search request object
    """

    mission_id, sensor_id = mission_and_sensor_id_for(product)

    return ManualTaskingOrchestrationSearchRequest(
        instruments=[{"mission_id": mission_id, "sensor_id": sensor_id}],
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
        constraints=[],
        start=opportunity.datetime[0],
        stop=opportunity.datetime[1],
    )


def mto_search_response_to_opportunity_collection(
    response: dict,
    token: str,
) -> list[Opportunity]:
    """Converts an MTO opportunity search response into a list of STAT Opportunities

    Args:
        response (dict): The MTO opportunity search response
        geometry (Geometry): The geometry of the search area

    Returns:
        list[Opportunity]: A list of STAT Opportunities (STAT Opportunity collection?)
    """



    opportunities = []
    for opportunity in response["data"]:
        start = str(opportunity["start"])
        stop = str(opportunity["stop"])
        
        # Call the Swath provider for each opportunity
        swath = get_swath(opportunity, opportunity["field_of_regard"]["footprint"]["geojson"]["geometry"], token)
        
        opportunities.append(
            Opportunity(
                id="id",
                type="Feature",
                geometry=swath["data"]["footprint"]["geojson"]["geometry"],
                # TODO implement constraints
                constraints=None,
                properties={"datetime": f"{start}/{stop}", 
                            "product_id": "hard coded opp product id",
                            "roll_angle": opportunity["suggested_roll"],
                            "sun_zenith_angle": opportunity["sza"],
                            "observational_zenith_angle": abs(opportunity["suggested_roll"]), #TODO use OZA instead of roll_steering
                            "cloud_coverage": opportunity["cloud_coverage"]["min_cloud_cover"]["forecast"]["cloud_cover_pc"] if opportunity.get("cloud_coverage") is not None else 25,
                },
                links=[]
            )
        )
    return opportunities


def get_swath(oc_opp: dict, aoi: Geometry, token: str) -> dict:
    """Builds the MTO swath request and sends it to the MTO service swath endpoint

    Args:
        oc_opp (dict): The OpenCosmos opportunity
        aoi (Geometry): The area of interest
        token (str): The user's token

    Returns:
        dict: The MTO swath response
    """

    headers = {
        "Authorization": f"{token}",
        "Content-Type": "application/json",
    }
    
    project_id = os.getenv("PROJECT_ID")
    if project_id is None:
        raise ValueError("PROJECT_ID environment variable not set")

    payload = ManualTaskingOrchestrationSwathRequest(
        instrument={"mission_id": oc_opp["mission_id"], "sensor_id": oc_opp["imager_id"]},
        area_of_interest={
            "name": "aoi_name",
            "geojson": Feature(
                geometry=aoi, type="Feature", properties={"test": "test"}
            ),
        },
        project_id=project_id,
        roll_angle=oc_opp["suggested_roll"],  # TODO get from constraints
        start=oc_opp["start"],
        stop=oc_opp["stop"],
    )

    mto_swath_response = requests.post(
        f"{OC_MTO_URL}/swath",
        data=json.dumps(payload.dict(), default=str, indent=4),
        headers=headers,
        timeout=10,
    )

    return mto_swath_response.json()


def get_oc_opportunity(opportunity: OpportunityPayload|OrderPayload, product: Product, token: str) -> ManualTaskingOrchestrationSearchResponse:
    """Gets an OpenCosmos opportunity from the MTO service opportunity search endpoint

    Args:
        opportunity (Opportunity): The STAT Opportunity object
        token (str): The user's token

    Returns:
        dict: The OpenCosmos opportunity search response
    """

    request_body = opportunity_to_mto_search_request(opportunity, product)
    headers = {
        "Authorization": f"{token}",
        "Content-Type": "application/json",
    }
    response = requests.post(
        f"{OC_MTO_URL}/search",
        data=request_body.to_json(),
        headers=headers,
        timeout=10,
    )

    return ManualTaskingOrchestrationSearchResponse.parse_obj(response.json()['data'][0])


def build_tasking_request_request(
    order: OrderPayload, product: Product, token: str
) -> CreateTaskingRequestRequest:
    """Builds an OC tasking request from a STAT order object

    Args:
        order (OrderPayload): The STAT order object
        token (str): The user's token

    Returns:
        CreateTaskingRequestRequest: The OC tasking request body"""

    oc_opp = get_oc_opportunity(order, product, token)

    activity_parameters = ActivityParameters(
        platform={
            "roll_angle": oc_opp.suggested_roll,  # TODO get from constraints
        },
        imager={"name": oc_opp.imager_id},
    )

    activity = Activity(
        type="IMAGE_ACQUISITION",
        mission_id=oc_opp.mission_id,
        start_date=oc_opp.start,
        end_date=oc_opp.stop,
        parameters=activity_parameters,
    )

    return CreateTaskingRequestRequest(
        type="MANUAL",
        region_name="STAPI Demo Works Woohoo",
        region=Feature(
            geometry=order.geometry, type="Feature", properties={"test": "test"}
        ),
        parameters=None,
        activities=[activity],
        constraints=list(),
        instruments=[{"mission_id": oc_opp.mission_id, "sensor_id": oc_opp.imager_id}],
    )


def generate_product_list(token: str) -> list[Product]:
    """Generates a list of products from the STAC API
    Returns:
        list[Product]: A list of products
    """

    headers = {"Authorization": f"Bearer {token}"}

    stac_collection_response = requests.get(
        f"{OC_STAC_API_URL}/collections", headers=headers
    )
    products = []
    for collection in stac_collection_response.json():
        if "--qa" in collection["id"]:
            continue
        platforms = collection.get("summaries", dict()).get("platform", None)
        [platform.lower() for platform in platforms] if platforms is not None else []
        if platforms is None:
            continue
        allowed_platforms = []
        [allowed_platforms.append(platform.name.lower()) for platform in get_available_oc_platforms()]
        if not set(platforms).issubset(allowed_platforms):
            continue
        products.append(oc_stac_collection_to_product(collection))
    return products


async def create_order(
    product_router: ProductRouter,
    order_payload: OrderPayload,
    request: Request,
) -> ResultE[Order]:
    """
    Create an order with the given payload using the Open Cosmos backend.
    
    Args:
        product_router (ProductRouter): The product router
        order_payload (OrderPayload): The order payload
        request (Request): The request object
    Returns:
        ResultE[Order]: A result object containing the order
    """
    product = product_router.product
    
    try:
        order = await place_order(product, order_payload, request.headers.get("Authorization"))
        return Success(order)
    except Exception as e:
        return Failure(e)


async def search_opportunities(product_router: ProductRouter,
                               search: OpportunityPayload,
                               next: str | None,
                               limit: int,
                               request: Request) -> ResultE[tuple[list[Opportunity], Maybe[str]]]:
    """Searches for opportunities using the Open Cosmos backend
    Args:
        product_router (ProductRouter): The product router
        search (OpportunityPayload): The STAT Opportunity object
        next (str | None): The next token for pagination
        limit (int): The limit for pagination
        request (Request): The request object
    Returns:
        ResultE[tuple[list[Opportunity], Maybe[str]]]: A result object containing the opportunities and the next token
    """

    try:
        opportunities = await find_opportunities(search, product_router.product, request.headers.get("Authorization"), request.base_url)
        return Success((opportunities, Nothing))
    except Exception as e:
        return Failure(e)


async def find_opportunities(
    search: OpportunityPayload, product: Product, token: str, base_url: str
) -> list[Opportunity]:
    """Finds opportunities from the MTO service and converts them to STAT Opportunities

    Args:
        search (OpportunityPayload): The STAT Opportunity object
        token (str): The user's token

    Returns:
        list[Opportunity]: A list of STAT Opportunities
    """

    headers = {
        "Authorization": f"{token}",
        "Content-Type": "application/json",
    }

    body = json.dumps(
            opportunity_to_mto_search_request(search, product).dict(), default=str, indent=4
        )

    mto_search_response = requests.post(
        f"{OC_MTO_URL}/search",
        data=body,
        headers=headers,
        timeout=10,
    )

    opportunities = mto_search_response_to_opportunity_collection(
        mto_search_response.json(), token
    )
    
    # Query the opportunities
    opportunities = filter_opportunity(parse_json(search.filter), opportunities)
    
    # Add links to opportunities
    for opportunity in opportunities:
        opp_json = opportunity.model_dump()
        
        opportunity.links = [
            StapiLink(
                rel="create-order",
                href=f"{base_url}products/{product.id}/orders",
                method="POST",
                type="application/json",
                body={"datetime": opp_json["properties"]["datetime"],
                      "geometry": opp_json["geometry"],
                      "filter": {},
                      "order_parameters": {}},
            )
        ]
    return opportunities


async def find_products(self, token: str) -> list[Product]:
    """Finds products from the STAC API and converts them to STAT Products

    Args:
        token (str): The user's token

    Returns:
        list[Product]: A list of STAT Products
    """

    headers = {"Authorization": f"Bearer {token}"}

    stac_collection_response = requests.get(
        f"{OC_STAC_API_URL}/collections", headers=headers
    )

    products = []
    for collection in stac_collection_response.json():
        if "--qa" in collection["id"]:
            continue
        platforms = collection.get("summaries", dict()).get("platform", None)
        [platform.lower() for platform in platforms] if platforms is not None else []
        if platforms is None:
            continue

        allowed_platforms = []
        [allowed_platforms.append(platform.name.lower()) for platform in get_available_oc_platforms()]
        if not set(platforms).issubset(allowed_platforms):
            continue
        products.append(oc_stac_collection_to_product(collection))

    return products


async def place_order(product: Product, order: OrderPayload, token: str) -> Order:
    """Takes a STAT opportunity and converts it to an OC tasking request and submits
    it to the Tasking Requests service.

    Args:
        order (Opportunity): The STAT Opportunity object
        token (str): The user's token

    Returns:
        Order: The order object
    """

    headers = {
        "Authorization": f"{token}",
        "Content-Type": "application/json",
    }

    tasking_request = build_tasking_request_request(order, product, token)

    project_id = os.getenv("PROJECT_ID")
    if project_id is None:
        raise ValueError("PROJECT_ID environment variable not set")

    tasking_request_response = requests.post(
        f"{OC_TASKING_REQUESTS_URL}/projects/{project_id}/tasking/requests",
        data=tasking_request.to_json(),
        headers=headers,
        timeout=10,
    )

    tasking_request = requests.get(
        f"{OC_TASKING_REQUESTS_URL}/tasking/requests/{tasking_request_response.json()['data']['id']}",
        headers=headers,
        timeout=10,
    ).json()["data"]

    return Order(id=tasking_request_response.json()["data"]["id"],
                 geometry=tasking_request["region"]["geometry"],
                 type="Feature",
                 properties={"product_id": product.id,
                             "created": tasking_request["created_at"],
                             "status": OrderStatus(timestamp=tasking_request["created_at"],
                                                   status_code=OrderStatusCode.received),
                             "search_parameters": {
                                 "geometry": order.geometry,
                                 "datetime": order.datetime,
                                 "filter": order.filter,
                             },
                             "opportunity_properties": {}, # TODO fill this
                             "order_parameters": order.order_parameters.model_dump()})
                #  links=[Link(href=)]) # TODO fill this
