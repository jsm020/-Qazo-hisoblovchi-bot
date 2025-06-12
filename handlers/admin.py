from database.db import get_stats, add_channel, get_channels, remove_channel

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.db import add_faq, create_faq_table, get_all_user_ids
from config import ADMINS

router = Router()

# Statistika handler
def format_stats(stats):
    return (
        "📊 <b>Foydalanuvchilar statistikasi</b>\n\n"
        f"🗓️ <b>Kunlik:</b> {stats['daily']}\n"
        f"📅 <b>Haftalik:</b> {stats['weekly']}\n"
        f"🗓️ <b>Oylik:</b> {stats['monthly']}"
    )
@router.message(F.text.in_(["📊 Statistika", "/stat", "/statistika"]))
async def stats_handler(message: Message):
    if message.from_user.id not in ADMINS:
        await message.answer("Faqat adminlar uchun.")
        return
    stats = await get_stats()
    await message.answer(format_stats(stats))

class AddFAQState(StatesGroup):
    waiting_for_question = State()
    waiting_for_answer = State()

class BroadcastState(StatesGroup):
    waiting_for_content = State()
    waiting_for_confirm = State()

class ChannelState(StatesGroup):
    waiting_for_channel = State()
    waiting_for_remove_channel = State()

@router.message(F.text == "/admin")
async def admin_panel(message: Message):
    await message.answer("Admin panel")

@router.message(F.text == "/addfaq")
async def add_faq_start(message: Message, state: FSMContext):
    if message.from_user.id not in ADMINS:
        await message.answer("Faqat adminlar savol qo'sha oladi.")
        return
    await message.answer("Yangi savol matnini yuboring:")
    await state.set_state(AddFAQState.waiting_for_question)

@router.message(AddFAQState.waiting_for_question)
async def add_faq_question(message: Message, state: FSMContext):
    await state.update_data(question=message.text)
    await message.answer("Endi ushbu savolga javobni yuboring:")
    await state.set_state(AddFAQState.waiting_for_answer)

@router.message(AddFAQState.waiting_for_answer)
async def add_faq_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    question = data["question"]
    answer = message.text
    await add_faq(question, answer)
    await message.answer("Savol va javob muvaffaqiyatli qo'shildi!")
    await state.clear()

@router.message(F.text == "/send_message")
async def broadcast_start(message: Message, state: FSMContext):
    if message.from_user.id not in ADMINS:
        await message.answer("Faqat adminlar uchun.")
        return
    await message.answer("Yuboriladigan xabarni (matn, rasm, audio, video, fayl va h.k.) yuboring:")
    await state.set_state(BroadcastState.waiting_for_content)

@router.message(BroadcastState.waiting_for_content)
async def broadcast_content(message: Message, state: FSMContext):
    await state.update_data(broadcast=message)
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Yuborish"), KeyboardButton(text="❌ Bekor qilish")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Xabar quyidagicha ko‘rinadi:\n\n(Tasdiqlash uchun '✅ Yuborish', bekor qilish uchun '❌ Bekor qilish' deb yozing)", reply_markup=markup)
    # Preview
    if message.text:
        await message.answer(message.text)
    elif message.photo:
        await message.answer_photo(message.photo[-1].file_id, caption=message.caption or "")
    elif message.audio:
        await message.answer_audio(message.audio.file_id, caption=message.caption or "")
    elif message.document:
        await message.answer_document(message.document.file_id, caption=message.caption or "")
    elif message.video:
        await message.answer_video(message.video.file_id, caption=message.caption or "")
    else:
        await message.answer("Xabar turi qo‘llab-quvvatlanmaydi.")
    await state.set_state(BroadcastState.waiting_for_confirm)

@router.message(BroadcastState.waiting_for_confirm)
async def broadcast_confirm(message: Message, state: FSMContext):
    data = await state.get_data()
    broadcast = data.get("broadcast")
    if message.text == "✅ Yuborish":
        user_ids = await get_all_user_ids()
        count = 0
        for uid in user_ids:
            try:
                if broadcast.text:
                    await message.bot.send_message(uid, broadcast.text)
                elif broadcast.photo:
                    await message.bot.send_photo(uid, broadcast.photo[-1].file_id, caption=broadcast.caption or "")
                elif broadcast.audio:
                    await message.bot.send_audio(uid, broadcast.audio.file_id, caption=broadcast.caption or "")
                elif broadcast.document:
                    await message.bot.send_document(uid, broadcast.document.file_id, caption=broadcast.caption or "")
                elif broadcast.video:
                    await message.bot.send_video(uid, broadcast.video.file_id, caption=broadcast.caption or "")
                count += 1
            except Exception:
                pass
        await message.answer(f"Xabar {count} foydalanuvchiga yuborildi.", reply_markup=ReplyKeyboardRemove())
        await state.clear()
    elif message.text == "❌ Bekor qilish":
        await message.answer("Xabar yuborish bekor qilindi.", reply_markup=ReplyKeyboardRemove())
        await state.clear()
    else:
        markup = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="✅ Yuborish"), KeyboardButton(text="❌ Bekor qilish")]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await message.answer("Iltimos, '✅ Yuborish' yoki '❌ Bekor qilish' tugmasini bosing.", reply_markup=markup)

@router.message(F.text == "➕ Kanal ulash")
async def add_channel_handler(message: Message, state: FSMContext):
    if message.from_user.id not in ADMINS:
        await message.answer("Faqat adminlar uchun.")
        return
    await message.answer("Kanal username yoki ID sini kiriting:")
    await state.set_state(ChannelState.waiting_for_channel)

@router.message(ChannelState.waiting_for_channel)
async def process_add_channel(message: Message, state: FSMContext):
    await add_channel(message.text)
    await message.answer("Kanal ulandi.")
    await state.clear()

@router.message(F.text == "📋 Ulangan kanallar")
async def list_channels_handler(message: Message):
    if message.from_user.id not in ADMINS:
        await message.answer("Faqat adminlar uchun.")
        return
    channels = await get_channels()
    if not channels:
        await message.answer("Ulangan kanallar yo'q.")
    else:
        await message.answer("Ulangan kanallar:\n" + "\n".join(channels))

@router.message(F.text == "❌ Kanal uzish")
async def remove_channel_handler(message: Message, state: FSMContext):
    if message.from_user.id not in ADMINS:
        await message.answer("Faqat adminlar uchun.")
        return
    await message.answer("Uziladigan kanal username yoki ID sini kiriting:")
    await state.set_state(ChannelState.waiting_for_remove_channel)

@router.message(ChannelState.waiting_for_remove_channel)
async def process_remove_channel(message: Message, state: FSMContext):
    await remove_channel(message.text)
    await message.answer("Kanal uzildi.")
    await state.clear()

def register_admin_handlers(dp):
    dp.include_router(router)


# Bot ishga tushganda jadval yaratilishi uchun
@router.startup()
async def on_startup():
    await create_faq_table()