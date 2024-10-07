import google.generativeai as genai
from app.core.config import settings
from app.utils.logger import logger

class GeminiService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel("gemini-1.5-flash")


    async def generate_response(self, prompt: str) -> str:
        """
        Generates a response using the Gemini API.
        
        Args:
            prompt (str): The input prompt for the API.
        
        Returns:
            str: The generated response.
        
        Raises:
            Exception: If there's an error in API communication.
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error in Gemini API communication: {str(e)}")
            raise

    async def chat_with_pdf(self, pdf_content: str, user_question: str) -> str:
        """
        Generates a response to a user's question about a PDF.
        
        Args:
            pdf_content (str): The content of the PDF.
            user_question (str): The user's question.
        
        Returns:
            str: The generated response.
        """
        prompt = f"Based on the following PDF content:\n\n{pdf_content}\n\nAnswer the following question: {user_question}"
        return await self.generate_response(prompt)