from enum import Enum
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class StorageBackend(str, Enum):
    DATABASE = "DATABASE"
    IN_MEMORY = "IN_MEMORY"

class Settings(BaseSettings):
    STORAGE_BACKEND: StorageBackend = StorageBackend.DATABASE
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/library_db"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()


def get_db_engine_and_factory(database_url: str):
    engine = create_engine(database_url, echo=False)
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine, session_factory
