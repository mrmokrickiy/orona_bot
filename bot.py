import os
import logging
import telebot
import openai

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получение токенов из переменных окружения
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Инициализация OpenAI клиента
client = openai
client.api_key = OPENAI_API_KEY

async def start_command(update, context):
    await update.message.reply_text('Привет! Я бот ORONA с интеграцией ChatGPT. Задайте мне вопрос!')

async def help_command(update, context):
    await update.message.reply_text('Просто напишите сообщение, и я отвечу с помощью ChatGPT!')

async def handle_message(update, context):
    user_message = update.message.text
    
    try:
        # Отправляем запрос к OpenAI API
        response = client.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_message}
            ],
            max_tokens=500
        )
        
        bot_response = response.choices[0].message.content
        
    except Exception as e:
        logging.error(f"Error with OpenAI API: {e}")
        bot_response = "Извините, произошла ошибка при обработке вашего запроса."
    
    await update.message.reply_text(bot_response)

async def error_handler(update, context):
    logging.error(f"Update {update} caused error {context.error}")

def main():
    # Создаем приложение
    application = telebot.TeleBot(TELEGRAM_TOKEN)
    
    # Добавляем обработчики
    application.message_handler(commands=['start'])(start_command)
    application.message_handler(commands=['help'])(help_command)
    application.message_handler(func=lambda message: True)(handle_message)
    
    # Запускаем бота
    application.polling()

if __name__ == '__main__':
    main()