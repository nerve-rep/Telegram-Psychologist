import chromadb
import requests
from config import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_EMBEDDING_MODEL
import uuid

# Класс для облачных эмбеддингов (использует основной API-ключ и URL)
class CloudEmbeddingFunction:
    def __init__(self, api_key, base_url, model):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.model = model

    def __call__(self, input: list[str]):
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {"input": input, "model": self.model}
        
        try:
            response = requests.post(f"{self.base_url}/embeddings", json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            return [item["embedding"] for item in data["data"]]
        except Exception as e:
            print(f"❌ Ошибка API при получении эмбеддингов: {e}")
            raise e

class RAGSystem:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./chroma_db")
        
        # ЛОГИКА ВЫБОРА РЕЖИМА:
        # 1. Если указана модель - идем в облако через основной API
        if OPENAI_EMBEDDING_MODEL and OPENAI_EMBEDDING_MODEL.strip():
            print(f"🧬 RAG: Используется облачная модель {OPENAI_EMBEDDING_MODEL}")
            print(f"🔗 API URL: {OPENAI_BASE_URL}")
            self.embedding_fn = CloudEmbeddingFunction(
                api_key=OPENAI_API_KEY,
                base_url=OPENAI_BASE_URL,
                model=OPENAI_EMBEDDING_MODEL
            )
            # Имя коллекции зависит от модели, чтобы не было конфликтов
            self.collection_name = f"consultations_{OPENAI_EMBEDDING_MODEL.replace('-', '_')}"
        
        # 2. Иначе - работаем локально (бесплатно)
        else:
            print("🏠 RAG: Работа в локальном режиме (встроенная модель ChromaDB)")
            self.embedding_fn = None
            self.collection_name = "consultations_local_v1"
        
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_fn
        )

    def add_consultation(self, patient_id: int, user_message: str, ai_response: str):
        doc_id = str(uuid.uuid4())
        combined_text = f"Пациент: {user_message}\nПсихолог: {ai_response}"
        self.collection.add(
            documents=[combined_text],
            ids=[doc_id],
            metadatas=[{"patient_id": str(patient_id), "user_message": user_message, "ai_response": ai_response}]
        )
        return doc_id

    def get_relevant_history(self, patient_id: int, query: str, n_results: int = 5):
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where={"patient_id": str(patient_id)}
        )
        relevant_docs = []
        if results and results.get('documents') and len(results['documents']) > 0:
            for i, doc in enumerate(results['documents'][0]):
                if results['metadatas'] and len(results['metadatas'][0]) > i:
                    meta = results['metadatas'][0][i]
                    relevant_docs.append({
                        'text': doc,
                        'user_message': meta.get('user_message', ''),
                        'ai_response': meta.get('ai_response', '')
                    })
        return relevant_docs

    def build_context(self, patient_id: int, current_message: str) -> str:
        history = self.get_relevant_history(patient_id, current_message)
        if not history:
            return ""
        context = "Предыдущие консультации (релевантный контекст):\n"
        for h in history:
            context += f"\n---\nПациент: {h['user_message']}\nПсихолог: {h['ai_response']}"
        return context

rag_system = RAGSystem()