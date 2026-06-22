import os
from urllib.parse import quote

from pydantic import SecretStr, PostgresDsn, Secret, computed_field
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=os.path.join(os.path.dirname(__file__), ".envs/.env"))

    TELEGRAM_API_KEY: SecretStr = SecretStr("secret")
    LOG_LEVEL: str = "INFO"

    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "yhbujnikmol,1"
    POSTGRES_DB: str = "postgres"

    @computed_field
    @property
    def POSTGRES_DSN(self) -> PostgresDsn:
        return Secret(MultiHostUrl.build(
            scheme="postgresql+asyncpg",
            username=quote(self.POSTGRES_USER, safe=""),
            password=quote(self.POSTGRES_PASSWORD, safe=""),
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB
        ))

    @computed_field
    @property
    def PERSISTENCE_POSTGRES_DSN(self) -> PostgresDsn:
        return Secret(MultiHostUrl.build(
            scheme="postgresql",
            username=quote(self.POSTGRES_USER, safe=""),
            password=quote(self.POSTGRES_PASSWORD, safe=""),
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB
        ))

    ADMIN_INTERFACE_PORT: int = 8001
    ADMIN_SECRET_KEY: SecretStr = SecretStr("secretkey")
    ADMIN_LOGIN: SecretStr = SecretStr("admin")
    ADMIN_PASSWORD: SecretStr = SecretStr("admin")

