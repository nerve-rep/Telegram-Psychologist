#%%
import chromadb
from chromadb.config import Settings
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from config import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_EMBEDDING_MODEL
import uuid


class RAGSystem:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL, model=OPENAI_EMBEDDING_MODEL)
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.collection_name = "consultations_v2"
        
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
        except:
            self.collection = self.client.create_collection(name=self.collection_name)

    def add_consultation(self, patient_id: int, user_message: str, ai_response: str):
        """Добавляет консультацию в векторную базу"""
        doc_id = str(uuid.uuid4())
        
        combined_text = f"Пациент: {user_message}\nПсихолог: {ai_response}"
        
        self.collection.add(
            documents=[combined_text],
            ids=[doc_id],
            metadatas=[{
                "patient_id": str(patient_id),  # ChromaDB хранит metadata как строки
                "user_message": user_message,
                "ai_response": ai_response
            }]
        )
        
        return doc_id

    def get_relevant_history(self, patient_id: int, query: str, n_results: int = 5):
        """Получает релевантную историю консультаций"""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where={"patient_id": str(patient_id)}  # Используем строку для фильтра
        )
        
        relevant_docs = []
        if results and results.get('documents'):
            for i, doc in enumerate(results['documents'][0]):
                if results['metadatas'] and len(results['metadatas']) > i:
                    meta = results['metadatas'][0][i]
                    relevant_docs.append({
                        'text': doc,
                        'user_message': meta.get('user_message', ''),
                        'ai_response': meta.get('ai_response', '')
                    })
        
        return relevant_docs

    def build_context(self, patient_id: int, current_message: str) -> str:
        """Строит контекст для AI на основе истории"""
        history = self.get_relevant_history(patient_id, current_message)
        
        if not history:
            return ""
        
        context = "Предыдущие консультации:\n"
        for h in history:
            context += f"\n---"
            context += f"\nПациент: {h['user_message']}"
            context += f"\nПсихолог: {h['ai_response']}"
        
        return context


rag_system = RAGSystem()