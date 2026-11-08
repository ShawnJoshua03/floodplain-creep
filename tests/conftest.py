import uuid
from collections.abc import Iterator
from pathlib import Path

import psycopg
import pytest
from fastapi.testclient import TestClient
from pgserver.postgres_server import get_server

from api.main import create_app
from pipeline.io.city_config import load_city_config
from pipeline.io.database import apply_schema, connect
from tests.api_support import api_settings, seed_database, write_overlay_files


@pytest.fixture(scope="session")
def database_url(tmp_path_factory: pytest.TempPathFactory) -> Iterator[str]:
    server = get_server(tmp_path_factory.mktemp("postgres"))
    yield server.get_uri()
    server.cleanup()


@pytest.fixture
def schema_name() -> str:
    return f"test_{uuid.uuid4().hex[:10]}"


@pytest.fixture
def conn(database_url: str, schema_name: str) -> Iterator[psycopg.Connection]:
    connection = connect(database_url, schema_name)
    apply_schema(connection)
    yield connection
    connection.rollback()
    connection.execute(f'DROP SCHEMA "{schema_name}" CASCADE')
    connection.commit()
    connection.close()


@pytest.fixture
def client(conn: psycopg.Connection, database_url: str, schema_name: str, tmp_path: Path) -> Iterator[TestClient]:
    seed_database(conn, tmp_path, load_city_config().min_count_k)
    overlay_dir = tmp_path / "overlays"
    write_overlay_files(overlay_dir)
    with TestClient(create_app(api_settings(database_url, schema_name, overlay_dir))) as test_client:
        yield test_client
