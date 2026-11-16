"""Shared pytest fixtures for Library Management API tests."""

import os
from collections.abc import Generator

import pytest
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from starlette.testclient import TestClient
from testcontainers.postgres import PostgresContainer

from app.auth.users import Role, get_demo_token_for_role
from app.core.config import Settings, StorageBackend, get_db_engine_and_factory


@pytest.fixture(scope="session")
def postgres_container() -> Generator[PostgresContainer, None, None]:
    """Start one disposable PostgreSQL database for the entire pytest session."""
    with PostgresContainer(
        "postgres:18",
        username="postgres",
        password="postgres",
        dbname="library_test",
        driver="psycopg",
    ) as container:
        os.environ["DATABASE_URL"] = container.get_connection_url()
        yield container

    os.environ.pop("DATABASE_URL", None)


@pytest.fixture(scope="session")
def db_engine(postgres_container: PostgresContainer) -> Engine:
    """Return the SQLAlchemy engine configured for the temporary container."""
    from app.models import models  # noqa: F401

    engine, _ = get_db_engine_and_factory(Settings().DATABASE_URL)
    return engine


@pytest.fixture
def reset_database(db_engine: Engine) -> Generator[None, None, None]:
    """Give each integration test empty Member and Book tables."""
    from app.models.models import Base

    Base.metadata.drop_all(bind=db_engine)
    Base.metadata.create_all(bind=db_engine)
    yield
    Base.metadata.drop_all(bind=db_engine)


@pytest.fixture
def db_session(
    reset_database: None, db_engine: Engine
) -> Generator[Session, None, None]:
    """Provide one real SQLAlchemy Session for repository integration tests."""
    session_factory = sessionmaker(bind=db_engine, autoflush=False)
    with session_factory() as session:
        yield session
        session.rollback()


@pytest.fixture
def database_client(
    reset_database: None,
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[TestClient, None, None]:
    """Provide a TestClient running against the temporary PostgreSQL container."""
    monkeypatch.setenv("STORAGE_BACKEND", "DATABASE")
    from app.main import app

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def memory_client(
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[TestClient, None, None]:
    """Provide a TestClient whose lifespan selects the in-memory services."""
    monkeypatch.setenv("STORAGE_BACKEND", "IN_MEMORY")
    from app.main import app

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def demo_settings() -> Settings:
    """Load token settings without requiring a live PostgreSQL database."""
    return Settings(STORAGE_BACKEND=StorageBackend.IN_MEMORY)


@pytest.fixture
def member_headers(demo_settings: Settings) -> dict[str, str]:
    """Provide Authorization headers for a valid member token."""
    token = get_demo_token_for_role(Role.MEMBER, demo_settings)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(demo_settings: Settings) -> dict[str, str]:
    """Provide Authorization headers for a valid administrator token."""
    token = get_demo_token_for_role(Role.ADMIN, demo_settings)
    return {"Authorization": f"Bearer {token}"}
