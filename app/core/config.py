import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
  API_V1_STR: str = "/api/v1"
  PROJECT_NAME: str = "PDF Chat API"
  GEMINI_API_KEY: str
  PDF_STORAGE_DIR: str = os.path.join(os.getcwd(), "pdf_storage")
  LOG_LEVEL: str = "INFO"
  LOG_FILE: str = "app.log"
  MAX_PDF_SIZE: int = 30 * 1024 * 1024
  FAISS_INDEX_PATH: str = os.path.join(os.getcwd(), "faiss_index")

  model_config = SettingsConfigDict(env_file=".env")

settings = Settings()