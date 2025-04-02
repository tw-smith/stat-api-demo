from multiprocessing import process
from typing import List
from geojson_pydantic.features import Feature
from api.backends.opencosmos_entities.platform_data import get_available_oc_platforms
from api.backends.opencosmos_entities.utils import OffNadirRange
from api.models import (
    Geometry,
    Order,
    Link,
)
import requests
import json
from api.backends.opencosmos_entities.transport import (
    CreateTaskingRequestRequest,
    ManualTaskingOrchestrationSearchRequest,
    ManualTaskingOrchestrationSearchResponse,
    ManualTaskingOrchestrationSwathRequest,
    ActivityParameters,
    Activity,
)
from fastapi import Request
from api.backends.opencosmos_entities.utils import convert_datetime_string_to_datetime, datetime_parser
from stapi_fastapi.models.opportunity import OpportunityPayload, Opportunity
from stapi_fastapi.models.product import (
    Product,
    Provider,
    ProviderRole,
)

from stapi_fastapi import ProductRouter
from returns.result import ResultE, Success, Failure
from returns.maybe import Maybe, Nothing, Some

from api.tests_fastapi.backends import mock_create_order
from api.tests_fastapi.shared import MyOrderParameters
from api.backends.opencosmos_products.menut import MyOpportunityProperties

OC_STAC_API_URL = "https://test.app.open-cosmos.com/api/data/v0/stac"
OC_MTO_URL = "https://test.app.open-cosmos.com/api/data/v1/tasking"
OC_TASKING_REQUESTS_URL = "https://test.app.open-cosmos.com/api/data/v1"

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
            constraints.update(constraint)

    return Product(
        id=collection.get("id", ""),
        title=collection.get("title", ""),
        description=collection.get("description", ""),
        constraints=constraints,
        license=collection.get("license", ""),
        links=[],
        keywords=collection.get("keywords", []),
        providers=providers,
        create_order=mock_create_order,
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
        constraints=[
        {
            "min": -15,
            "max": 15,
            "type": "ROLL"
        },
        {
            "min": 0,
            "max": 90,
            "type": "SZA"
        }
    ],
        start=opportunity.datetime[0],
        stop=opportunity.datetime[1],
    )


def mto_search_response_to_opportunity_collection(
    response: dict
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
        opportunities.append(
            Opportunity(
                id="id",
                type="Feature",
                geometry=opportunity["field_of_regard"]["footprint"]["geojson"]["geometry"],
                # TODO implement constraints
                constraints=None,
                properties={"datetime": f"{start}/{stop}", 
                            "product_id": "hard coded opp product id",
                            "off_nadir": OffNadirRange(minimum=20, maximum=22)},
                links=[],
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
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    payload = ManualTaskingOrchestrationSwathRequest(
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
        timeout=10,
    )

    return mto_swath_response.json()


def get_oc_opportunity(opportunity: Opportunity, token: str) -> ManualTaskingOrchestrationSearchResponse:
    """Gets an OpenCosmos opportunity from the MTO service opportunity search endpoint

    Args:
        opportunity (Opportunity): The STAT Opportunity object
        token (str): The user's token

    Returns:
        dict: The OpenCosmos opportunity search response
    """

    request_body = opportunity_to_mto_search_request(opportunity)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    response = requests.post(
        f"{OC_MTO_URL}/search",
        data=request_body.to_json(),
        headers=headers,
        timeout=10,
    )

    return ManualTaskingOrchestrationSearchResponse.parse_obj(response.json(object_hook=datetime_parser)['data'][0])


def build_tasking_request_request(
    opportunity: Opportunity, token: str
) -> CreateTaskingRequestRequest:
    """Builds an OC tasking request from a STAT Opportunity object

    Args:
        opportunity (Opportunity): The STAT Opportunity object
        token (str): The user's token

    Returns:
        CreateTaskingRequestRequest: The OC tasking request body"""

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
        start_date=oc_opp.start,
        end_date=oc_opp.stop,
        parameters=activity_parameters,
    )

    return CreateTaskingRequestRequest(
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
        opportunities = await find_opportunities(search, product_router.product, request.headers.get("Authorization"))
        return Success((opportunities, Nothing))
    except Exception as e:
        return Failure(e)


async def find_opportunities(
    search: OpportunityPayload, product: Product, token: str
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
        mto_search_response.json()
    )
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


async def place_order(self, order: Opportunity, token: str) -> Order:
    """Takes a STAT opportunity and converts it to an OC tasking request and submits
    it to the Tasking Requests service.

    Args:
        order (Opportunity): The STAT Opportunity object
        token (str): The user's token

    Returns:
        Order: The order object
    """

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
        timeout=10,
    )

    print(tasking_request_response.json())
    return Order(id=tasking_request_response.json()["data"]["id"])
