import asyncio
import logging
import sys
from aiohttp import web

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN, GROUP_CHAT_ID, PORT
from handlers import start, student, staff, admin

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Подключение роутеров
dp.include_router(start.router)
dp.include_router(student.router)
dp.include_router(staff.router)
dp.include_router(admin.router)

# Веб-сервер для health check
async def start_web_server():
    app = web.Application()
    app.router.add_get('/', lambda request: web.Response(text="Bot is running"))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host='0.0.0.0', port=PORT)
    await site.start()
    logger.info("🌐 Web server started on port %s", PORT)

async def main():
    # Проверка группы при запуске
    try:
        bot_me = await bot.get_me()
        chat = await bot.get_chat(GROUP_CHAT_ID)
        logger.info(f"Бот @{bot_me.username} работает в чате '{chat.title}' (ID: {GROUP_CHAT_ID})")
        member = await bot.get_chat_member(GROUP_CHAT_ID, bot_me.id)
        logger.info(f"Статус бота в группе: {member.status}")
        if member.status not in ("administrator", "member", "creator"):
            logger.warning("Бот не является участником группы! Возможно, он не добавлен.")
    except Exception as e:
        logger.error(f"Не удалось проверить группу: {e}. Убедитесь, что бот добавлен в группу и ID верен.")

    await start_web_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен вручную.")
    except Exception as e:
        logger.critical(f"Критическая ошибка: {e}", exc_info=True)
        sys.exit(1)
