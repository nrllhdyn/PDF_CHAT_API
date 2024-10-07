import uuid
import json
import os
from typing import List, Dict, Tuple, Any
from fastapi import UploadFile, HTTPException, Depends
from app.schemas.pdf import PDFListResponse
from pypdf import PdfReader
from app.core.config import settings
from app.utils.logger import logger
from app.services.langchain_gemini_service import LangchainGeminiService

class PDFService:
    def __init__(self, langchain_service: LangchainGeminiService = Depends()):
        self.pdf_dir = settings.PDF_STORAGE_DIR
        self.text_dir = os.path.join(settings.PDF_STORAGE_DIR, "extracted_text")
        self.langchain_service = langchain_service
        os.makedirs(self.pdf_dir, exist_ok=True)
        os.makedirs(self.text_dir, exist_ok=True)
        logger.info(f"PDFService initialized with storage directory: {self.pdf_dir}")

    async def get_pdf_path(self, pdf_id: str) -> str:
        """
        Get the file path for a specific PDF.
        """
        pdf_path = os.path.join(self.pdf_dir, f"{pdf_id}.pdf")
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF with id {pdf_id} not found")
        return pdf_path

    async def process_pdf(self, file: UploadFile) -> str:
        # Check file size
        file_size = await file.read()
        await file.seek(0)
        if len(file_size) > settings.MAX_PDF_SIZE:
            logger.warning(f"Attempted to upload file larger than {settings.MAX_PDF_SIZE} bytes")
            raise HTTPException(status_code=400, detail="File too large")

        pdf_id = str(uuid.uuid4())
        file_path = os.path.join(self.pdf_dir, f"{pdf_id}.pdf")
        
        try:
            # Save the uploaded file
            content = await file.read()
            with open(file_path, "wb") as pdf_file:
                pdf_file.write(content)
            
            # Extract text and metadata from PDF
            text, metadata = self._extract_text_and_metadata(file_path)
            
            # Save extracted text and metadata
            self._save_text_and_metadata(pdf_id, text, metadata)

            # Process and index the PDF content
            await self.langchain_service.process_pdf(pdf_id, text)

            self.langchain_service.check_index_contents()
            
            logger.info(f"Successfully processed PDF with ID: {pdf_id}")
            return pdf_id
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            raise HTTPException(status_code=500, detail="Error processing PDF")

    def _extract_text_and_metadata(self, file_path: str) -> Tuple[str, Dict]:
        try:
            with open(file_path, "rb") as file:
                reader = PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
                
                metadata = {
                    "title": reader.metadata.title if reader.metadata.title else "Unknown",
                    "author": reader.metadata.author if reader.metadata.author else "Unknown",
                    "number_of_pages": len(reader.pages)
                }
            logger.info(f"Extracted text and metadata from {file_path}")
            return text, metadata
        
        except Exception as e:
            logger.error(f"Error extracting text and metadata from {file_path}: {str(e)}")
            raise
        
    def split_text_into_chunks(self, text: str, chunk_size: int = 10000) -> List[str]:
        """
        Splits the text into smaller chunks for processing.

        Args:
            text (str): The text to split.
            chunk_size (int): The maximum size of each chunk.

        Returns:
            List[str]: A list of text chunks.
        """
        return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    
    def _save_text_and_metadata(self, pdf_id: str, text: str, metadata: Dict):
        text_file_path = os.path.join(self.text_dir, f"{pdf_id}.json")
        data = {
            "text": text,
            "metadata": metadata
        }
        try:
            with open(text_file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            logger.info(f"Saved text and metadata for PDF {pdf_id}")
        except Exception as e:
            logger.error(f"Error saving text and metadata for PDF {pdf_id}: {str(e)}")
            raise

    async def list_pdfs(self) -> List[PDFListResponse]:
        try:
            pdf_list = []
            for filename in os.listdir(self.pdf_dir):
                if filename.endswith('.pdf'):
                    pdf_id = filename[:-4]  # Remove .pdf extension
                    metadata_path = os.path.join(self.text_dir, f"{pdf_id}.json")
                        
                    if os.path.exists(metadata_path):
                        with open(metadata_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            metadata = data.get('metadata', {})
                            
                            pdf_list.append(PDFListResponse(
                                id=pdf_id,
                                title=metadata.get('title', 'Unknown'),
                                author=metadata.get('author', 'Unknown'),
                                number_of_pages=metadata.get('number_of_pages', 0)
                            ))
                    else:
                        # If metadata file doesn't exist, add basic info
                        pdf_list.append(PDFListResponse(
                            id=pdf_id,
                            title='Unknown',
                            author='Unknown',
                            number_of_pages=0
                        ))
                
            logger.info(f"Listed {len(pdf_list)} PDFs")
            return pdf_list
        except Exception as e:
            logger.error(f"Error listing PDFs: {str(e)}")
            raise HTTPException(status_code=500, detail="An error occurred while listing PDFs")    
            
    
    async def get_pdf_text(self, pdf_id: str) -> str:
        text_file_path = os.path.join(self.text_dir, f"{pdf_id}.json")
        try:
            if not os.path.exists(text_file_path):
                logger.warning(f"No text found for PDF with id {pdf_id}")
                raise HTTPException(status_code=404, detail="PDF not found")
            
            with open(text_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Retrieved text for PDF {pdf_id}")
            return data['text']
        except Exception as e:
            logger.error(f"Error retrieving text for PDF {pdf_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Error retrieving PDF text")