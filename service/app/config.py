from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    ENV: str = "development"

    MINIO_ENDPOINT: str = "minio:9000"
    MINIO_ACCESS_KEY: str = ""
    MINIO_SECRET_KEY: str = ""

    S3_ENDPOINT: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_BUCKET: str
    S3_REGION: str

    class Config:
        env_file = ".env"


settings = Settings()
