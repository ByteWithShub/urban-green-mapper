from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str
    city: str = Field(default="Ottawa")
    user_type: str = Field(default="general")
    green_pct: float | None = None
    dense_pct: float | None = None
    mean_ndvi: float | None = None


class ChatResponse(BaseModel):
    answer: str