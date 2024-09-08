# pylint: disable=unused-argument
# pylint: disable=redefined-outer-name
import pytest
from fastapi.testclient import TestClient

from consumer_api.consumer_api import system_app


@pytest.fixture(scope="module")
def api_client():
    """Create FastAPI test client"""
    yield TestClient(system_app)


@pytest.mark.parametrize(
    "path",
    [
        "/information",
        "/information/build-id",
        "/healthcheck",
    ],
)
def test_system_api_endpoints(api_client, path):
    response = api_client.get(path)
    assert response.status_code == 200
