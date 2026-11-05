from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

ENV_FILE = Path(__file__).resolve().parent / ".env"

class Settings(BaseSettings):

    model_config = SettingsConfigDict(env_file=ENV_FILE)

    upbank_token: SecretStr
    database_url: str
    sync_interval: int = 300

settings = Settings()