import asyncio
import logging
import sys
from aiohttp import web

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN, GROUP_CHAT_ID, PORT

# Импортируем роутеры из папки handlers
from handlers.start import router as start_router
from handlers.student import router as student_router
from handlers.staff import router as staff_router
from handlers.admin import router as admin_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Подключаем роутеры
dp.include_router(start_router)
dp.include_router(student_router)
dp.include_router(staff_router)
dp.include_router(admin_router)

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
