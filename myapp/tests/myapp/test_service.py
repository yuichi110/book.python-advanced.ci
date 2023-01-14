import pytest
from myapp.const import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD
from myapp.service import IndexService
from myapp.repository import Repository


@pytest.fixture
def service():
    repository = Repository(DB_HOST, DB_NAME, DB_USER, DB_PASSWORD)
    return IndexService(repository)


def test_add_item(service: IndexService):
    service.add_item("apple")


def test_get_items(service: IndexService):
    items = service.get_items()
    assert items == ["apple"]
