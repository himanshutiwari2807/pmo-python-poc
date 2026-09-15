from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Local-only defaults. Override via real environment variables if needed
    (e.g. DATABASE_URL=... uvicorn app.main:app). No .env file is used in this
    POC — these defaults match docker-compose.yml.
    """

    database_url: str = "mysql+aiomysql://pmo:pmopass@127.0.0.1:3307/pmo_poc"
    redis_url: str = "redis://127.0.0.1:6380/0"

    class Config:
        env_prefix = ""


settings = Settings()
