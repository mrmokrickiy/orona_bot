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
            messages=[
                {
                    "role": "system", 
                    "content": """Ты - AI ассистент в стиле DeepSeek. Отвечай:
                    
1. 📚 ПОЛНО и РАЗВЕРНУТО - давай исчерпывающие ответы
2. 🎯 КОНКРЕТНО - без воды, только суть
3. 🔧 ПРАКТИЧЕСКИ - с примерами, кодом, инструкциями
4. 📋 СТРУКТУРНО - используй списки, шаги, разделы
5. 🤝 ПОЛЕЗНО - помогай решать реальные проблемы
6. 🔗 С ССЫЛКАМИ - рекомендуй проверенные ресурсы
7. 💡 С ОБЪЯСНЕНИЯМИ - не просто ответ, а почему так

Отвечай как опытный наставник, который хочет помочь, а не просто дать информацию."""
                },
                {
                    "role": "user", 
                    "content": message.text
                }
            ],
            max_tokens=2000
        )
        answer = response.choices[0].message.content
        bot.reply_to(message, answer)
            
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        bot.reply_to(message, "Извините, ошибка обработки")

if __name__ == '__main__':
    logger.info("🚀 Бот запускается...")
    bot.infinity_polling()