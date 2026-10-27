import uuid
from urllib.parse import quote_plus

from dotenv import find_dotenv
from pydantic import UUID4, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class _Settings(BaseSettings):
    rabbitmq_host: str = "localhost"
    rabbitmq_port: int = 5672
    rabbitmq_user: str = "guest"
    rabbitmq_password: str = "guest"
    rabbitmq_vhost: str = "vhost"

    redis_host: str = "localhost"
    redis_password: str = ""
    redis_port: int = 6379
    redis_db: int = 0

    postgresql_host: str = "localhost"
    postgresql_port: int = 5432
    postgresql_user: str = "postgres"
    postgresql_password: str = "postgres"
    postgresql_db: str = "postgres"

    api_key: UUID4 = Field(default_factory=uuid.uuid4)

    model_config = SettingsConfigDict(
        env_file=find_dotenv(), env_file_encoding="utf-8", populate_by_name=True, extra="ignore"
    )

    @property
    def rabbitmq_url(self) -> str:
        return (
            f"amqp://{self.rabbitmq_user}:{quote_plus(self.rabbitmq_password)}@"
            f"{self.rabbitmq_host}:{self.rabbitmq_port}/"
        )

    @property
    def redis_url(self) -> str:
        return f"redis://:{quote_plus(self.redis_password)}@{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @property
    def postgresql_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgresql_user}:{self.postgresql_password}@"
            f"{self.postgresql_host}:{self.postgresql_port}/{self.postgresql_db}"
        )


settings = _Settings()
