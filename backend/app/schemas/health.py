from pydantic import BaseModel


class RootResponse(BaseModel):
    message: str
    status: str
    version: str


class HealthResponse(BaseModel):
    status: str
    service: str