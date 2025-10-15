import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from openai import OpenAI

# Настройка логов
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получаем токены из окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TELEGRAM_TOKEN or not OPENAI_API_KEY:
    raise ValueError("❌ Не найдены переменные TELEGRAM_TOKEN или OPENAI_API_KEY!")

logger.info("✅ Токены загружены")

# Инициализация
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)
client = OpenAI(api_key=OPENAI_API_KEY)

# Команда /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Привет 👋\nЯ бот ChatGPT! Напиши мне любой вопрос — и я помогу!")

# Обработка текстов
@dp.message_handler(content_types=['text'])
async def handle_message(message: types.Message):
    try:
        user_message = message.text
        await message.answer("🤔 Думаю...")

        completion = client.chat.completions.create(
            model="gpt-4o-mini",  # компактная и быстрая модель
            messages=[
                {"role": "system", "content": "Ты — доброжелательный и умный помощник."},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=500,
        )

        answer = completion.choices[0].message.content.strip()
        await message.answer(answer)

    except Exception as e:
        logger.exception(e)
        await message.answer("⚠️ Произошла ошибка. Попробуй чуть позже.")

# Запуск
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
