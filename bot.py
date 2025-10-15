import os
import logging
import telebot
import openai
import requests
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
SERPER_API_KEY = os.getenv('SERPER_API_KEY')  # Бесплатный ключ для поиска

bot = telebot.TeleBot(TELEGRAM_TOKEN)
openai.api_key = OPENAI_API_KEY

# Хранилище контекста
user_conversations = {}

def search_google(query):
    """Поиск в интернете через Serper API (бесплатно)"""
    try:
        url = "https://google.serper.dev/search"
        payload = json.dumps({"q": query})
        headers = {
            'X-API-KEY': SERPER_API_KEY,
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, headers=headers, data=payload)
        results = response.json()
        
        # Форматируем результаты
        search_info = "🔍 *Результаты поиска:*\n\n"
        
        if 'organic' in results:
            for i, result in enumerate(results['organic'][:3], 1):
                title = result.get('title', '')
                link = result.get('link', '')
                snippet = result.get('snippet', '')[:150] + '...'
                search_info += f"{i}. *{title}*\n{snippet}\n{link}\n\n"
        
        return search_info
    except Exception as e:
        logger.error(f"Ошибка поиска: {e}")
        return "❌ Не удалось выполнить поиск"

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    user_conversations[user_id] = [
        {"role": "system", "content": "Ты - умный помощник с доступом к интернету. Используй актуальную информацию."}
    ]
    
    welcome = """
🤖 *Привет! Я умный помощник с доступом в интернет* 

*Что я умею:*
• 🔍 Искать актуальную информацию онлайн
• 💬 Поддерживать контекст разговора  
• 📊 Давать свежие данные и новости

*Команды:*
/search [запрос] - поиск в интернете
/clear - очистить историю
/help - справка

Просто спроси о чем-то актуальном! 🌐
    """
    bot.reply_to(message, welcome, parse_mode='Markdown')

@bot.message_handler(commands=['search', 'поиск'])
def search_command(message):
    try:
        query = message.text.replace('/search', '').replace('/поиск', '').strip()
        
        if not query:
            bot.reply_to(message, "🔍 Введи запрос для поиска:\n/search погода в Москве\n/search последние новости")
            return
        
        bot.reply_to(message, f"🔍 Ищу в интернете: '{query}'...")
        
        # Выполняем поиск
        search_results = search_google(query)
        
        # Отправляем результаты поиска
        if len(search_results) > 4096:
            for i in range(0, len(search_results), 4096):
                part = search_results[i:i+4096]
                if i == 0:
                    bot.reply_to(message, part, parse_mode='Markdown')
                else:
                    bot.send_message(message.chat.id, part, parse_mode='Markdown')
        else:
            bot.reply_to(message, search_results, parse_mode='Markdown')
            
    except Exception as e:
        bot.reply_to(message, "❌ Ошибка поиска")

@bot.message_handler(commands=['clear'])
def clear_context(message):
    user_id = message.from_user.id
    user_conversations[user_id] = [
        {"role": "system", "content": "Ты - умный помощник с доступом к интернету."}
    ]
    bot.reply_to(message, "🧹 История очищена!")

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = """
🆘 *Помощь по поиску*

*Команды:*
/search [запрос] - поиск в интернете
/clear - очистить историю
/help - справка

*Примеры запросов:*
/search погода в Москве сегодня
/search курс доллара
/search последние новости технологии
/search как приготовить пасту

*Поиск работает через Google и дает актуальные результаты!* 🔍
    """
    bot.reply_to(message, help_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        user_id = message.from_user.id
        user_message = message.text
        
        # Автоматически используем поиск для актуальных запросов
        search_keywords = ['погода', 'курс', 'новости', 'сегодня', 'сейчас', '2024', '2025', 'актуальн', 'свежие']
        
        if any(keyword in user_message.lower() for keyword in search_keywords):
            bot.reply_to(message, f"🔍 Запрос выглядит актуальным! Используй /search {user_message} для получения свежих данных из интернета.")
            return
        
        # Обычный ответ с контекстом
        if user_id not in user_conversations:
            user_conversations[user_id] = [
                {"role": "system", "content": "Ты - умный помощник."}
            ]
        
        user_conversations[user_id].append({"role": "user", "content": user_message})
        
        if len(user_conversations[user_id]) > 7:
            user_conversations[user_id] = [user_conversations[user_id][0]] + user_conversations[user_id][-6:]
        
        bot.send_chat_action(message.chat.id, 'typing')
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=user_conversations[user_id],
            max_tokens=600
        )
        
        bot_response = response.choices[0].message.content
        user_conversations[user_id].append({"role": "assistant", "content": bot_response})
        
        if len(user_conversations[user_id]) > 7:
            user_conversations[user_id] = [user_conversations[user_id][0]] + user_conversations[user_id][-6:]
        
        bot.reply_to(message, bot_response)
        
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        bot.reply_to(message, "❌ Ошибка. Попробуй еще раз!")

if __name__ == '__main__':
    logger.info("🚀 Запускаю бота с поиском...")
    bot.infinity_polling()