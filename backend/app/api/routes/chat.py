from fastapi import APIRouter

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import generate_chat_answer

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest):
    answer = generate_chat_answer(
        message=payload.message,
        city=payload.city,
        user_type=payload.user_type,
        green_pct=payload.green_pct,
        dense_pct=payload.dense_pct,
        mean_ndvi=payload.mean_ndvi,
    )

    return ChatResponse(answer=answer)