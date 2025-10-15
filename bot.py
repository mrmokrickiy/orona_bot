import os
import logging
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import openai

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получение токенов
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if not TELEGRAM_TOKEN or not OPENAI_API_KEY:
    logger.error("❌ Токены не установлены!")
    exit(1)

logger.info("✅ Токены загружены")

# Настройка OpenAI
openai.api_key = OPENAI_API_KEY

def start_command(update, context):
    update.message.reply_text('Привет! Я бот ORONA с ChatGPT. Задай вопрос!')

def help_command(update, context):
    update.message.reply_text('Просто напиши сообщение - я отвечу через GPT!')

def handle_message(update, context):
    try:
        user_message = update.message.text
        logger.info(f"📨 Получено: {user_message}")
        
        # Запрос к OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}],
            max_tokens=500
        )
        
        answer = response.choices[0].message.content
        update.message.reply_text(answer)
        
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        update.message.reply_text("Ошибка обработки запроса")

def error_handler(update, context):
    logger.error(f"Ошибка: {context.error}")

def main():
    try:
        # Создаем updater
        updater = Updater(TELEGRAM_TOKEN, use_context=True)
        dp = updater.dispatcher
        
        # Добавляем обработчики
        dp.add_handler(CommandHandler("start", start_command))
        dp.add_handler(CommandHandler("help", help_command))
        dp.add_handler(MessageHandler(Filters.text, handle_message))
        dp.add_error_handler(error_handler)
        
        # Запускаем бота
        logger.info("🚀 Бот запускается...")
        updater.start_polling()
        updater.idle()
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        exit(1)

if __name__ == '__main__':
    main()