# InReflectBot 🤖

Telegram-бот психолог с RAG системой для доступа к истории консультаций и ведения истории болезни пациента.

## Возможности

- 📝 AI-психолог на основе GPT-4 с контекстной памятью
- 🔍 RAG система для семантического поиска по истории консультаций
- 📋 Ведение медицинской карты пациента
- 💾 Сохранение истории болезни в SQLite
- 🐳 Запуск в Docker

## Настройка "Памяти" (RAG)

Бот автоматически выбирает режим работы с векторной базой:

1. **Локальный режим (по умолчанию)**:
   - Если переменная `OPENAI_EMBEDDING_MODEL` в `.env` **пустая** или не задана.
   - Используется встроенная модель ChromaDB. Бесплатно, работает локально.
   - Данные сохраняются в коллекцию `consultations_local_v1`.

2. **Облачный режим (OpenAI / Custom API)**:
   - Если в `OPENAI_EMBEDDING_MODEL` указана модель (например, `text-embedding-3-small`).
   - Используются основной `OPENAI_API_KEY` и `OPENAI_BASE_URL` из настроек.
   - Позволяет повысить качество поиска по смыслу на русском языке.
   - Данные сохраняются в отдельную коллекцию (например, `consultations_text_embedding_3_small`).

> **Важно**: При переключении между режимами (локальный/облачный) старая история "памяти" не удаляется, но становится недоступной в новом режиме из-за несовместимости векторов.

## Установка и запуск



1. Клонируйте репозиторий и перейдите в папку проекта

2. Создайте файл `.env` на основе `.env.example`:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_API_ID=your_api_id_here
TELEGRAM_API_HASH=your_api_hash_here
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://your-private-api.com/v1
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

3. Запустите бота:

```bash
docker-compose up -d
```

## Команды бота

- `/start` - начать работу с ботом
- Кнопки меню для навигации

## Структура проекта

```
.
├── bot.py              # Основной файл бота
├── config.py           # Конфигурация
├── database.py         # Модели SQLAlchemy
├── rag.py              # RAG система
├── psychologist.py     # AI логика психолога
├── requirements.txt    # Зависимости
├── Dockerfile          # Docker образ
├── docker-compose.yml  # Docker Compose
└── .env.example        # Пример конфигурации
```

## Получение Telegram Bot Token

1. Откройте @BotFather в Telegram
2. Отправьте /newbot
3. Следуйте инструкциям для создания бота
4. Скопируйте токен в .env

## Требования

- Python 3.11+
- Docker и Docker Compose
- Telegram аккаунт
- OpenAI API ключ
