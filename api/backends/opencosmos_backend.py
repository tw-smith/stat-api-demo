from email import header
from math import prod
from pystac import Collection
from models import Opportunity, Product, Provider, Link
import requests


OC_STAC_API_URL = "https://app.open-cosmos.com/api/data/v0/stac"


def oc_stac_collection_to_product(collection: dict) -> Product:
    # TODO implement functionality to convert from OC STAC collection to STAT Produc
    return Product(
        id=collection["id"],
        title=collection["title"],
        description=collection["description"],
        #constraints=constraints,
        #parameters=parameters,
        license=collection["license"],
        links=[Link.parse_obj(link) for link in collection["links"]],
        keywords=collection["keywords"],
        providers=[Provider.parse_obj(provider) for provider in collection["providers"]],
    )


class OpenCosmosBackend:
    async def find_opportunities() -> list[Opportunity]:
        return []
    
    async def find_products(self, token: str) -> list[Product]:
        products = []
        headers = {
            "Authorization": f"Bearer {token}"
        }
        response = requests.get(f"{OC_STAC_API_URL}/collections", headers=headers)
        print(response.json())
        collections = response.json()
        for collection in collections:
            products.append(oc_stac_collection_to_product(collection))
        return products