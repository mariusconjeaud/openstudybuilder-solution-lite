"""Configuration parameters."""

import urllib.parse
from os import environ

from neomodel import config as neomodel_config
from pydantic import BaseSettings

DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f%z"
OPENAPI_SCHEMA_API_ROOT_PATH = environ.get("UVICORN_ROOT_PATH") or "/"
MAX_INT_NEO4J = 9223372036854775807
DEFAULT_PAGE_SIZE = 10
PAGE_SIZE_100 = 100
MAX_PAGE_SIZE = 1000


# Teach urljoin that Neo4j DSN URLs like bolt:// and neo4j:// semantically similar to http://
for scheme in ("bolt", "bolt+s", "neo4j", "neo4j+s"):
    urllib.parse.uses_relative.append(scheme)
    urllib.parse.uses_netloc.append(scheme)

neo4j_dsn = environ.get("NEO4J_DSN")
neomodel_config.DATABASE_URL = neo4j_dsn
db_name = environ.get("NEO4J_DATABASE")
if db_name:
    neomodel_config.DATABASE_URL = urllib.parse.urljoin(neo4j_dsn, f"/{db_name}")


class Settings(BaseSettings):
    app_name: str = "Clinical MDR API"
    neo4j_dsn: str | None
    neo4j_database: str = environ.get("NEO4J_DATABASE") or "neo4j"


settings = Settings()
