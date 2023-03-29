from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse

from datetime import datetime, timedelta

from api.backends.base import Backend
from api.backends import BACKENDS

from api.api_types import Search, OpportunityCollection

app = FastAPI(title="Tasking API")


@app.get("/")
async def redirect_home():
    return RedirectResponse("/docs")


@app.get("/opportunities", response_model=OpportunityCollection)
async def get_opportunities(
    request: Request,
    search: Search | None = None,
):
    if search is None:
        start_datetime = datetime.now()
        end_datetime = start_datetime + timedelta(days=40)
        product_id = "landsat-c2-l2"
        search = Search(
            datetime=f"{start_datetime.isoformat()}/{end_datetime.isoformat()}",
            product_id=product_id,
        )

    return await post_opportunities(request, search)


@app.post("/opportunities", response_model=OpportunityCollection)
async def post_opportunities(
    request: Request,
    search: Search,
):
    # get the right token and backend from the header
    backend = request.headers.get("backend", "historical")

    token = "this-is-not-a-real-token"
    if authorization := request.headers.get("authorization"):
        token = authorization.replace("Bearer ", "")

    if backend in BACKENDS:
        impl: Backend = BACKENDS[backend]
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Backend '{backend}' not in options: {list(BACKENDS.keys())}"
        )

    opportunity_collection = await impl.find_opportunities(
        search,
        token=token,
    )

    return opportunity_collection
