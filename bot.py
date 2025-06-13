import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from config import BOT_TOKEN
import asyncio
from database.db import init_db
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database.db import get_all_user_ids
from keyboards.user import kunlik_namoz_kb
from datetime import datetime
import pytz
from database.db import ensure_main_admin
import asyncio

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("bot.log"), logging.StreamHandler()]
)

async def send_daily_namoz(bot):
    user_ids = await get_all_user_ids()
    today = datetime.now(pytz.timezone("Asia/Tashkent")).strftime("%d-%m-%Y")
    text = f"-------------\n|{today}|\n---------------\nBugun qaysi namozlarni o'qidingiz? Har biriga mos tugmani tanlang:"
    for user_id in user_ids:
        try:
            await bot.send_message(user_id, text, reply_markup=kunlik_namoz_kb())
            logging.info(f"Xabar {user_id} ga muvaffaqiyatli yuborildi")
        except Exception as e:
            logging.error(f"Xabar {user_id} ga yuborishda xato: {e}")

def setup_scheduler(bot):
    tz = pytz.timezone("Asia/Tashkent")
    current_time = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    logging.info(f"Joriy vaqt (Asia/Tashkent): {current_time}")
    scheduler = AsyncIOScheduler(timezone=tz)
    scheduler.add_job(send_daily_namoz, "cron", hour=17, minute=4, args=[bot])
    # Test uchun: har daqiqada
    # scheduler.add_job(send_daily_namoz, "cron", minute="*", args=[bot])
    logging.info("Scheduler ishga tushdi")
    scheduler.start()
    return scheduler



async def main():
    try:
        await init_db()
        bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        bot_info = await bot.get_me()
        logging.info(f"Bot muvaffaqiyatli ishga tushdi: @{bot_info.username}")
        dp = Dispatcher(storage=MemoryStorage())
        from handlers import register_handlers
        await ensure_main_admin()
        register_handlers(dp)
        scheduler = setup_scheduler(bot)
        try:
            await dp.start_polling(bot)
        finally:
            scheduler.shutdown()
    except Exception as e:
        logging.error(f"Bot ishga tushishda xato: {e}")

if __name__ == '__main__':
    print(f"Bot ishga tushdi! Hozirgi vaqt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    asyncio.run(main())