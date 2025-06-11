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

logging.basicConfig(level=logging.INFO)

async def send_daily_namoz(bot):
    user_ids = await get_all_user_ids()
    today = datetime.now().strftime("%d-%m-%Y")
    text = f"-------------\n|{today}|\n---------------\nBugun qaysi namozlarni o'qidingiz? Har biriga mos tugmani tanlang:"
    for user_id in user_ids:
        try:
            await bot.send_message(user_id, text, reply_markup=kunlik_namoz_kb())
        except Exception:
            pass

def setup_scheduler(bot):
    scheduler = AsyncIOScheduler(timezone="Asia/Tashkent")
    scheduler.add_job(send_daily_namoz, "cron", hour=12, minute=37, args=[bot])
    scheduler.start()

async def main():
    await init_db()
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())
    from handlers import register_handlers
    register_handlers(dp)
    setup_scheduler(bot)
    await dp.start_polling(bot)

if __name__ == '__main__':
    print(f"Bot ishga tushdi! Hozirgi vaqt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    asyncio.run(main())
