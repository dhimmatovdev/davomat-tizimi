"""Asosiy bot fayli."""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from core.config import settings
from core.db import init_db
from bot.handlers import start, admin, staff

# Logging sozlash
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    """Asosiy funksiya."""
    # Sozlamalarni tekshirish
    try:
        settings.validate()
    except ValueError as e:
        logger.error(f"Sozlamalar xatosi: {e}")
        return
    
    # Database'ni initsializatsiya qilish
    logger.info("Database'ni initsializatsiya qilish...")
    await init_db()
    logger.info("Database tayyor!")
    
    # Bot va Dispatcher yaratish
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    
    # Routerlarni ro'yxatdan o'tkazish
    dp.include_router(start.router)
    dp.include_router(admin.router)
    dp.include_router(staff.router)
    
    # Botni ishga tushirish
    logger.info("Bot ishga tushmoqda...")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot to'xtatildi.")
