# Telegram Bot Psychologist with RAG

## Project Overview
- **Project name:** PsychoBot
- **Type:** Telegram Bot with AI (RAG)
- **Core functionality:** AI-powered psychological consultation bot that uses RAG to access consultation history and maintains patient medical records
- **Target users:** Patients seeking psychological support, psychologists managing patients

## Functionality Specification

### Core Features

1. **Telegram Bot Interface**
   - Start command `/start` - welcome message and registration
   - Menu with options: "Новая консультация", "История болезни", "Моя история консультаций"
   - Text conversation with AI psychologist

2. **RAG System for Consultation History**
   - Vector store using ChromaDB for embeddings
   - Indexing past consultations for context-aware responses
   - Semantic search through conversation history

3. **Patient Medical Records**
   - SQLite database for structured patient data
   - Store: personal info, symptoms, diagnoses, treatment plans, session notes
   - Each patient has unique ID linked to Telegram user ID

4. **AI Psychologist Responses**
   - Contextual responses based on consultation history
   - Professional psychological dialogue patterns
   - Memory of previous sessions

### Data Models

**Patient:**
- telegram_id (PK)
- name
- age
- registration_date
- last_consultation_date

**Consultation:**
- id (PK)
- patient_id (FK)
- timestamp
- user_message
- ai_response
- embedding (for RAG)

**MedicalRecord:**
- id (PK)
- patient_id (FK)
- record_type (symptom, diagnosis, treatment, note)
- content
- created_at

### Configuration
- All settings in `.env` file
- TELEGRAM_BOT_TOKEN
- TELEGRAM_API_ID
- TELEGRAM_API_HASH
- OPENAI_API_KEY (for embeddings)
- DATABASE_URL

### Docker
- Python 3.11 base image
- All dependencies in requirements.txt
- Volume for SQLite database persistence

## Acceptance Criteria
1. Bot starts via Docker and responds to /start
2. User can register and start consultation
3. AI responds contextually using RAG
4. Patient medical records are saved to SQLite
5. History is retrievable via semantic search
6. All sensitive data in .env
