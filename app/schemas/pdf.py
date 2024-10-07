from pydantic import BaseModel

class PDFResponse(BaseModel):
  id: str
  message: str

class PDFListResponse(BaseModel):
  id: str
  title: str
  author: str
  number_of_pages: int