import os
import logging
import telebot
from openai import OpenAI

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

# Инициализация бота и OpenAI
bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = OpenAI(api_key=OPENAI_API_KEY)

@bot.message_handler(commands=['start'])
def start_command(message):
    bot.reply_to(message, 'Привет! Я бот ORONA с ChatGPT. Задай вопрос!')

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.reply_to(message, 'Просто напиши сообщение - я отвечу через GPT!')

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        user_message = message.text
        logger.info(f"📨 Получено: {user_message}")
        
        # Запрос к OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}],
            max_tokens=500
        )
        
        answer = response.choices[0].message.content
        bot.reply_to(message, answer)
        
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        bot.reply_to(message, "Ошибка обработки запроса")

if __name__ == '__main__':
    logger.info("🚀 Бот запускается...")
    bot.infinity_polling()