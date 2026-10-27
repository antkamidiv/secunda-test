from urllib.parse import quote_plus

from dotenv import find_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


class _Settings(BaseSettings):
    rabbitmq_host: str = "localhost"
    rabbitmq_port: int = 5672
    rabbitmq_user: str = "guest"
    rabbitmq_password: str = "guest"
    rabbitmq_vhost: str = "vhost"

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str = ""
    redis_db: int = 0

    postgresql_host: str = "localhost"
    postgresql_port: int = 5432
    postgresql_user: str = "postgres"
    postgresql_password: str = "postgres"
    postgresql_db: str = "postgres"

    model_config = SettingsConfigDict(env_file=find_dotenv(), env_file_encoding="utf-8", extra="ignore")

    @property
    def rabbitmq_url(self) -> str:
        return (
            f"amqp://{self.rabbitmq_user}:{quote_plus(self.rabbitmq_password)}@"
            f"{self.rabbitmq_host}:{self.rabbitmq_port}/"
        )

    @property
    def redis_url(self) -> str:
        return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @property
    def postgresql_url(self) -> str:
        return (
            f"postgresql://{self.postgresql_user}:{quote_plus(self.postgresql_password)}@"
            f"{self.postgresql_host}:{self.postgresql_port}/{self.postgresql_db}"
        )


settings = _Settings()
