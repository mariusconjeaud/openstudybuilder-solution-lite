# pylint: disable=redefined-outer-name

import logging

import pytest
from starlette.testclient import TestClient

__all__ = ["app_client", "main_app"]

log = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def main_app(request):
    """Fixture to load the API application

    Intention to move this to a fixture is to increase the initial startup time,
    save on loading and initializing the whole app (which does tons of DB queries) if only a unit test is requested,
    and to isolate where the startup time is spent.
    """
    log.info("%s fixture: loading FastAPI application", request.fixturename)
    from clinical_mdr_api.main import app

    log.info("%s fixture: application loading completed", request.fixturename)
    return app


@pytest.fixture(scope="session")
def app_client(main_app, request):
    log.debug("%s fixture: creating shared TestClient", request.fixturename)
    return TestClient(main_app)
