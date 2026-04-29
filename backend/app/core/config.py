from pydantic import BaseModel


class Settings(BaseModel):
    APP_NAME: str = "EarthLens"
    API_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"

    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "*",
    ]


settings = Settings()