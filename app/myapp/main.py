from fastapi import FastAPI
from myapp.const import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD
from myapp.service import ItemService
from myapp.repository import Repository

app = FastAPI()


@app.get("/api/v1/items/")
async def get_items():
    service = ItemService(get_repository())
    return {"items": service.get_items()}


@app.post("/api/v1/items/{item_name}")
async def add_item(item_name):
    service = ItemService(get_repository())
    service.add_item(item_name)
    return {}


def get_repository():
    return Repository(DB_HOST, DB_NAME, DB_USER, DB_PASSWORD)
