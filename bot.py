import os
import logging
from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
import asyncio
from openai import OpenAI

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Получение токенов из переменных окружения
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Проверка наличия токенов
if not TELEGRAM_TOKEN:
    logger.error("❌ TELEGRAM_TOKEN не установлен!")
    exit(1)
if not OPENAI_API_KEY:
    logger.error("❌ OPENAI_API_KEY не установлен!")
    exit(1)

logger.info("✅ Токены загружены успешно")

# Инициализация бота и диспетчера
bot = Bot(token=TELEGRAM_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
router = Router()
dp.include_router(router)

# Инициализация OpenAI клиента
client = OpenAI(api_key=OPENAI_API_KEY)

@router.message(Command("start"))
async def start_command(message: Message):
    await message.answer('Привет! Я бот ORONA с интеграцией ChatGPT. Задайте мне вопрос!')

@router.message(Command("help"))
async def help_command(message: Message):
    await message.answer('Просто напишите сообщение, и я отвечу с помощью ChatGPT!')

@router.message()
async def handle_message(message: Message):
    user_message = message.text
    logger.info(f"📨 Получено сообщение: {user_message}")
    
    try:
        # Отправляем запрос к OpenAI API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that responds in Russian."},
                {"role": "user", "content": user_message}
            ],
            max_tokens=500
        )
        
        bot_response = response.choices[0].message.content
        logger.info(f"🤖 Ответ от GPT: {bot_response}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка OpenAI API: {e}")
        bot_response = "Извините, произошла ошибка при обработке вашего запроса."
    
    await message.answer(bot_response)

async def main():
    logger.info("🚀 Бот запускается...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())