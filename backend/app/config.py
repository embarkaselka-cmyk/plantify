from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "نادي الصحفي الصغير - Newspaper Generator"
    app_version: str = "1.0.0"

    database_url: str = "sqlite:///./newspaper.db"

    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    ai_mode: Literal["online", "offline", "auto"] = Field(default="auto", alias="AI_MODE")

    ollama_host: str = Field(default="http://localhost:11434", alias="OLLAMA_HOST")
    ollama_model: str = Field(default="llama2", alias="OLLAMA_MODEL")

    cors_origins: list[str] = ["*"]

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
