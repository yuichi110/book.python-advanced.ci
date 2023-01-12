import pytest
from myapp.service import IndexService


@pytest.fixture
def indexservice_instance():
    return IndexService()


def test_serve(indexservice_instance: IndexService):
    result = indexservice_instance.serve()
    assert result == {"Hello": "World"}
