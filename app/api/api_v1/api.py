from fastapi import APIRouter
from app.api.api_v1.endpoints import pdf,chat

api_router = APIRouter()

api_router = APIRouter()
api_router.include_router(pdf.router, prefix="/pdf", tags=["pdf"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])