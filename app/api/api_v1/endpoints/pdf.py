from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.services.pdf_service import PDFService
from app.schemas.pdf import PDFResponse, PDFListResponse
from typing import List
from app.utils.logger import logger
from app.utils.metrics import PerformanceMetrics

router = APIRouter()

@router.post("/upload", response_model=PDFResponse)
@PerformanceMetrics.measure_time
async def upload_pdf(file: UploadFile = File(...), pdf_service: PDFService = Depends()):
  """
  Upload a PDF file.

  - **file**: The PDF file to upload (max 30MB)
  
  Returns:
  - **id**: Unique identifier for the uploaded PDF
  - **message**: Confirmation message
  """
  if not file.filename.endswith('.pdf'):
    logger.warning(f"Attempted to upload non-PDF file: {file.filename}")
    raise HTTPException(status_code=400, detail="Only PDF files are allowed")
  
  try:
    pdf_id = await pdf_service.process_pdf(file)
    logger.info(f"Successfully uploaded PDF with ID: {pdf_id}")
    return PDFResponse(id=pdf_id, message="PDF successfully uploaded and processed")
  
  except HTTPException as he:
    # Re-raise HTTP exceptions
    raise he
  
  except Exception as e:
    logger.error(f"Error uploading PDF: {str(e)}")
    raise HTTPException(status_code=500, detail="An unexpected error occurred while processing the PDF")

@router.get("/list", response_model=List[PDFListResponse])
@PerformanceMetrics.measure_time
async def list_pdfs(pdf_service: PDFService = Depends()):
  """
  List all uploaded PDFs.

  Returns a list of PDFs with their metadata:
  - **id**: Unique identifier of the PDF
  - **title**: Title of the PDF
  - **author**: Author of the PDF
  - **number_of_pages**: Number of pages in the PDF
  """
  try:
    pdfs = await pdf_service.list_pdfs()
    logger.info(f"Listed {len(pdfs)} PDFs")
    return pdfs
  
  except HTTPException as he:
    raise he
  
  except Exception as e:
    logger.error(f"Error listing PDFs: {str(e)}")
    raise HTTPException(status_code=500, detail="An error occurred while listing PDFs")
  
@router.get("/{pdf_id}/text", response_model=str)
@PerformanceMetrics.measure_time
async def get_pdf_text(pdf_id: str, pdf_service: PDFService = Depends()):
  """
  Get the extracted text from a specific PDF.

  - **pdf_id**: The unique identifier of the PDF

  Returns the full text content of the PDF.
  """
  try:
    return await pdf_service.get_pdf_text(pdf_id)
  
  except HTTPException as he:
    # Re-raise HTTP exceptions
    raise he
  except FileNotFoundError:
    logger.error(f"PDF not found: {str(e)}")
    raise HTTPException(status_code=404, detail="PDF not found")
  
  except Exception as e:
    logger.error(f"Error retrieving text for PDF {pdf_id}: {str(e)}")
    raise HTTPException(status_code=500, detail="An error occurred while retrieving PDF text")