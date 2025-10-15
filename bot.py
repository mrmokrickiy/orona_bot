import os
import logging
import telebot
import openai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

bot = telebot.TeleBot(TELEGRAM_TOKEN)
openai.api_key = OPENAI_API_KEY

# Умный системный промпт
system_prompt = """Ты - умный и полезный AI-помощник. Отвечай:

🎯 КОНКРЕТНО - давай четкие, практические ответы
📚 ПОДРОБНО - объясняй темы глубоко, но доступно  
🔧 ПОЛЕЗНО - предлагай конкретные шаги и решения
💡 СТРУКТУРНО - используй списки, примеры, шаги

Избегай общих фраз. Будь настоящим помощником!"""

@bot.message_handler(commands=['start'])
def start(message):
    welcome = """
🤖 *Привет! Я твой умный помощник*

Просто напиши:
• Любой вопрос - отвечу подробно
• Попроси совет - дам практические рекомендации
• Попроси объяснить тему - расскажу простыми словами
• Опиши проблему - предложу решение

*Примеры:*
"Как научиться программировать?"
"Объясни что такое блокчейн"
"Помоги составить план тренировок"
"Напиши мотивационное письмо"

*Пиши что угодно - помогу!* 🚀
    """
    bot.reply_to(message, welcome, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        user_text = message.text
        
        # Показываем что бот думает
        bot.send_chat_action(message.chat.id, 'typing')
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text}
            ],
            max_tokens=1200
        )
        
        answer = response.choices[0].message.content
        
        # Отправляем ответ частями если он длинный
        if len(answer) > 4096:
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
        bot.reply_to(message, "❌ Произошла ошибка. Попробуй еще раз!")

if __name__ == '__main__':
    logger.info("🚀 Умный помощник запускается...")
    bot.infinity_polling()