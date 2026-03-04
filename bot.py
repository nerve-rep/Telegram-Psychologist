from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

from config import TELEGRAM_BOT_TOKEN
from database import init_db, SessionLocal, Patient, Consultation, MedicalRecord
from psychologist import generate_response
from datetime import datetime

# Состояния для ConversationHandler
NAME, AGE, MAIN_MENU, CONSULTATION, MEDICAL_RECORD_TYPE, MEDICAL_RECORD_CONTENT = range(6)

# Клавиатуры
def get_main_keyboard():
    keyboard = [
        [KeyboardButton("📝 Новая консультация")],
        [KeyboardButton("📋 История болезни")],
        [KeyboardButton("📜 Моя история консультаций")],
        [KeyboardButton("🏥 Медицинская карта")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_medical_record_keyboard():
    keyboard = [
        [KeyboardButton("🤒 Симптомы")],
        [KeyboardButton("📝 Заметки")],
        [KeyboardButton("🔙 Назад в меню")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    await update.message.reply_text(
        "👋 Привет! Я - бот-психолог.\n\n"
        "Я помогу вам с психологической поддержкой и буду вести историю ваших консультаций.\n"
        "Для начала работы, пожалуйста, представьтесь.",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton("Начать регистрацию")]],
            resize_keyboard=True
        )
    )
    return NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение имени пользователя"""
    user_id = update.effective_user.id
    name = update.message.text
    
    if name == "Начать регистрацию":
        await update.message.reply_text("Как вас зовут?")
        return NAME
    
    db = SessionLocal()
    try:
        patient = db.query(Patient).filter(Patient.telegram_id == user_id).first()
        
        if not patient:
            patient = Patient(telegram_id=user_id, name=name)
            db.add(patient)
        else:
            patient.name = name
            
        db.commit()
        
        context.user_data['patient_name'] = name
        await update.message.reply_text(
            f"Приятно познакомиться, {name}! 👋\n\n"
            "Сколько вам лет?",
            reply_markup=ReplyKeyboardMarkup([[]], resize_keyboard=True)
        )
        return AGE
    finally:
        db.close()


async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение возраста пользователя"""
    user_id = update.effective_user.id
    age_text = update.message.text
    
    try:
        age = int(age_text)
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите число.")
        return AGE
    
    db = SessionLocal()
    try:
        patient = db.query(Patient).filter(Patient.telegram_id == user_id).first()
        if patient:
            patient.age = age
            db.commit()
        
        await update.message.reply_text(
            f"Отлично! Регистрация завершена. ✅\n\n"
            "Выберите действие:",
            reply_markup=get_main_keyboard()
        )
        return MAIN_MENU
    finally:
        db.close()


async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик главного меню"""
    text = update.message.text
    user_id = update.effective_user.id
    
    db = SessionLocal()
    try:
        patient = db.query(Patient).filter(Patient.telegram_id == user_id).first()
        
        if not patient:
            await update.message.reply_text("Сначала зарегистрируйтесь /start")
            return MAIN_MENU
        
        if "Новая консультация" in text:
            await update.message.reply_text(
                "Начнём консультацию. 📝\n\n"
                "Расскажите, что вас беспокоит. Я вас слушаю.",
                reply_markup=ReplyKeyboardMarkup(
                    [[KeyboardButton("Завершить консультацию")]],
                    resize_keyboard=True
                )
            )
            return CONSULTATION
        
        elif "История болезни" in text:
            await show_medical_history(update, patient)
            return MAIN_MENU
        
        elif "Моя история консультаций" in text:
            await show_consultation_history(update, patient)
            return MAIN_MENU
        
        elif "Медицинская карта" in text:
            await update.message.reply_text(
                "Выберите тип записи:",
                reply_markup=get_medical_record_keyboard()
            )
            return MEDICAL_RECORD_TYPE
        
    finally:
        db.close()


async def handle_consultation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик консультации"""
    text = update.message.text
    user_id = update.effective_user.id
    
    if "Завершить консультацию" in text:
        await update.message.reply_text(
            "Консультация завершена. До следующей встречи! 👋\n\n"
            "Выберите действие:",
            reply_markup=get_main_keyboard()
        )
        
        # Обновляем дату последней консультации
        db = SessionLocal()
        try:
            patient = db.query(Patient).filter(Patient.telegram_id == user_id).first()
            if patient:
                patient.last_consultation_date = datetime.utcnow()
                db.commit()
        finally:
            db.close()
        
        return MAIN_MENU
    
    # Генерируем ответ
    await update.message.reply_text("Думаю над вашим сообщением... 🤔")
    
    db = SessionLocal()
    try:
        patient = db.query(Patient).filter(Patient.telegram_id == user_id).first()
        
        # Сохраняем сообщение в БД
        consultation = Consultation(
            patient_id=patient.id,
            user_message=text,
            ai_response=""
        )
        db.add(consultation)
        db.commit()
        
        # Генерируем ответ с RAG
        ai_response = generate_response(
            patient_id=patient.id,
            user_message=text,
            patient_name=patient.name
        )
        
        # Обновляем запись
        consultation.ai_response = ai_response
        db.commit()
        
        await update.message.reply_text(ai_response)
        
    except Exception as e:
        import traceback
        # Печатаем полную ошибку в консоль сервера
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА В handle_consultation:")
        traceback.print_exc()
        
        # Пользователю отправляем вежливое общее сообщение
        await update.message.reply_text("Извините, произошла техническая ошибка. Пожалуйста, попробуйте позже.")
    finally:
        db.close()
    
    return CONSULTATION


async def show_medical_history(update: Update, patient: Patient):
    """Показывает историю болезни"""
    db = SessionLocal()
    try:
        records = db.query(MedicalRecord).filter(
            MedicalRecord.patient_id == patient.id
        ).order_by(MedicalRecord.created_at.desc()).limit(10).all()
        
        if not records:
            await update.message.reply_text(
                "История болезни пуста. 📋\n\n"
                "Выберите действие:",
                reply_markup=get_main_keyboard()
            )
            return
        
        response = "📋 Ваша история болезни:\n\n"
        for record in records:
            response += f"• [{record.record_type}] {record.content}\n"
            response += f"  📅 {record.created_at.strftime('%d.%m.%Y')}\n\n"
        
        await update.message.reply_text(
            response + "\nВыберите действие:",
            reply_markup=get_main_keyboard()
        )
    finally:
        db.close()


async def show_consultation_history(update: Update, patient: Patient):
    """Показывает историю консультаций"""
    db = SessionLocal()
    try:
        consultations = db.query(Consultation).filter(
            Consultation.patient_id == patient.id
        ).order_by(Consultation.timestamp.desc()).limit(5).all()
        
        if not consultations:
            await update.message.reply_text(
                "У вас пока нет консультаций. 📜\n\n"
                "Выберите действие:",
                reply_markup=get_main_keyboard()
            )
            return
        
        response = "📜 История ваших консультаций:\n\n"
        for cons in consultations:
            response += f"📅 {cons.timestamp.strftime('%d.%m.%Y %H:%M')}\n"
            response += f"Вы: {cons.user_message[:100]}...\n"
            response += f"Психолог: {cons.ai_response[:100]}...\n\n"
        
        await update.message.reply_text(
            response + "\nВыберите действие:",
            reply_markup=get_main_keyboard()
        )
    finally:
        db.close()


async def handle_medical_record_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик выбора типа медицинской записи"""
    text = update.message.text
    
    if "Назад в меню" in text:
        await update.message.reply_text(
            "Главное меню:",
            reply_markup=get_main_keyboard()
        )
        return MAIN_MENU
    
    if "Симптомы" in text:
        context.user_data['record_type'] = 'symptom'
        await update.message.reply_text("Опишите ваши симптомы:")
    elif "Заметки" in text:
        context.user_data['record_type'] = 'note'
        await update.message.reply_text("Введите заметку:")
    else:
        await update.message.reply_text("Выберите тип записи:", reply_markup=get_medical_record_keyboard())
        return MEDICAL_RECORD_TYPE
    
    return MEDICAL_RECORD_CONTENT


async def handle_medical_record_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохранение медицинской записи"""
    text = update.message.text
    user_id = update.effective_user.id
    record_type = context.user_data.get('record_type', 'note')
    
    db = SessionLocal()
    try:
        patient = db.query(Patient).filter(Patient.telegram_id == user_id).first()
        
        record = MedicalRecord(
            patient_id=patient.id,
            record_type=record_type,
            content=text
        )
        db.add(record)
        db.commit()
        
        await update.message.reply_text(
            "Запись сохранена! ✅\n\n"
            "Выберите действие:",
            reply_markup=get_main_keyboard()
        )
        return MAIN_MENU
    finally:
        db.close()


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена"""
    await update.message.reply_text(
        "Отменено. Главное меню:",
        reply_markup=get_main_keyboard()
    )
    return MAIN_MENU


def main():
    """Запуск бота"""
    # Инициализация БД
    init_db()
    
    # Создание приложения
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Обработчики
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start_command)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_age)],
            MAIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_main_menu)],
            CONSULTATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_consultation)],
            MEDICAL_RECORD_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_medical_record_type)],
            MEDICAL_RECORD_CONTENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_medical_record_content)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    app.add_handler(conv_handler)
    
    print("🤖 Бот запущен!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()