import os
import logging
import telebot
import openai
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

bot = telebot.TeleBot(TELEGRAM_TOKEN)
openai.api_key = OPENAI_API_KEY

# ========== УМНАЯ КЛАВИАТУРА ==========
def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton('💡 Попросить совет'),
        KeyboardButton('📚 Объяснить тему'), 
        KeyboardButton('🔧 Решить проблему'),
        KeyboardButton('📝 Написать текст'),
        KeyboardButton('💻 Помощь с кодом'),
        KeyboardButton('🎯 Поставить цель'),
        KeyboardButton('📖 О боте')
    )
    return markup

# ========== СИСТЕМНЫЙ ПРОМПТ ==========
system_prompt = """Ты - умный и полезный AI-помощник в стиле DeepSeek. Твои ключевые принципы:

🎯 **КОНКРЕТНОСТЬ** - давай четкие, практические ответы
📚 **ПОЛНОТА** - объясняй темы глубоко, но доступно  
🔧 **ПРАКТИЧНОСТЬ** - предлагай конкретные шаги и решения
💡 **ПОЛЬЗА** - фокусируйся на том, что действительно поможет пользователю
🎨 **ЯСНОСТЬ** - структурируй ответы, используй списки и примеры

Всегда:
- Давай пошаговые инструкции где уместно
- Приводи конкретные примеры и цифры
- Объясняй сложные темы простыми словами
- Предлагай разные варианты решений
- Будь поддерживающим и мотивирующим

Избегай общих фраз и "воды" в ответах."""

# ========== ОБРАБОТКА КОМАНД ==========
@bot.message_handler(func=lambda message: message.text == '💡 Попросить совет')
def ask_advice_prompt(message):
    msg = bot.reply_to(message, "🧠 По какой теме нужен совет?\n\nНапример:\n• Как научиться программировать\n• Как улучшить продуктивность\n• Как справиться со стрессом\n• Карьерные рекомендации")
    bot.register_next_step_handler(msg, give_advice)

def give_advice(message):
    try:
        topic = message.text.strip()
        bot.reply_to(message, "🤔 Анализирую ситуацию...")
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Дай подробный практический совет по теме: {topic}. Включи конкретные шаги и рекомендации."}
            ],
            max_tokens=1200
        )
        
        advice = response.choices[0].message.content
        send_long_message(message, f"🧠 Совет по '{topic}':\n\n{advice}")
        
    except Exception as e:
        bot.reply_to(message, "❌ Ошибка обработки запроса", reply_markup=main_menu())

@bot.message_handler(func=lambda message: message.text == '📚 Объяснить тему')
def ask_explain_prompt(message):
    msg = bot.reply_to(message, "📖 Какую тему объяснить?\n\nПримеры:\n• Что такое блокчейн\n• Как работает искусственный интеллект\n• Основы инвестирования\n• Принципы здорового питания")
    bot.register_next_step_handler(msg, explain_topic)

def explain_topic(message):
    try:
        topic = message.text.strip()
        bot.reply_to(message, "📚 Готовлю объяснение...")
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Объясни тему '{topic}' подробно, но доступно. Используй аналогии и примеры."}
            ],
            max_tokens=1500
        )
        
        explanation = response.choices[0].message.content
        send_long_message(message, f"📚 Объяснение '{topic}':\n\n{explanation}")
        
    except Exception as e:
        bot.reply_to(message, "❌ Ошибка обработки запроса", reply_markup=main_menu())

@bot.message_handler(func=lambda message: message.text == '🔧 Решить проблему')
def ask_problem_prompt(message):
    msg = bot.reply_to(message, "🔧 Опиши проблему для решения:\n\nПримеры:\n• Не могу сосредоточиться на работе\n• Хочу выучить английский, но нет мотивации\n• Проблемы в отношениях с коллегами\n• Не знаю как начать свой проект")
    bot.register_next_step_handler(msg, solve_problem)

def solve_problem(message):
    try:
        problem = message.text.strip()
        bot.reply_to(message, "🔍 Анализирую проблему...")
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Помоги решить проблему: {problem}. Дай пошаговый план решения."}
            ],
            max_tokens=1200
        )
        
        solution = response.choices[0].message.content
        send_long_message(message, f"🔧 Решение проблемы:\n\n{solution}")
        
    except Exception as e:
        bot.reply_to(message, "❌ Ошибка обработки запроса", reply_markup=main_menu())

@bot.message_handler(func=lambda message: message.text == '📝 Написать текст')
def ask_writing_prompt(message):
    msg = bot.reply_to(message, "✍️ Что написать?\n\nПримеры:\n• Деловое письмо партнеру\n• Мотивационное письмо для университета\n• Пост для соцсетей о путешествии\n• Отчет о проделанной работе")
    bot.register_next_step_handler(msg, write_text)

def write_text(message):
    try:
        request = message.text.strip()
        bot.reply_to(message, "✍️ Пишу текст...")
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Напиши: {request}. Сделай текст качественным и соответствующим цели."}
            ],
            max_tokens=1000
        )
        
        text = response.choices[0].message.content
        send_long_message(message, f"✍️ Текст:\n\n{text}")
        
    except Exception as e:
        bot.reply_to(message, "❌ Ошибка обработки запроса", reply_markup=main_menu())

@bot.message_handler(func=lambda message: message.text == '💻 Помощь с кодом')
def ask_code_prompt(message):
    msg = bot.reply_to(message, "💻 С чем помочь в программировании?\n\nПримеры:\n• Напиши функцию для парсинга сайта на Python\n• Помоги найти ошибку в коде\n• Объясни как работает этот алгоритм\n• Создай структуру базы данных для приложения")
    bot.register_next_step_handler(msg, help_with_code)

def help_with_code(message):
    try:
        request = message.text.strip()
        bot.reply_to(message, "💻 Анализирую задачу...")
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Помоги с программированием: {request}. Дай рабочий код с комментариями и объяснениями."}
            ],
            max_tokens=1200
        )
        
        code_help = response.choices[0].message.content
        send_long_message(message, f"💻 Помощь с кодом:\n\n{code_help}")
        
    except Exception as e:
        bot.reply_to(message, "❌ Ошибка обработки запроса", reply_markup=main_menu())

@bot.message_handler(func=lambda message: message.text == '🎯 Поставить цель')
def ask_goal_prompt(message):
    msg = bot.reply_to(message, "🎯 Какую цель хочешь достичь?\n\nПримеры:\n• Выучить английский за 6 месяцев\n• Начать зарабатывать на фрилансе\n• Похудеть на 10 кг\n• Освоить новую профессию")
    bot.register_next_step_handler(msg, set_goal)

def set_goal(message):
    try:
        goal = message.text.strip()
        bot.reply_to(message, "🎯 Создаю план достижения цели...")
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Создай подробный план для достижения цели: {goal}. Разбей на этапы, укажи сроки и конкретные действия."}
            ],
            max_tokens=1200
        )
        
        plan = response.choices[0].message.content
        send_long_message(message, f"🎯 План для '{goal}':\n\n{plan}")
        
    except Exception as e:
        bot.reply_to(message, "❌ Ошибка обработки запроса", reply_markup=main_menu())

@bot.message_handler(func=lambda message: message.text == '📖 О боте')
def about_bot(message):
    about_text = """
🤖 *Умный помощник*

Я - AI-ассистент, созданный чтобы помогать тебе:
• 🧠 **Давать умные советы** по любым вопросам
• 📚 **Объяснять сложные темы** простыми словами  
• 🔧 **Решать проблемы** с пошаговыми планами
• 📝 **Писать тексты** любого формата
• 💻 **Помогать с программированием**
• 🎯 **Ставить и достигать цели**

*Как использовать:*
Просто нажми на одну из кнопок ниже и опиши что тебе нужно!

*О создателе:*
Этот бот создан с помощью DeepSeek и работает на OpenAI GPT-3.5
    """
    bot.reply_to(message, about_text, parse_mode='Markdown', reply_markup=main_menu())

# ========== ОБЩИЕ СООБЩЕНИЯ ==========
@bot.message_handler(commands=['start', 'help'])
def start(message):
    welcome_text = """
🤖 *Привет! Я твой умный помощник* 

Выбери чем могу помочь:

💡 *Совет* - практические рекомендации по любой теме
📚 *Объяснить тему* - простыми словами о сложном
🔧 *Решить проблему* - пошаговый план решения
📝 *Написать текст* - любой формат и цель
💻 *Помощь с кодом* - программирование и отладка  
🎯 *Поставить цель* - план достижения мечты

*Просто нажми на кнопку ниже!* 👇
    """
    bot.reply_to(message, welcome_text, parse_mode='Markdown', reply_markup=main_menu())

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        # Если сообщение не обработано кнопками - отвечаем как умный помощник
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message.text}
            ],
            max_tokens=1000
        )
        
        answer = response.choices[0].message.content
        send_long_message(message, answer)
        
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        bot.reply_to(message, "❌ Ошибка обработки запроса", reply_markup=main_menu())

# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========
def send_long_message(message, text):
    """Разбивает длинные сообщения на части"""
    if len(text) > 4096:
        for i in range(0, len(text), 4096):
            part = text[i:i+4096]
            if i == 0:
                bot.reply_to(message, part, reply_markup=main_menu())
            else:
                bot.send_message(message.chat.id, part, reply_markup=main_menu())
    else:
        bot.reply_to(message, text, reply_markup=main_menu())

# ========== ЗАПУСК ==========
if __name__ == '__main__':
    logger.info("🚀 Умный помощник запускается...")
    bot.infinity_polling()