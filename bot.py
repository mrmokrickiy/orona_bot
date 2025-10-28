import os
import logging
import telebot
from openai import OpenAI
import requests
import base64
from io import BytesIO

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = OpenAI(api_key=OPENAI_API_KEY)  # Новый клиент

# Хранилище контекста
user_conversations = {}

SMART_SYSTEM_PROMPT = """Ты - умный и полезный AI-помощник. Отвечай подробно и по делу."""

def transcribe_audio(audio_file):
    """Транскрибация голосового сообщения"""
    try:
        file_info = bot.get_file(audio_file.file_id)
        file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_info.file_path}"
        
        # Скачиваем файл
        response = requests.get(file_url)
        audio_data = BytesIO(response.content)
        
        # Сохраняем во временный файл
        with open('temp_audio.ogg', 'wb') as f:
            f.write(audio_data.getvalue())
        
        # Транскрибация через Whisper
        with open('temp_audio.ogg', 'rb') as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file,
                language="ru"
            )
        
        # Удаляем временный файл
        if os.path.exists('temp_audio.ogg'):
            os.remove('temp_audio.ogg')
            
        return transcript.text
    except Exception as e:
        logger.error(f"❌ Ошибка транскрибации: {e}")
        return None

def analyze_image(image_file):
    """Анализ изображения через GPT-4 Vision"""
    try:
        file_info = bot.get_file(image_file.file_id)
        file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_info.file_path}"
        
        response = requests.get(file_url)
        base64_image = base64.b64encode(response.content).decode('utf-8')
        
        analysis_response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "text", 
                        "text": "Опиши что изображено на фото"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }],
            max_tokens=500
        )
        
        return analysis_response.choices[0].message.content
    except Exception as e:
        logger.error(f"❌ Ошибка анализа изображения: {e}")
        return None

def generate_image_dalle(prompt):
    """Генерация изображения через DALL-E 3"""
    try:
        response = client.images.generate(
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
    """Получение умного ответа"""
    try:
        model = "gpt-4" if use_gpt4 else "gpt-3.5-turbo"
        
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=1000
        )
        
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"❌ Ошибка GPT: {e}")
        return "❌ Ошибка обработки запроса"

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    user_conversations[user_id] = [
        {"role": "system", "content": SMART_SYSTEM_PROMPT}
    ]
    
    welcome = """
🤖 *ПРИВЕТ! Я УМНЫЙ ПОМОЩНИК* 

*Мои возможности:*

🎨 **Создание изображений:**
/image [описание] - создам картинку

📱 **Мультимедиа:**
• Отправь фото - проанализирую
• Отправь голосовое - расшифрую и отвечу

🧠 **Умные ответы:**
• Поддерживаю контекст разговора
• Отвечаю на сложные вопросы

*Просто используй меня!* 🚀
    """
    bot.reply_to(message, welcome, parse_mode='Markdown')

@bot.message_handler(commands=['image'])
def image_command(message):
    try:
        prompt = message.text.replace('/image', '').strip()
        
        if not prompt:
            bot.reply_to(message, "🎨 Опиши что создать:\n/image космический корабль\n/image кот в шляпе")
            return
        
        bot.reply_to(message, f"🎨 Создаю: '{prompt}'...")
        
        image_url = generate_image_dalle(prompt)
        
        if image_url:
            image_response = requests.get(image_url)
            image_data = BytesIO(image_response.content)
            
            bot.send_photo(message.chat.id, image_data, caption=f"🎨 {prompt}")
        else:
            bot.reply_to(message, "❌ Не удалось создать изображение")
            
    except Exception as e:
        logger.error(f"❌ Ошибка создания изображения: {e}")
        bot.reply_to(message, "❌ Ошибка генерации")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        bot.reply_to(message, "📸 Анализирую изображение...")
        
        analysis = analyze_image(message.photo[-1])
        
        if analysis:
            bot.reply_to(message, f"📸 Анализ изображения:\n\n{analysis}")
        else:
            bot.reply_to(message, "❌ Не удалось проанализировать")
            
    except Exception as e:
        logger.error(f"❌ Ошибка обработки фото: {e}")
        bot.reply_to(message, "❌ Ошибка анализа")

@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    try:
        bot.reply_to(message, "🎤 Расшифровываю голосовое...")
        
        transcript = transcribe_audio(message.voice)
        
        if transcript:
            bot.reply_to(message, f"🎤 Распознанный текст:\n{transcript}")
            
            # Обрабатываем текст
            user_id = message.from_user.id
            if user_id not in user_conversations:
                user_conversations[user_id] = [{"role": "system", "content": SMART_SYSTEM_PROMPT}]
            
            response = get_smart_response([
                {"role": "system", "content": SMART_SYSTEM_PROMPT},
                {"role": "user", "content": transcript}
            ])
            
            bot.reply_to(message, f"🤖 Ответ:\n\n{response}")
        else:
            bot.reply_to(message, "❌ Не удалось распознать голосовое")
            
    except Exception as e:
        logger.error(f"❌ Ошибка обработки голосового: {e}")
        bot.reply_to(message, "❌ Ошибка распознавания")

@bot.message_handler(commands=['clear'])
def clear_context(message):
    user_id = message.from_user.id
    user_conversations[user_id] = [{"role": "system", "content": SMART_SYSTEM_PROMPT}]
    bot.reply_to(message, "🧹 История очищена!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        user_id = message.from_user.id
        user_message = message.text
        
        if user_id not in user_conversations:
            user_conversations[user_id] = [{"role": "system", "content": SMART_SYSTEM_PROMPT}]
        
        user_conversations[user_id].append({"role": "user", "content": user_message})
        
        if len(user_conversations[user_id]) > 6:
            user_conversations[user_id] = [user_conversations[user_id][0]] + user_conversations[user_id][-5:]
        
        bot.send_chat_action(message.chat.id, 'typing')
        
        response = get_smart_response(user_conversations[user_id])
        
        user_conversations[user_id].append({"role": "assistant", "content": response})
        
        if len(user_conversations[user_id]) > 6:
            user_conversations[user_id] = [user_conversations[user_id][0]] + user_conversations[user_id][-5:]
        
        bot.reply_to(message, response)
            
    except Exception as e:
        logger.error(f"❌ Ошибка обработки: {e}")
        bot.reply_to(message, "❌ Ошибка. Попробуй еще раз!")

if __name__ == '__main__':
    logger.info("🚀 Запускаю умного бота...")
    bot.infinity_polling()