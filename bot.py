import logging
import asyncio
from datetime import datetime

import pytz
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import BOT_TOKEN
from database.db import (
    init_db, get_all_user_ids, get_notify_times, ensure_main_admin
)
from keyboards.user import kunlik_namoz_kb
from handlers.admin import set_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("bot.log"), logging.StreamHandler()]
)

async def send_daily_namoz(bot):
    user_ids = await get_all_user_ids()
    today = datetime.now(pytz.timezone("Asia/Tashkent")).strftime("%d-%m-%Y")
    text = (
        f"-------------\n|{today}|\n---------------\n"
        "Bugun qaysi namozlarni o'qidingiz? Har biriga mos tugmani tanlang:"
    )
    for user_id in user_ids:
        try:
            await bot.send_message(user_id, text, reply_markup=kunlik_namoz_kb())
            logging.info(f"Xabar {user_id} ga muvaffaqiyatli yuborildi")
        except Exception as e:
            logging.error(f"Xabar {user_id} ga yuborishda xato: {e}")

async def setup_scheduler(bot):
    tz = pytz.timezone("Asia/Tashkent")
    logging.info(f"Joriy vaqt (Asia/Tashkent): {datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')}")
    scheduler = AsyncIOScheduler(timezone=tz)
    notify_times = await get_notify_times()
    for hour, minute in notify_times:
        scheduler.add_job(send_daily_namoz, "cron", hour=hour, minute=minute, args=[bot])
    logging.info("Scheduler ishga tushdi")
    scheduler.start()
    return scheduler

async def main():
    await init_db()
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    logging.info(f"Bot muvaffaqiyatli ishga tushdi: @{(await bot.get_me()).username}")
    dp = Dispatcher(storage=MemoryStorage())
    from handlers import register_handlers
    await ensure_main_admin()
    register_handlers(dp)
    scheduler = await setup_scheduler(bot)
    set_scheduler(scheduler, send_daily_namoz)
    try:
        await dp.start_polling(bot)
    finally:
        scheduler.shutdown()

if __name__ == '__main__':
    print(f"Bot ishga tushdi! Hozirgi vaqt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    asyncio.run(main())