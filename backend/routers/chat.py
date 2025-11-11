from fastapi import APIRouter
from pydantic import BaseModel
from services.llm_service import insuranceAI


router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    message: str


@router.post("/")
async def chat_endpoint(request: ChatRequest):
    user_message = request.message

    reply = insuranceAI(user_message)
    return {"reply": reply}