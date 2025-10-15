import os
import logging
import telebot
import openai

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токены
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if not TELEGRAM_TOKEN:
    logger.error("❌ TELEGRAM_TOKEN не установлен!")
    exit(1)
if not OPENAI_API_KEY:
    logger.error("❌ OPENAI_API_KEY не установлен!")
    exit(1)

logger.info("✅ Токены загружены")

# Инициализация
bot = telebot.TeleBot(TELEGRAM_TOKEN)
openai.api_key = OPENAI_API_KEY

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message.text}],
            max_tokens=3500  # Максимум для Telegram
        )
        answer = response.choices[0].message.content
        
        # Проверяем длину и разбиваем если нужно
        if len(answer) > 4096:
            # Разбиваем на части по 4096 символов
            for i in range(0, len(answer), 4096):
                part = answer[i:i+4096]
                if i == 0:
                    bot.reply_to(message, part)
                else:
                    bot.send_message(message.chat.id, part)
        else:
            bot.reply_to(message, answer)
            
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        bot.reply_to(message, "Извините, ошибка обработки")

if __name__ == '__main__':
    logger.info("🚀 Бот запускается...")
    bot.infinity_polling()