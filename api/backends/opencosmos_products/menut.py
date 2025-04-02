from typing import Self
from fastapi import Request
from pydantic import BaseModel, Field, model_validator
from stapi_fastapi import OpportunityProperties, ProductRouter
from stapi_fastapi.models.order import (
    OrderParameters,
)
from stapi_fastapi.models.product import (
    Product,
    Provider,
    ProviderRole,
)
from stapi_fastapi.models.order import (
    Order,
    OrderPayload,
    OrderStatus,
    OrderStatusCode,
)


from stapi_fastapi.models.opportunity import (
    Opportunity,
    OpportunityCollection,
    OpportunityPayload,
    OpportunitySearchRecord,
    OpportunitySearchStatus,
    OpportunitySearchStatusCode,
)


from returns.maybe import Maybe, Nothing, Some
from returns.result import Failure, ResultE, Success
from api.backends.opencosmos_entities.utils import OffNadirRange
from api.tests_fastapi.backends import mock_create_order

provider = provider = Provider(
    name="Open Cosmos",
    description="Open Cosmos provider",
    roles=[ProviderRole.producer],  # Example role
    url="https://open-cosmos.com",  # Must be a valid URL
)

class MyProductConstraints(BaseModel):
    off_nadir: float = Field(ge=0, le=45)

class MyOpportunityProperties(OpportunityProperties):
    off_nadir: OffNadirRange

class MyOrderParameters(OrderParameters):
    pass

#def search_opportunities_wrapper(sat_id: str):
    # async def search_opportunities(
    #     product_router: ProductRouter,
    #     search: OpportunityPayload,
    #     next: str | None,
    #     limit: int,
    #     request: Request,
    # ) -> ResultE[tuple[list[Opportunity], Maybe[str]]]:
    #     print(sat_id)
        
    #     back = OpenCosmosBackend()
    #     try: 
    #         opportunities = await back.find_opportunities(search, request.headers.get("Authorization"))
    #         return Success((opportunities, Nothing))
    #     except Exception as e:
    #         return Failure(e)
        
    # return search_opportunities

# menut = Product(
#     id="test-menut",
#     title="Test Menut Product",
#     description="Test product for menut in test cluster",
#     license="CC-BY-4.0",
#     keywords=["menut", "satellite"],
#     providers=[provider],
#     links=[],
#     create_order=mock_create_order,
#     search_opportunities=search_opportunities_wrapper("55"),
#     search_opportunities_async=None,
#     get_opportunity_collection=None,
#     constraints=MyProductConstraints,
#     opportunity_properties=MyOpportunityProperties,
#     order_parameters=MyOrderParameters,
# )
