# PDF Chat API

## Project Overview

This PDF Chat API is a sophisticated system that combines modern web technologies, artificial intelligence, and efficient data processing techniques to create a powerful tool for interacting with PDF documents. The project leverages a Retrieval-Augmented Generation (RAG) approach, allowing users to engage in meaningful conversations about the content of uploaded PDFs.

### Key Technologies and Libraries:

1. **FastAPI**: A modern, fast (high-performance) web framework for building APIs with Python 3.6+ based on standard Python type hints.

2. **Gemini AI**: Utilized through the LangChain integration, Gemini AI provides advanced language understanding and generation capabilities.

3. **LangChain**: An open-source framework for developing applications powered by language models, used here to integrate Gemini AI and create a seamless chat experience.

4. **FAISS (Facebook AI Similarity Search)**: An efficient similarity search and clustering library for dense vectors, used to create and query our vector database.

5. **PyPDF2**: A library for reading and writing PDF files, used for extracting text content from uploaded PDFs.

6. **Pydantic**: Data validation and settings management using Python type annotations.

7. **Python-dotenv**: Used for managing environment variables.

8. **Pytest**: For comprehensive unit and integration testing of the application.

### Key Features and Implementations:

- **RAG (Retrieval-Augmented Generation)**: This project implements a RAG system, which enhances the AI's responses by retrieving relevant information from the processed PDFs before generating an answer.

- **Vector Database**: FAISS is used to create a vector database of the PDF contents, allowing for efficient similarity search when answering queries.

- **Long-form Output Generation**: An algorithm is implemented to handle output token limitations. It iteratively generates responses, concatenating them to provide comprehensive answers to complex queries.

- **Asynchronous Processing**: FastAPI's asynchronous capabilities are utilized for efficient handling of concurrent requests.

- **Rate Limiting**: Implemented to prevent API abuse and ensure fair usage.

- **Performance Metrics**: Custom middleware for logging performance metrics of API calls.

- **JSON Logging**: Structured logging in JSON format for easier log parsing and analysis.

The combination of these technologies and implementations results in a robust, scalable, and efficient system for PDF content interaction through a chat interface.

## Features

- Upload PDF files
- Extract text content from PDFs
- List uploaded PDFs with metadata
- Retrieve extracted text from specific PDFs
- Chat with PDF content using Gemini API
- Rate limiting for API endpoints
- Performance metrics logging

## Setup

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Set up your `.env` file with your Gemini API key
   - GEMINI_API_KEY=your_gemini_api_key_here
   - PDF_STORAGE_DIR= pdf_storage
   - LOG_LEVEL=INFO
   - LOG_FILE=app.log
   
6. Run the application: `uvicorn app.main:app --reload`

## API Documentation

Once the application is running, you can access the API documentation at `http://localhost:8000/docs`.

## API Endpoints

- `POST /api/v1/pdf/upload`: Upload a new PDF file
- `GET /api/v1/pdf/list`: List all uploaded PDFs
- `GET /api/v1/pdf/{pdf_id}/text`: Get extracted text from a specific PDF
- `POST /api/v1/chat/{pdf_id}/chat`: Chat with a specific PDF

## Testing

To run tests: `pytest tests/ -v`

You need to upload a PDF document named `sample.pdf` to the `tests/test_files/` directory for testing.

## Logging

Logs are written to both console and the file specified in `LOG_FILE`. The log level can be adjusted in the `.env` file. Logs are in JSON format for easy parsing and analysis.

## Performance Monitoring

The application includes performance metrics logging for API endpoints. You can analyze these logs to identify bottlenecks and optimize performance.

## Error Handling

The application includes centralized error handling and returns appropriate HTTP status codes and error messages.

## Future Improvements

- Implement user authentication and authorization for secure access to PDFs and chat functionality.
- Add support for concurrent PDF processing to improve performance with large numbers of uploads.
- Enhance chat capabilities with more advanced NLP features, such as sentiment analysis and entity recognition.
- Integrate additional AI models alongside Gemini AI to provide users with model selection options and potentially improve response quality through model ensembling.
- Develop a custom embedding algorithm to replace FAISS for potentially improved efficiency and customization in vector similarity search.
- Implement adaptive chunk sizing for PDF text splitting, optimizing for both processing speed and context relevance.
- Create a user-friendly web interface for easier interaction with the API.
- Add support for more document formats beyond PDFs (e.g., DOCX, TXT, EPUB).
- Implement a caching mechanism to speed up repeated queries on the same PDF content.
- Develop a feedback system for users to rate and improve AI responses over time.
- Add multi-language support for PDF content extraction and chat interactions.
- Implement privacy-preserving techniques for handling sensitive information in PDFs.
- Develop a plugin system to allow for easy extension of functionality by third-party developers.
- Create a dashboard for monitoring system performance, usage statistics, and AI model performance metrics.
- Implement a versioning system for PDFs to track changes and allow for querying specific versions of documents.
- Explore and implement more advanced RAG techniques, such as multi-hop reasoning or hybrid retrieval methods.


## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[MIT License](LICENSE) 