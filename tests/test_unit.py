import pytest
from unittest.mock import patch, mock_open, AsyncMock, MagicMock
from app.services.pdf_service import PDFService
from app.services.langchain_gemini_service import LangchainGeminiService
from app.utils.logger import logger, JSONFormatter

@pytest.fixture
def pdf_service():
    return PDFService()

@pytest.fixture
def langchain_service():
    return LangchainGeminiService()

def test_pdf_text_extraction(pdf_service):
    mock_pdf_content = "This is a test PDF content"
    with patch('builtins.open', mock_open(read_data=b'dummy content')):
        with patch('app.services.pdf_service.PdfReader') as mock_pdf_reader:
            mock_pdf_reader.return_value.pages = [type('obj', (object,), {'extract_text': lambda: mock_pdf_content})]
            extracted_text, _ = pdf_service._extract_text_and_metadata("dummy_path.pdf")
            assert extracted_text == mock_pdf_content

@pytest.mark.asyncio
async def test_langchain_process_pdf(langchain_service):
    mock_pdf_id = "test_pdf_id"
    mock_text = "This is a test PDF content"
    with patch('app.services.langchain_gemini_service.FAISS') as mock_faiss:
        mock_faiss.from_texts.return_value = AsyncMock()
        await langchain_service.process_pdf(mock_pdf_id, mock_text)
        assert mock_pdf_id in langchain_service.pdf_vectorstores
        mock_faiss.from_texts.assert_called_once()

@pytest.mark.asyncio
async def test_langchain_query_pdf(langchain_service):
    mock_pdf_id = "test_pdf_id"
    mock_query = "What is the content?"
    mock_vectorstore = AsyncMock()
    langchain_service.pdf_vectorstores[mock_pdf_id] = mock_vectorstore
    
    with patch('app.services.langchain_gemini_service.RetrievalQA') as mock_qa:
        mock_qa.from_chain_type.return_value.return_value = {
            "result": "This is a test answer",
            "source_documents": [MagicMock(metadata={"source": mock_pdf_id})]
        }
        response = await langchain_service.query_pdf(mock_pdf_id, mock_query)
        assert "Answer: This is a test answer" in response
        assert f"Sources: ['{mock_pdf_id}']" in response

def test_logger_json_format():
    with patch.object(JSONFormatter, 'format') as mock_format:
        mock_format.return_value = '{"level": "INFO", "message": "Test log"}'
        logger.info("Test log")
        assert mock_format.call_count > 0 