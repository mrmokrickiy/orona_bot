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

# Простое хранилище контекста в памяти
user_conversations = {}

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    # Начинаем новый диалог
    user_conversations[user_id] = [
        {"role": "system", "content": "Ты - умный помощник. Поддерживай контекст разговора."}
    ]
    
    welcome = """
🤖 *Привет! Я умный помощник с памятью* 

Теперь я помню наш разговор! 

*Команды:*
/clear - очистить историю
/help - справка

Просто общайся со мной - я запомню контекст! 🧠
    """
    bot.reply_to(message, welcome, parse_mode='Markdown')

@bot.message_handler(commands=['clear'])
def clear_context(message):
    user_id = message.from_user.id
    if user_id in user_conversations:
        user_conversations[user_id] = [
            {"role": "system", "content": "Ты - умный помощник. Поддерживай контекст разговора."}
        ]
    bot.reply_to(message, "🧹 История очищена! Начинаем заново.")

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = """
🆘 *Помощь*

*Команды:*
/start - начать новый диалог
/clear - очистить историю
/help - справка

*Память:*
• Запоминаю последние 6 сообщений
• Поддерживаю контекст разговора
• Отвечаю с учетом предыдущих сообщений

Просто пиши - я помню наш разговор! 💬
    """
    bot.reply_to(message, help_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        user_id = message.from_user.id
        user_message = message.text
        
        # Создаем контекст если его нет
        if user_id not in user_conversations:
            user_conversations[user_id] = [
                {"role": "system", "content": "Ты - умный помощник. Поддерживай контекст разговора."}
            ]
        
        # Добавляем сообщение пользователя
        user_conversations[user_id].append({"role": "user", "content": user_message})
        
        # Ограничиваем историю (6 последних сообщений + системное)
        if len(user_conversations[user_id]) > 7:
            user_conversations[user_id] = [user_conversations[user_id][0]] + user_conversations[user_id][-6:]
        
        # Отправляем в OpenAI
        bot.send_chat_action(message.chat.id, 'typing')
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=user_conversations[user_id],
            max_tokens=600
        )
        
        bot_response = response.choices[0].message.content
        
        # Добавляем ответ бота в историю
        user_conversations[user_id].append({"role": "assistant", "content": bot_response})
        
        # Снова ограничиваем историю
        if len(user_conversations[user_id]) > 7:
            user_conversations[user_id] = [user_conversations[user_id][0]] + user_conversations[user_id][-6:]
        
        bot.reply_to(message, bot_response)
        
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        bot.reply_to(message, "❌ Ошибка. Попробуй еще раз!")

if __name__ == '__main__':
    logger.info("🚀 Запускаю бота с памятью...")
    bot.infinity_polling()