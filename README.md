# PsychoBot 🤖

Telegram-бот психолог с RAG системой для доступа к истории консультаций и ведения истории болезни пациента.

## Возможности

- 📝 AI-психолог на основе GPT-4 с контекстной памятью
- 🔍 RAG система для семантического поиска по истории консультаций
- 📋 Ведение медицинской карты пациента
- 💾 Сохранение истории болезни в SQLite
- 🐳 Запуск в Docker

## Установка

1. Клонируйте репозиторий и перейдите в папку проекта

2. Создайте файл `.env` на основе `.env.example`:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_API_ID=your_api_id_here
TELEGRAM_API_HASH=your_api_hash_here
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=sqlite:///psychobot.db
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
