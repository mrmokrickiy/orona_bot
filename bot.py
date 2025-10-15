import os
import logging
import telebot
import openai
import requests
import random
from io import BytesIO
import base64

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

bot = telebot.TeleBot(TELEGRAM_TOKEN)
openai.api_key = OPENAI_API_KEY

# ========== 🎨 СОЗДАНИЕ ИЗОБРАЖЕНИЙ ==========
@bot.message_handler(commands=['image', 'img', 'картинка'])
def generate_image(message):
    try:
        prompt = message.text.split(' ', 1)[1] if ' ' in message.text else ''
        
        if not prompt:
            bot.reply_to(message, '🎨 Напиши описание картинки после команды:\n/image космический корабль\n/image милый котенок')
            return
        
        bot.reply_to(message, f'🎨 Создаю: "{prompt}"...')
        
        response = openai.Image.create(prompt=prompt, n=1, size="1024x1024")
        image_url = response['data'][0]['url']
        
        image_response = requests.get(image_url)
        image_data = BytesIO(image_response.content)
        
        bot.send_photo(message.chat.id, image_data, caption=f'🎨 {prompt}')
        
    except Exception as e:
        bot.reply_to(message, '❌ Ошибка создания картинки')

# ========== 📸 АНАЛИЗ ФОТО ==========
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        bot.reply_to(message, "🖼️ Анализирую фото...")
        
        file_info = bot.get_file(message.photo[-1].file_id)
        file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_info.file_path}"
        
        response = requests.get(file_url)
        base64_image = base64.b64encode(response.content).decode('utf-8')
        
        analysis_response = openai.ChatCompletion.create(
            model="gpt-4-vision-preview",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": "Опиши подробно что на фото"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }],
            max_tokens=500
        )
        
        description = analysis_response.choices[0].message.content
        bot.reply_to(message, f"📸 Анализ фото:\n\n{description}")
        
    except Exception as e:
        bot.reply_to(message, "❌ Не удалось проанализировать фото")

# ========== 🎤 ГОЛОСОВЫЕ СООБЩЕНИЯ ==========
@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    bot.reply_to(message, "🎤 Вижу голосовое сообщение! Напиши текст, и я с радостью отвечу! 💬")

# ========== 🎲 ИГРЫ ==========
games = {}

@bot.message_handler(commands=['game', 'игра'])
def start_game(message):
    games_list = """
🎮 *Доступные игры:*

/quiz - 🧠 Викторина (5 случайных вопросов)
/riddle - 🔍 Загадка (угадай загадку)
/guess - 🔢 Угадай число (от 1 до 100)

Выбери игру! 🎯
    """
    bot.reply_to(message, games_list, parse_mode='Markdown')

@bot.message_handler(commands=['quiz'])
def quiz_game(message):
    questions = [
        {"question": "Какая планета солнечной системы самая горячая?", "answer": "Венера"},
        {"question": "Сколько костей в теле взрослого человека?", "answer": "206"},
        {"question": "Какой химический элемент обозначается как Au?", "answer": "Золото"},
        {"question": "В каком году человек впервые полетел в космос?", "answer": "1961"},
        {"question": "Какое животное самое быстрое на земле?", "answer": "Гепард"}
    ]
    
    random.shuffle(questions)
    games[message.chat.id] = {"type": "quiz", "questions": questions, "score": 0, "current": 0}
    
    bot.reply_to(message, f"🧠 ВИКТОРИНА! Ответь на 5 вопросов!\n\nПервый вопрос:\n{questions[0]['question']}")

@bot.message_handler(commands=['riddle'])
def riddle_game(message):
    riddles = [
        {"riddle": "Висит груша - нельзя скушать. Что это?", "answer": "лампочка"},
        {"riddle": "Зимой и летом одним цветом. Что это?", "answer": "ель"},
        {"riddle": "Сидит дед, во сто шуб одет. Кто это?", "answer": "лук"}
    ]
    
    riddle = random.choice(riddles)
    games[message.chat.id] = {"type": "riddle", "riddle": riddle}
    
    bot.reply_to(message, f"🔍 ЗАГАДКА:\n\n{riddle['riddle']}")

@bot.message_handler(commands=['guess'])
def guess_number(message):
    number = random.randint(1, 100)
    games[message.chat.id] = {"type": "guess", "number": number, "attempts": 0}
    
    bot.reply_to(message, "🔢 Я загадал число от 1 до 100! Попробуй угадать!")

# ========== 💰 КОНВЕРТЕР ВАЛЮТ ==========
@bot.message_handler(commands=['currency', 'курс'])
def convert_currency(message):
    try:
        text = message.text.lower()
        
        if 'доллар' in text or 'usd' in text:
            rate = 95.0
            bot.reply_to(message, f"💵 Курс доллара: ~{rate} руб.")
        elif 'евро' in text or 'eur' in text:
            rate = 102.0
            bot.reply_to(message, f"💶 Курс евро: ~{rate} руб.")
        else:
            bot.reply_to(message, "💱 Конвертер валют:\n\n/currency доллар - курс USD\n/currency евро - курс EUR")
            
    except Exception as e:
        bot.reply_to(message, "❌ Ошибка конвертации")

# ========== 😂 ГЕНЕРАТОР ШУТОК ==========
@bot.message_handler(commands=['joke', 'шутка'])
def tell_joke(message):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "user", 
                "content": "Расскажи смешную шутку на русском. Будь оригинальным и веселым."
            }],
            max_tokens=150
        )
        
        joke = response.choices[0].message.content
        bot.reply_to(message, f"😂 Шутка:\n\n{joke}")
        
    except Exception as e:
        jokes = [
            "Почему программисты путают Хэллоуин и Рождество? Потому что Oct 31 == Dec 25!",
            "Как называется баран, который знает только одну ноту? Бара-бара-бан!",
            "Почему курица перешла дорогу? Чтобы доказать боту, что она не индюк!"
        ]
        bot.reply_to(message, f"😂 {random.choice(jokes)}")

# ========== 💻 ГЕНЕРАТОР КОДА ==========
@bot.message_handler(commands=['code', 'код'])
def generate_code(message):
    try:
        request = message.text.replace('/code', '').replace('/код', '').strip()
        
        if not request:
            bot.reply_to(message, "💻 Генератор кода:\n\n/code напиши функцию сложения на Python\n/code создай HTML страницу с формой")
            return
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "user", 
                "content": f"Напиши код для: {request}. Дай полный рабочий код с комментариями."
            }],
            max_tokens=800
        )
        
        code = response.choices[0].message.content
        bot.reply_to(message, f"💻 Код для \"{request}\":\n\n```\n{code}\n```", parse_mode='Markdown')
        
    except Exception as e:
        bot.reply_to(message, "❌ Ошибка генерации кода")

# ========== ✍️ КРЕАТИВНОЕ ПИСЬМО ==========
@bot.message_handler(commands=['write', 'напиши'])
def creative_writing(message):
    try:
        request = message.text.replace('/write', '').replace('/напиши', '').strip()
        
        if not request:
            bot.reply_to(message, "✍️ Креативное письмо:\n\n/write короткий рассказ про космос\n/write стих про любовь")
            return
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "user", 
                "content": f"Напиши: {request}. Будь креативным и оригинальным."
            }],
            max_tokens=600
        )
        
        writing = response.choices[0].message.content
        bot.reply_to(message, f"✍️ {writing}")
        
    except Exception as e:
        bot.reply_to(message, "❌ Ошибка создания текста")

# ========== 🔮 ПРЕДСКАЗАНИЯ ==========
@bot.message_handler(commands=['predict', 'предскажи'])
def make_prediction(message):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "user", 
                "content": "Сделай забавное предсказание на ближайшее будущее. Будь креативным и позитивным. 2-3 предложения."
            }],
            max_tokens=150
        )
        
        prediction = response.choices[0].message.content
        bot.reply_to(message, f"🔮 Мое предсказание для тебя:\n\n{prediction}")
        
    except Exception as e:
        predictions = [
            "Завтра тебя ждет приятный сюрприз от старого друга!",
            "На этой неделе ты найдешь решение давней проблемы!",
            "Скоро тебе улыбнется удача в неожиданном месте!"
        ]
        bot.reply_to(message, f"🔮 {random.choice(predictions)}")

# ========== 🧠 ПЕРСОНАЛЬНЫЙ КОУЧ ==========
@bot.message_handler(commands=['advice', 'совет'])
def give_advice(message):
    try:
        request = message.text.replace('/advice', '').replace('/совет', '').strip()
        
        if not request:
            bot.reply_to(message, "🧠 Коуч-помощник:\n\n/advice как стать дисциплинированным\n/advice как справиться со стрессом")
            return
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "user", 
                "content": f"Дай практический совет по теме: {request}. Будь конкретным и поддерживающим."
            }],
            max_tokens=400
        )
        
        advice = response.choices[0].message.content
        bot.reply_to(message, f"🧠 Совет по \"{request}\":\n\n{advice}")
        
    except Exception as e:
        bot.reply_to(message, "❌ Ошибка генерации совета")

# ========== ОБРАБОТКА ИГР ==========
@bot.message_handler(func=lambda message: message.chat.id in games)
def handle_game_response(message):
    try:
        game = games[message.chat.id]
        user_answer = message.text.strip().lower()
        
        if game["type"] == "quiz":
            current_q = game["questions"][game["current"]]
            if user_answer.lower() == current_q["answer"].lower():
                game["score"] += 1
                bot.reply_to(message, "✅ Правильно!")
            else:
                bot.reply_to(message, f"❌ Неверно! Правильный ответ: {current_q['answer']}")
            
            game["current"] += 1
            
            if game["current"] < len(game["questions"]):
                next_q = game["questions"][game["current"]]
                bot.reply_to(message, f"Следующий вопрос:\n{next_q['question']}")
            else:
                bot.reply_to(message, f"🎉 Викторина завершена! Твой счет: {game['score']}/5")
                del games[message.chat.id]
                
        elif game["type"] == "riddle":
            if user_answer == game["riddle"]["answer"]:
                bot.reply_to(message, "🎉 Правильно! Ты отгадал загадку!")
                del games[message.chat.id]
            else:
                bot.reply_to(message, "❌ Не угадал! Попробуй еще раз.")
                
        elif game["type"] == "guess":
            game["attempts"] += 1
            try:
                guess = int(user_answer)
                if guess == game["number"]:
                    bot.reply_to(message, f"🎉 Угадал! За {game['attempts']} попыток!")
                    del games[message.chat.id]
                elif guess < game["number"]:
                    bot.reply_to(message, "📈 Больше!")
                else:
                    bot.reply_to(message, "📉 Меньше!")
            except:
                bot.reply_to(message, "Введи число!")
                
    except Exception as e:
        bot.reply_to(message, "❌ Ошибка в игре")

# ========== 💬 ОБЩИЕ СООБЩЕНИЯ ==========
@bot.message_handler(commands=['start', 'help'])
def start(message):
    welcome_text = """
🤖 *УНИВЕРСАЛЬНЫЙ МЕГА-БОТ* 🚀

*🎨 Креатив:*
/image [описание] - Создать картинку
/write [запрос] - Написать текст/стихи
/joke - Случайная шутка
/predict - Предсказание будущего

*🎮 Развлечения:*
/game - Все игры
/quiz - Викторина
/riddle - Загадки
/guess - Угадай число

*🛠️ Практичное:*
/currency - Курсы валют
/code - Генератор кода
/advice - Советы коуча

*📱 Мультимедиа:*
Отправь фото - Анализ изображения
Отправь голосовое - (поддержка скоро появится!)

*Просто напиши что-нибудь - и я отвечу!* ✨
    """
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        # Обычный ответ
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Ты - универсальный помощник с чувством юмора. Отвечай полезно, но не скучно."
                },
                {
                    "role": "user", 
                    "content": message.text
                }
            ],
            max_tokens=600
        )
        
        answer = response.choices[0].message.content
        
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
        bot.reply_to(message, "❌ Ошибка обработки запроса")

# ========== ЗАПУСК ==========
if __name__ == '__main__':
    logger.info("🚀 МЕГА-БОТ ЗАПУСКАЕТСЯ...")
    bot.infinity_polling()