import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from openai import OpenAI

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получение токенов
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if not TELEGRAM_TOKEN or not OPENAI_API_KEY:
    logger.error("❌ Токены не установлены!")
    exit(1)

logger.info("✅ Токены загружены")

# Инициализация
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
client = OpenAI(api_key=OPENAI_API_KEY)

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Привет! Я бот ORONA с ChatGPT. Задай вопрос!")

@dp.message(Command("help"))
async def help_handler(message: types.Message):
    await message.answer("Просто напиши сообщение - я отвечу через GPT!")

@dp.message()
async def message_handler(message: types.Message):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message.text}],
            max_tokens=500
        )
        answer = response.choices[0].message.content
        await message.answer(answer)
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await message.answer("Ошибка обработки запроса")

async def main():
    logger.info("🚀 Бот запускается...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())