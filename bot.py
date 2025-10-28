import os
import logging
import telebot
import openai
import requests
import base64
import io
from io import BytesIO
import tempfile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

bot = telebot.TeleBot(TELEGRAM_TOKEN)
openai.api_key = OPENAI_API_KEY

# Хранилище контекста
user_conversations = {}

# Умный системный промпт
SMART_SYSTEM_PROMPT = """Ты - продвинутый AI-ассистент с мультимедийными возможностями. Твои способности:

🎯 **ИНТЕЛЛЕКТ:**
- Используй GPT-4 для сложных задач
- Анализируй контекст глубоко
- Предлагай креативные решения
- Думай как эксперт в разных областях

📱 **МУЛЬТИМЕДИА:**
- Создавай изображения по описанию
- Анализируй загруженные фото
- Работай с голосовыми сообщениями
- Понимай разные форматы контента

💡 **ПОВЕДЕНИЕ:**
- Будь проактивным и полезным
- Задавай уточняющие вопросы
- Предлагай дополнительные возможности
- Будь настоящим интеллектуальным партнером"""

def transcribe_audio(audio_file):
    """Транскрибация голосового сообщения"""
    try:
        # Скачиваем аудио файл
        file_info = bot.get_file(audio_file.file_id)
        file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_info.file_path}"
        
        # Скачиваем файл
        response = requests.get(file_url)
        audio_data = BytesIO(response.content)
        
        # Сохраняем во временный файл
        with tempfile.NamedTemporaryFile(delete=False, suffix='.ogg') as temp_audio:
            temp_audio.write(audio_data.getvalue())
            temp_audio_path = temp_audio.name
        
        # Открываем файл и отправляем в Whisper
        with open(temp_audio_path, 'rb') as audio_file:
            transcript = openai.Audio.transcribe(
                model="whisper-1",
                file=audio_file,
                language="ru"  # Указываем язык для лучшего распознавания
            )
        
        # Удаляем временный файл
        os.unlink(temp_audio_path)
        
        return transcript.text
    except Exception as e:
        logger.error(f"❌ Ошибка транскрибации: {e}")
        return None

def analyze_image(image_file):
    """Анализ изображения через GPT-4 Vision"""
    try:
        # Скачиваем изображение
        file_info = bot.get_file(image_file.file_id)
        file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_info.file_path}"
        
        response = requests.get(file_url)
        base64_image = base64.b64encode(response.content).decode('utf-8')
        
        # Анализируем через GPT-4 Vision
        analysis_response = openai.ChatCompletion.create(
            model="gpt-4-vision-preview",
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "text", 
                        "text": "Детально опиши что изображено на фото. Будь максимально внимательным к деталям, цветам, эмоциям, объектам. Если есть текст - расшифруй его."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }],
            max_tokens=1000
        )
        
        return analysis_response.choices[0].message.content
    except Exception as e:
        logger.error(f"❌ Ошибка анализа изображения: {e}")
        return None

def generate_image_dalle(prompt):
    """Генерация изображения через DALL-E 3"""
    try:
        response = openai.Image.create(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )
        return response.data[0].url
    except Exception as e:
        logger.error(f"❌ Ошибка генерации изображения: {e}")
        return None

def get_smart_response(messages, use_gpt4=False):
    """Получение умного ответа от GPT"""
    try:
        model = "gpt-4" if use_gpt4 else "gpt-3.5-turbo"
        
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            max_tokens=1500,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"❌ Ошибка GPT: {e}")
        # Пробуем с GPT-3.5 если GPT-4 недоступен
        if use_gpt4:
            return get_smart_response(messages, use_gpt4=False)
        return "❌ Ошибка обработки запроса"

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    user_conversations[user_id] = [
        {"role": "system", "content": SMART_SYSTEM_PROMPT}
    ]
    
    welcome = """
🤖 *ПРИВЕТ! Я УМНЫЙ МУЛЬТИМЕДИЙНЫЙ ПОМОЩНИК* 

*Мои суперспособности:*

🧠 **ИНТЕЛЛЕКТ:**
• GPT-4 для сложных задач
• Глубокий анализ и креативность
• Контекстное понимание

🎨 **СОЗДАНИЕ:**
• Генерация уникальных изображений
• Креативное письмо и идеи
• Дизайн и арт

📱 **МУЛЬТИМЕДИА:**
• Анализ фотографий
• Распознавание голосовых сообщений
• Работа с разными форматами

*Команды:*
/image [описание] - создать изображение
/gpt4 [запрос] - использовать GPT-4
/clear - очистить историю
/help - все возможности

*Просто отправь:*
• Текст - умный ответ
• Фото - детальный анализ
• Голосовое - расшифровка и ответ
    """
    bot.reply_to(message, welcome, parse_mode='Markdown')

@bot.message_handler(commands=['gpt4'])
def gpt4_command(message):
    """Использование GPT-4 для сложных запросов"""
    try:
        query = message.text.replace('/gpt4', '').strip()
        
        if not query:
            bot.reply_to(message, "🧠 Используй GPT-4 для сложных задач:\n/gpt4 объясни квантовую физику\n/gpt4 напиши бизнес-план\n/gpt4 придумай креативную идею")
            return
        
        user_id = message.from_user.id
        if user_id not in user_conversations:
            user_conversations[user_id] = [{"role": "system", "content": SMART_SYSTEM_PROMPT}]
        
        user_conversations[user_id].append({"role": "user", "content": f"GPT-4 ЗАПРОС: {query}"})
        
        bot.reply_to(message, "🧠 *GPT-4 анализирует запрос...*", parse_mode='Markdown')
        
        response = get_smart_response(user_conversations[user_id], use_gpt4=True)
        
        user_conversations[user_id].append({"role": "assistant", "content": response})
        
        # Ограничиваем историю
        if len(user_conversations[user_id]) > 8:
            user_conversations[user_id] = [user_conversations[user_id][0]] + user_conversations[user_id][-7:]
        
        if len(response) > 4000:
            parts = [response[i:i+4000] for i in range(0, len(response), 4000)]
            for i, part in enumerate(parts):
                if i == 0:
                    bot.reply_to(message, f"🧠 *GPT-4 отвечает:*\n\n{part}", parse_mode='Markdown')
                else:
                    bot.send_message(message.chat.id, part)
        else:
            bot.reply_to(message, f"🧠 *GPT-4 отвечает:*\n\n{response}", parse_mode='Markdown')
            
    except Exception as e:
        logger.error(f"❌ Ошибка GPT-4: {e}")
        bot.reply_to(message, "❌ GPT-4 временно недоступен. Используй обычный режим.")

@bot.message_handler(commands=['image', 'img'])
def image_command(message):
    """Генерация изображения через DALL-E 3"""
    try:
        prompt = message.text.replace('/image', '').replace('/img', '').strip()
        
        if not prompt:
            bot.reply_to(message, "🎨 Опиши что создать:\n/image космический корабль в nebula\n/image кот в костюме супергероя\n/image футуристический город")
            return
        
        bot.reply_to(message, f"🎨 *DALL-E 3 создает:* '{prompt}'...", parse_mode='Markdown')
        
        image_url = generate_image_dalle(prompt)
        
        if image_url:
            # Скачиваем и отправляем изображение
            image_response = requests.get(image_url)
            image_data = BytesIO(image_response.content)
            
            bot.send_photo(message.chat.id, image_data, caption=f"🎨 {prompt}")
        else:
            bot.reply_to(message, "❌ Не удалось создать изображение")
            
    except Exception as e:
        logger.error(f"❌ Ошибка создания изображения: {e}")
        bot.reply_to(message, "❌ Ошибка генерации изображения")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    """Обработка фотографий"""
    try:
        bot.reply_to(message, "📸 *Анализирую изображение...*", parse_mode='Markdown')
        
        analysis = analyze_image(message.photo[-1])
        
        if analysis:
            bot.reply_to(message, f"📸 *Анализ изображения:*\n\n{analysis}", parse_mode='Markdown')
        else:
            bot.reply_to(message, "❌ Не удалось проанализировать изображение")
            
    except Exception as e:
        logger.error(f"❌ Ошибка обработки фото: {e}")
        bot.reply_to(message, "❌ Ошибка анализа изображения")

@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    """Обработка голосовых сообщений"""
    try:
        bot.reply_to(message, "🎤 *Расшифровываю голосовое...*", parse_mode='Markdown')
        
        transcript = transcribe_audio(message.voice)
        
        if transcript:
            bot.reply_to(message, f"🎤 *Распознанный текст:*\n{transcript}", parse_mode='Markdown')
            
            # Автоматически обрабатываем распознанный текст
            user_id = message.from_user.id
            if user_id not in user_conversations:
                user_conversations[user_id] = [{"role": "system", "content": SMART_SYSTEM_PROMPT}]
            
            user_conversations[user_id].append({"role": "user", "content": f"ГОЛОСОВОЕ: {transcript}"})
            
            response = get_smart_response(user_conversations[user_id])
            
            user_conversations[user_id].append({"role": "assistant", "content": response})
            
            if len(user_conversations[user_id]) > 8:
                user_conversations[user_id] = [user_conversations[user_id][0]] + user_conversations[user_id][-7:]
            
            bot.reply_to(message, f"🤖 *Ответ на голосовое:*\n\n{response}", parse_mode='Markdown')
        else:
            bot.reply_to(message, "❌ Не удалось распознать голосовое сообщение")
            
    except Exception as e:
        logger.error(f"❌ Ошибка обработки голосового: {e}")
        bot.reply_to(message, "❌ Ошибка распознавания голоса")

@bot.message_handler(commands=['clear'])
def clear_context(message):
    user_id = message.from_user.id
    user_conversations[user_id] = [{"role": "system", "content": SMART_SYSTEM_PROMPT}]
    bot.reply_to(message, "🧹 *История очищена!*", parse_mode='Markdown')

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = """
🆘 *ПОЛНЫЙ СПИСОК ВОЗМОЖНОСТЕЙ*

🧠 **УМНЫЕ ФУНКЦИИ:**
• `/gpt4 [запрос]` - GPT-4 для сложных задач
• Автоконтекст - помню 8 последних сообщений
• Глубокий анализ и креативность

🎨 **СОЗДАНИЕ КОНТЕНТА:**
• `/image [описание]` - генерация изображений DALL-E 3
• Креативное письмо и идеи
• Дизайн и арт-проекты

📱 **МУЛЬТИМЕДИА:**
• Отправь фото - детальный анализ
• Отправь голосовое - расшифровка и ответ
• Поддержка разных форматов

⚡ **КОМАНДЫ:**
• `/start` - описание возможностей
• `/gpt4` - умный режим
• `/image` - создание картинок
• `/clear` - очистка истории
• `/help` - эта справка

*Просто общайся со мной в любом формате!* 🚀
    """
    bot.reply_to(message, help_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    """Обработка текстовых сообщений"""
    try:
        user_id = message.from_user.id
        user_message = message.text
        
        if user_id not in user_conversations:
            user_conversations[user_id] = [{"role": "system", "content": SMART_SYSTEM_PROMPT}]
        
        user_conversations[user_id].append({"role": "user", "content": user_message})
        
        # Определяем сложность запроса для выбора модели
        complex_keywords = ['анализируй', 'объясни', 'создай', 'придумай', 'проект', 'бизнес', 'науч', 'технич']
        use_gpt4 = any(keyword in user_message.lower() for keyword in complex_keywords)
        
        bot.send_chat_action(message.chat.id, 'typing')
        
        response = get_smart_response(user_conversations[user_id], use_gpt4=use_gpt4)
        
        user_conversations[user_id].append({"role": "assistant", "content": response})
        
        # Ограничиваем историю
        if len(user_conversations[user_id]) > 8:
            user_conversations[user_id] = [user_conversations[user_id][0]] + user_conversations[user_id][-7:]
        
        if len(response) > 4000:
            parts = [response[i:i+4000] for i in range(0, len(response), 4000)]
            for i, part in enumerate(parts):
                if i == 0:
                    bot.reply_to(message, part)
                else:
                    bot.send_message(message.chat.id, part)
        else:
            bot.reply_to(message, response)
            
    except Exception as e:
        logger.error(f"❌ Ошибка обработки: {e}")
        bot.reply_to(message, "❌ Временная ошибка. Попробуй еще раз!")

if __name__ == '__main__':
    logger.info("🚀 ЗАПУСКАЮ УМНОГО МУЛЬТИМЕДИЙНОГО БОТА...")
    bot.infinity_polling()