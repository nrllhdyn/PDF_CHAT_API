import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.core.config import settings
from app.utils.logger import logger
from langchain.prompts import PromptTemplate

class LangchainGeminiService:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.3,
            top_p=1,
            top_k=1,
            system_message="You are an AI assistant that answers questions based on the provided PDF content. Always refer to the given context to answer questions."
        )
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=settings.GEMINI_API_KEY)
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=settings.GEMINI_API_KEY)
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=150)
        self.vectorstore = self._load_or_create_vectorstore()
        self.pdf_vectorstores = {}

    def _load_or_create_vectorstore(self):
        try:
            if os.path.exists(settings.FAISS_INDEX_PATH):
                logger.info(f"Loading existing FAISS index from {settings.FAISS_INDEX_PATH}")
                vectorstore = FAISS.load_local(settings.FAISS_INDEX_PATH, self.embeddings, allow_dangerous_deserialization=True)
                logger.info(f"FAISS index loaded with {len(vectorstore.index_to_docstore_id)} documents")
                return vectorstore
            else:
                logger.info(f"Creating new FAISS index at {settings.FAISS_INDEX_PATH}")
                vectorstore = FAISS.from_texts(["Initialize"], self.embeddings)
                vectorstore.save_local(settings.FAISS_INDEX_PATH)
                return vectorstore
        except Exception as e:
            logger.error(f"Error loading or creating FAISS index: {str(e)}")
            logger.info("Creating new FAISS index as fallback")
            vectorstore = FAISS.from_texts(["Initialize"], self.embeddings)
            vectorstore.save_local(settings.FAISS_INDEX_PATH)
            return vectorstore
        
    
    async def generate_long_answer(self,pdf_id: str,  query: str, max_tokens: int = 16392, max_iterations: int = 3) -> str:
        full_response = ""
        iteration = 0
        
        while len(full_response.split()) < max_tokens and iteration < max_iterations:
            current_query = query if iteration == 0 else f"Continue the previous answer. {query}"
            
            result = await self.query_pdf(pdf_id,current_query)
            response = result.split("Answer: ")[1].split("\n\nSources:")[0]
            
            full_response += " " + response
            
            if len(response.split()) < 100:  # Stop if the response is too short
                break
            
            iteration += 1
        
        sources = result.split("\n\nSources:")[1]
        return f"Answer: {full_response.strip()}\n\nSources: {sources}"

    async def process_pdf(self, pdf_id: str, text: str):
        chunks = self.text_splitter.split_text(text)
        logger.info(f"Split PDF {pdf_id} into {len(chunks)} chunks")

        vectorstore = FAISS.from_texts(chunks, self.embeddings, metadatas=[{"source": pdf_id}] * len(chunks))
        self.pdf_vectorstores[pdf_id] = vectorstore
        logger.info(f"Processed and indexed PDF {pdf_id}. Total documents in index: {len(chunks)}")


    async def query_pdf(self, pdf_id: str, query: str) -> str:
        if pdf_id not in self.pdf_vectorstores:
            raise ValueError(f"PDF with id {pdf_id} not found in the index")
        
        vectorstore = self.pdf_vectorstores[pdf_id]
        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
        
        prompt_template = """Use the following pieces of context to answer the question at the end. 

        {context}
        Question: {question}
        Answer:"""
        PROMPT = PromptTemplate(
            template=prompt_template, input_variables=["context", "question"]
        )
        
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": PROMPT},
        )
        
        result = qa_chain({"query": query})
        response = result['result']
        source_documents = result['source_documents']
        
        logger.info(f"Query for PDF {pdf_id}: {query}")
        logger.info(f"Response: {response}")
        for i, doc in enumerate(source_documents):
            logger.info(f"Source document {i+1}: Content={doc.page_content[:100]}..., Metadata={doc.metadata}")
        
        return f"Answer: {response}\n\nSources: {[doc.metadata.get('source', 'Unknown') for doc in source_documents]}"


    def check_index_contents(self):
        logger.info(f"Total documents in index: {len(self.vectorstore.index_to_docstore_id)}")
        for i, (index, doc_id) in enumerate(self.vectorstore.index_to_docstore_id.items()):
            doc = self.vectorstore.docstore.search(doc_id)
            logger.info(f"Document {i+1}: ID={doc_id}, Content={doc.page_content[:100]}...")