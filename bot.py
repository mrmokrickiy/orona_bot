import os
import logging
import telebot
import openai

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info("=== БОТ НАЧИНАЕТ ЗАПУСК ===")

# Получаем токены
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

logger.info(f"TELEGRAM_TOKEN: {'***' if TELEGRAM_TOKEN else 'MISSING'}")
logger.info(f"OPENAI_API_KEY: {'***' if OPENAI_API_KEY else 'MISSING'}")

if not TELEGRAM_TOKEN or not OPENAI_API_KEY:
    logger.error("❌ ТОКЕНЫ НЕ НАЙДЕНЫ!")
    exit(1)

bot = telebot.TeleBot(TELEGRAM_TOKEN)
openai.api_key = OPENAI_API_KEY

logger.info("✅ Токены загружены")

@bot.message_handler(commands=['start'])
def start(message):
    logger.info(f"Получена команда /start от {message.from_user.username}")
    bot.reply_to(message, "🤖 Привет! Я умный помощник. Задай любой вопрос!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        logger.info(f"Обрабатываю сообщение: {message.text}")
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты полезный AI-помощник. Отвечай подробно и по делу."},
                {"role": "user", "content": message.text}
            ],
            max_tokens=500
        )
        
        answer = response.choices[0].message.content
        logger.info("✅ Ответ сгенерирован")
        bot.reply_to(message, answer)
        
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        bot.reply_to(message, "❌ Ошибка обработки")

logger.info("🚀 Запускаю бота...")
bot.infinity_polling()