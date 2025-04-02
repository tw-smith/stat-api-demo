import os
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI


from api.backends.opencosmos_backend import generate_product_list

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stapi_fastapi.models.conformance import  CORE, OPPORTUNITIES
from stapi_fastapi.routers.root_router import RootRouter
from api.tests_fastapi.backends import (
    mock_get_order,
    mock_get_order_statuses,
    mock_get_orders,
)
from api.tests_fastapi.shared import (
    InMemoryOpportunityDB,
    InMemoryOrderDB,
    product_test_satellite_provider_sync_opportunity,
    product_test_spotlight_sync_async_opportunity,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[dict[str, Any]]:
    try:
        yield {
            "_orders_db": InMemoryOrderDB(),
            "_opportunities_db": InMemoryOpportunityDB(),
        }
    finally:
        pass


root_router = RootRouter(
    get_orders=mock_get_orders,
    get_order=mock_get_order,
    get_order_statuses=mock_get_order_statuses,
    get_opportunity_search_records=None,
    get_opportunity_search_record=None,
    conformances=[CORE, OPPORTUNITIES]
)
# root_router.add_product(product_test_spotlight_sync_async_opportunity)
# root_router.add_product(product_test_satellite_provider_sync_opportunity)

tk = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlJEVTFPRFExTURZd09VWXpOMFV6UTBWRE5EZEJRVFJHTUVZMk1FTkdNa0pHUmtZMVJqQkdPQSJ9.eyJpc3MiOiJodHRwczovL2xvZ2luLm9wZW4tY29zbW9zLmNvbS8iLCJzdWIiOiJnb29nbGUtYXBwc3x0b2J5LnNtaXRoQG9wZW4tY29zbW9zLmNvbSIsImF1ZCI6Imh0dHBzOi8vdGVzdC5iZWVhcHAub3Blbi1jb3Ntb3MuY29tIiwiaWF0IjoxNzQzNTg5NTI5LCJleHAiOjE3NDM1OTY3MjksInNjb3BlIjoibXNkIG9wcyBkYXRhIGhpbCBwb3J0YWwgdXNlciBzdWJqZWN0IHJlbGF0aW9uc2hpcCByb2xlIG1pc3Npb24gcHJvZ3JhbW1lIG9yZ2FuaXNhdGlvbiBlcGhlbWVyaXMiLCJhenAiOiJUdFkzYlJ2c1hvaEo1aDFEUzBhd2ZiNUhqZDA0SHhyMCJ9.n0oCH2omd3mlCBKEEvVMTZBHeLDu69vJKiFJyOT7B7j-HbQiONqDmeCcPj1h1LvB-03axyOtIVYKIdgjWrNkQvy1EQMxONFzPtcQ5zujU123_SUrXNLH97Gpjk-321LAiOqiMsEHggfXrG_Or3rEnKJ_E3VA69PtqFH7ihq7pR4oD7IBs7zEg2fcb2qLo-hH7meSmLnSu84zisJxuOkMhTNTAKbfyIXkKvkedFvefwy87jXnYCN6wz60MSoxlGoLsNBjP8_I3ELautJTHdHp11LnDYPKm877D5o8pSe6S3wUUBShAtszUVpMuKfEyIZJrnsNovw57SrS9ClUc5OiHw"
available_products = generate_product_list(tk)

for product in available_products:
    root_router.add_product(product)

#root_router.add_product(menut)
app: FastAPI = FastAPI(lifespan=lifespan)
app.include_router(root_router, prefix="")
