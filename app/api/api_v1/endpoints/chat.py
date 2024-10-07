from fastapi import APIRouter, HTTPException, Depends, Query
from app.services.pdf_service import PDFService
from app.services.langchain_gemini_service import LangchainGeminiService
from app.utils.logger import logger
from app.utils.cache import get_cached_response, set_cached_response
from app.utils.metrics import PerformanceMetrics

router = APIRouter()

@router.post("/{pdf_id}")
@PerformanceMetrics.measure_time
async def chat_with_pdf(
  pdf_id: str,
  question: str = Query(..., min_length=5, max_length=500),
  pdf_service: PDFService = Depends(),
  langchain_service: LangchainGeminiService = Depends()
):
  """
  Chat with the content of a specific PDF using Langchain with Gemini API.

  - **pdf_id**: The unique identifier of the PDF
  - **question**: The user's question about the PDF content

  Returns the generated response using Langchain's RetrievalQA with Gemini API.
  """
  try:
    # Check if the response is already cached
    cached_response = get_cached_response(pdf_id, question)
    if cached_response:
      logger.info(f"Returning cached response for PDF {pdf_id} with question: {question}")
      return {"response": cached_response}
      
    # Ensure the PDF content is in the vector store
    if pdf_id not in langchain_service.pdf_vectorstores:
      pdf_text = await pdf_service.get_pdf_text(pdf_id)
      await langchain_service.process_pdf(pdf_id, pdf_text)

      # Query the PDF using Langchain with Gemini
      response = await langchain_service.generate_long_answer(pdf_id, question, max_tokens=16392, max_iterations=5)
        
      # Cache the response
      set_cached_response(pdf_id, question, response)

      logger.info(f"Generated response for PDF {pdf_id} with question: {question}")
      return {"response": response}
  except ValueError as ve:
    logger.error(f"PDF not found: {str(ve)}")
    raise HTTPException(status_code=404, detail=str(ve))
  except Exception as e:
    logger.error(f"Error during chat with PDF {pdf_id}: {str(e)}")
    raise HTTPException(status_code=500, detail="An error occurred while generating the response")