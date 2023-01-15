import pytest
from myapp.const import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD
from myapp.service import ItemService
from myapp.repository import Repository


@pytest.fixture
def service():
    repository = Repository(DB_HOST, DB_NAME, DB_USER, DB_PASSWORD)
    return ItemService(repository)


@pytest.mark.order(1)
def test_delete_all_items(service: ItemService):
    service.delete_all_items()


@pytest.mark.order(2)
def test_add_item(service: ItemService):
    service.add_item("apple")


@pytest.mark.order(3)
def test_get_items(service: ItemService):
    items = service.get_items()
    item_names = [item["name"] for item in items]
    assert item_names == ["apple"]
