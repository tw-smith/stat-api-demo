import os
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import uvicorn


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

tk = os.environ.get("TOKEN")
if tk is None:
    raise ValueError("TOKEN environment variable not set")
available_products = generate_product_list(tk)

for product in available_products:
    root_router.add_product(product)

#root_router.add_product(menut)
app: FastAPI = FastAPI(lifespan=lifespan)
app.include_router(root_router, prefix="")

app.add_middleware(CORSMiddleware,
                   allow_origins=["*"],
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"],
)


if __name__ == "__main__":
    uvicorn.run(app=app, port=8000, host="0.0.0.0")