import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
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

def start_command(update: Update, context: CallbackContext):
    update.message.reply_text('Привет! Я бот ORONA с интеграцией ChatGPT. Задайте мне вопрос!')

def help_command(update: Update, context: CallbackContext):
    update.message.reply_text('Просто напишите сообщение, и я отвечу с помощью ChatGPT!')

def handle_message(update: Update, context: CallbackContext):
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
    
    update.message.reply_text(bot_response)

def error_handler(update: Update, context: CallbackContext):
    logging.error(f"❌ Ошибка: {context.error}")

def main():
    try:
        # Создаем Updater и Dispatcher
        updater = Updater(TELEGRAM_TOKEN, use_context=True)
        dp = updater.dispatcher
        
        # Добавляем обработчики
        dp.add_handler(CommandHandler("start", start_command))
        dp.add_handler(CommandHandler("help", help_command))
        dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
        
        # Обработчик ошибок
        dp.add_error_handler(error_handler)
        
        # Запускаем бота
        logging.info("🚀 Бот запускается...")
        updater.start_polling()
        updater.idle()
        
    except Exception as e:
        logging.error(f"❌ Критическая ошибка при запуске: {e}")
        exit(1)

if __name__ == '__main__':
    main()