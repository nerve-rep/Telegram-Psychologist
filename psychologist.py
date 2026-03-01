from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_BASE_URL
from rag import rag_system


client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)


SYSTEM_PROMPT = """Ты - опытный психолог-психотерапевт с более чем 15-летним стажем работы. 
Ты проводишь консультации в теплой, эмпатичной и неосуждающей манере. 

Твои принципы:
1. Активно слушай и показывай понимание
2. Задавай уточняющие вопросы для лучшего понимания
3. Используй техники когнитивно-поведенческой терапии (КПТ)
4. Предлагай практические упражнения и техники самопомощи
5. Никогда не давай медицинские диагнозы - направляй к специалистам при необходимости
6. Поддерживай, но не давай ложных обещаний
7. Помни контекст предыдущих сессий

Отвечай на русском языке, кратко и по делу. Используй обращение на "ты"."""


def generate_response(patient_id: int, user_message: str, patient_name: str = None) -> str:
    """Генерирует ответ психолога с использованием RAG"""
    
    # Получаем контекст из истории
    context = rag_system.build_context(patient_id, user_message)
    
    # Формируем промпт
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    if context:
        messages.append({
            "role": "system", 
            "content": f"Контекст из предыдущих консультаций:\n{context}"
        })
    
    if patient_name:
        messages.append({
            "role": "system",
            "content": f"Имя пациента: {patient_name}"
        })
    
    messages.append({"role": "user", "content": user_message})
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        # Сохраняем в RAG
        rag_system.add_consultation(patient_id, user_message, ai_response)
        
        return ai_response
    
    except Exception as e:
        return f"Извините, произошла техническая ошибка. Пожалуйста, попробуйте позже. ({str(e)})"
