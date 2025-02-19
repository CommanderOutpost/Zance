# app/config.py

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # MongoDB URI: defaults to local if not provided.
    mongo_uri: str = Field("mongodb://localhost:27017", env="MONGO_URI")
    mongo_db_name: str = Field("remindria", env="MONGO_DB_NAME")
    # Redis URL: defaults to local if not provided.
    redis_url: str = Field("redis://localhost:6379", env="REDIS_URL")
    # OpenAI API Key: must be provided.
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    # JWT Secret key: defaults to a placeholder if not provided.
    secret_key: str = Field("your_jwt_secret", env="SECRET_KEY")

    openai_model: str = Field("gpt-4o-mini", env="OPENAI_MODEL")

    class Config:
        env_file = ".env"  # Tells pydantic to load variables from .env


# Instantiate the settings so other modules can import them.
settings = Settings()
