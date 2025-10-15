import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Получение токенов из переменных окружения
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Проверка наличия токенов
if not TELEGRAM_TOKEN:
    logging.error("❌ TELEGRAM_TOKEN не установлен!")
    exit(1)
if not OPENAI_API_KEY:
    logging.error("❌ OPENAI_API_KEY не установлен!")
    exit(1)

logging.info("✅ Токены загружены успешно")

# Инициализация OpenAI клиента
client = OpenAI(api_key=OPENAI_API_KEY)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Привет! Я бот ORONA с интеграцией ChatGPT. Задайте мне вопрос!')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Просто напишите сообщение, и я отвечу с помощью ChatGPT!')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    logging.info(f"📨 Получено сообщение: {user_message}")
    
    try:
        # Отправляем запрос к OpenAI API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that responds in Russian."},
                {"role": "user", "content": user_message}
            ],
            max_tokens=500
        )
        
        bot_response = response.choices[0].message.content
        logging.info(f"🤖 Ответ от GPT: {bot_response}")
        
    except Exception as e:
        logging.error(f"❌ Ошибка OpenAI API: {e}")
        bot_response = "Извините, произошла ошибка при обработке вашего запроса."
    
    await update.message.reply_text(bot_response)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.error(f"❌ Ошибка: {context.error}")

async def main():
    try:
        # Создаем приложение
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # Добавляем обработчики
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        # Обработчик ошибок
        application.add_error_handler(error_handler)
        
        # Запускаем бота
        logging.info("🚀 Бот запускается...")
        await application.run_polling()
        
    except Exception as e:
        logging.error(f"❌ Критическая ошибка при запуске: {e}")
        exit(1)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())