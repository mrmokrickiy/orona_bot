import os
import logging
import telebot
import openai
import time
import requests

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

bot = telebot.TeleBot(TELEGRAM_TOKEN)
openai.api_key = OPENAI_API_KEY

# Хранилище контекста
user_conversations = {}

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    user_conversations[user_id] = [
        {"role": "system", "content": "Ты - умный и полезный помощник. Отвечай подробно и по делу."}
    ]
    
    welcome = """
🤖 *Привет! Я стабильный умный помощник* 

*Что я умею:*
💬 Отвечать на любые вопросы
🧠 Помнить контекст разговора
⚡ Быстро восстанавливаться при сбоях

*Команды:*
/clear - очистить историю
/status - статус бота
/help - справка

Задавай вопросы - я всегда на связи! 🚀
    """
    bot.reply_to(message, welcome, parse_mode='Markdown')

@bot.message_handler(commands=['clear'])
def clear_context(message):
    user_id = message.from_user.id
    user_conversations[user_id] = [
        {"role": "system", "content": "Ты - умный помощник."}
    ]
    bot.reply_to(message, "🧹 История очищена! Начинаем заново.")

@bot.message_handler(commands=['status'])
def status_command(message):
    bot.reply_to(message, "✅ Бот работает стабильно! Пользователей в памяти: {}".format(len(user_conversations)))

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = """
🆘 *Помощь*

*Команды:*
/start - начать диалог
/clear - очистить историю  
/status - статус бота
/help - справка

*Особенности:*
• 🧠 Помню контекст разговора
• ⚡ Автовосстановление при сбоях
• 💬 Отвечаю на любые вопросы

Просто пиши - я всегда отвечу! ✨
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
                {"role": "system", "content": "Ты - умный помощник."}
            ]
        
        # Добавляем сообщение пользователя
        user_conversations[user_id].append({"role": "user", "content": user_message})
        
        # Ограничиваем историю
        if len(user_conversations[user_id]) > 7:
            user_conversations[user_id] = [user_conversations[user_id][0]] + user_conversations[user_id][-6:]
        
        # Показываем что бот "печатает"
        bot.send_chat_action(message.chat.id, 'typing')
        
        # Генерируем ответ
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=user_conversations[user_id],
            max_tokens=600
        )
        
        bot_response = response.choices[0].message.content
        
        # Добавляем ответ в историю
        user_conversations[user_id].append({"role": "assistant", "content": bot_response})
        
        # Снова ограничиваем историю
        if len(user_conversations[user_id]) > 7:
            user_conversations[user_id] = [user_conversations[user_id][0]] + user_conversations[user_id][-6:]
        
        # Отправляем ответ
        bot.reply_to(message, bot_response)
        
        logger.info(f"💬 Ответ отправлен пользователю {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка обработки: {e}")
        bot.reply_to(message, "❌ Временная ошибка. Попробуй отправить сообщение еще раз!")

def run_bot():
    """Запуск бота с обработкой ошибок соединения"""
    while True:
        try:
            logger.info("🚀 Запускаю бота...")
            bot.infinity_polling(timeout=60, long_polling_timeout=30)
            
        except telebot.apihelper.ApiTelegramException as e:
            if "Conflict" in str(e):
                logger.warning("⚠️ Обнаружено несколько экземпляров бота. Жду 10 секунд...")
                time.sleep(10)
            else:
                logger.error(f"❌ Ошибка Telegram API: {e}")
                time.sleep(5)
                
        except requests.exceptions.ConnectionError as e:
            logger.error(f"🔌 Ошибка соединения: {e}")
            logger.info("🔄 Перезапуск через 10 секунд...")
            time.sleep(10)
            
        except Exception as e:
            logger.error(f"❌ Критическая ошибка: {e}")
            logger.info("🔄 Перезапуск через 15 секунд...")
            time.sleep(15)

if __name__ == '__main__':
    logger.info("🤖 Бот инициализирован")
    run_bot()