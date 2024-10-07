import os
from fastapi import FastAPI
from app.api.api_v1.api import api_router
from app.core.config import settings
from app.services.pdf_service import PDFService
from app.services.gemini_service import GeminiService
from app.middleware.timing import TimingMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.services.langchain_gemini_service import LangchainGeminiService
from app.middleware.error_handler import error_handler_middleware

app = FastAPI(
  title=settings.PROJECT_NAME,
  openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.middleware("http")(error_handler_middleware)
app.add_middleware(TimingMiddleware)
app.add_middleware(RateLimitMiddleware, max_requests=100, window=60)
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
  os.makedirs(os.path.dirname(settings.FAISS_INDEX_PATH), exist_ok=True)
  app.state.pdf_service = PDFService()
  app.state.gemini_service = GeminiService()
  app.state.langchain_service = LangchainGeminiService()

@app.get("/")
async def root():
  return {"message": "Welcome to PDF Chat API"}