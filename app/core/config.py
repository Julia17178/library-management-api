from enum import Enum
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class StorageBackend(str, Enum):
    DATABASE = "DATABASE"
    IN_MEMORY = "IN_MEMORY"

class Settings(BaseSettings):
    # Defaulting to DATABASE backend as required by your assignment rubric
    STORAGE_BACKEND: StorageBackend = StorageBackend.DATABASE
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/library_db"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

# Load configuration parameters once at app initialization
settings = Settings()

# Setup application-scoped SQLAlchemy engine and session factory
engine = create_engine(settings.DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
