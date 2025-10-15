import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from openai import OpenAI

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Загружаем токены из переменных окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TELEGRAM_TOKEN or not OPENAI_API_KEY:
    raise ValueError("Не найдены токены TELEGRAM_TOKEN или OPENAI_API_KEY!")

# Инициализация бота и OpenAI клиента
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)
client = OpenAI(api_key=OPENAI_API_KEY)

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Привет! Я бот ChatGPT 🤖\nНапиши мне что-нибудь!")

# Обработка всех текстовых сообщений
@dp.message_handler(content_types=['text'])
async def handle_message(message: types.Message):
    try:
        user_message = message.text
        await message.answer("⏳ Думаю...")

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты — умный и доброжелательный помощник."},
                {"role": "user", "content": user_message}
            ],
            temperature=0.8,
            max_tokens=500
        )

        reply = response.choices[0].message.content
        await message.answer(reply)

    except Exception as e:
        logging.exception(e)
        await message.answer("⚠️ Произошла ошибка. Попробуй позже.")

# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
