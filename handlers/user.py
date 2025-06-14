from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from keyboards.user import main_menu_kb,start_2_kb,qazo_nima_kb, kop_savollar_kb, qazo_hisoblash_start_kb, kunlik_namoz_kb
from keyboards.qazo import qazo_plus_kb
from database.db import get_qazo, get_faq_answer, get_all_faq, increment_qazo_if_missed, update_qazo, save_all_qazo, get_channels
from datetime import datetime

import aiosqlite
from config import DATABASE
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramBadRequest
import logging
logging.basicConfig(level=logging.INFO)

router = Router()

class QazoHisoblashState(StatesGroup):
    waiting_for_years = State()

class KunlikNamozState(StatesGroup):
    waiting_for_namoz = State()

async def check_user_channels(user_id, bot):
    channels = await get_channels()
    not_joined = []
    for channel in channels:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            logging.info(f"Checking channel {channel} for user {user_id}: {member.status}")
            if member.status in ("left", "kicked"):
                not_joined.append(channel)
        except TelegramBadRequest:
            not_joined.append(channel)
            
    return not_joined

@router.message(F.text.in_(["/start", "/help"]))
async def start_cmd(message: Message):
    not_joined = await check_user_channels(message.from_user.id, message.bot)
    if not_joined:
        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=f"Kanalga aʼzo bo‘lish", url=f"https://t.me/{ch.lstrip('@')}")] for ch in not_joined
            ]
        )
        await message.answer("Botdan foydalanish uchun quyidagi kanallarga aʼzo bo‘ling:", reply_markup=markup)
        return
    async with aiosqlite.connect(DATABASE) as db:
        cursor = await db.execute("SELECT * FROM users WHERE telegram_id=?", (message.from_user.id,))
        user = await cursor.fetchone()
        if not user:
            await db.execute("INSERT INTO users (telegram_id, full_name, username) VALUES (?, ?, ?)", (message.from_user.id, message.from_user.full_name, message.from_user.username))
            await db.execute("INSERT INTO qazo (user_id) VALUES (?)", (message.from_user.id,))
            await db.commit()
            await message.answer("Assalomu alaykum! 😊 \n\n Bu bot sizning qazo qilganizni ko‘maklashadi. Keling birinch chi namoz qazo qilganicha namozingiz chi va batta, qancha namoz qazo qilganicha yordam beringiz. Hisoblan uchun pasdagi 'Qazo hisoblan' knopkasidan foydalaning:", reply_markup=start_2_kb())
        else:
            await message.answer("Assalomu alaykum! 😊\n\n Yana siz bilan korishganimizdan xursandmiz. Sizga qanday yordam bera olamiz? Qazo yigimlarini tumanlardam birin tanlang", reply_markup=main_menu_kb())


@router.callback_query(F.data == "qazo_nima")
async def qazo_nima_callback(call: CallbackQuery):
    await call.message.edit_text(
        "Qazo nima?\n\nQazo namozi — o‘z vaqtida o‘qilmay qolgan namozni keyinroq to‘ldirishdir. Batafsil ma’lumot uchun quyidagi tugmalardan foydalaning.",
        reply_markup=qazo_nima_kb()
    )
    await call.answer()

@router.callback_query(F.data == "main_qazolarim")
async def main_qazolarim_callback(call: CallbackQuery):
    qazo = await get_qazo(call.from_user.id)
    text = (
        f"<b>Qazo namozlaringiz:</b>\n"
    )
    await call.message.edit_text(
        text,
        reply_markup=qazo_plus_kb(qazo),
        parse_mode="HTML"
    )
    await call.answer()

@router.callback_query(F.data == "main_kop_beriladigan_savollar")
async def kop_beriladigan_savollar_callback(call: CallbackQuery):
    savollar = await get_all_faq()
    kb = kop_savollar_kb(savollar, page=0)
    await call.message.edit_text(
        "Ko'p beriladigan savollar:",
        reply_markup=kb
    )

@router.callback_query(F.data.startswith("faq_page_"))
async def kop_savollar_page_callback(call: CallbackQuery):
    page = int(call.data.split("_")[-1])
    savollar = await get_all_faq()
    kb = kop_savollar_kb(savollar, page=page)
    await call.message.edit_text(
        "Ko'p beriladigan savollar:",
        reply_markup=kb
    )

@router.callback_query(F.data.startswith("faq_"))
async def faq_answer_callback(call: CallbackQuery):
    faq_id = int(call.data.split("_")[1])
    answer = await get_faq_answer(faq_id)
    if answer:
        await call.message.edit_text(answer)
    else:
        await call.message.edit_text("Javob topilmadi.")

@router.inline_query()
async def faq_inline_query(inline_query: InlineQuery):
    query = inline_query.query.lower()
    savollar = await get_all_faq()
    results = []
    for faq_id, question in savollar:
        if query in question.lower() or not query:
            answer = await get_faq_answer(faq_id)
            results.append(
                InlineQueryResultArticle(
                    id=str(faq_id),
                    title=question,
                    input_message_content=InputTextMessageContent(message_text=answer or "Javob topilmadi.")
                )
            )
    await inline_query.answer(results, cache_time=1)

@router.callback_query(F.data == "main_hisoblash")
async def qazo_hisoblash_start(call: CallbackQuery):
    text = (
        "Qazo namozlari haqida batafsil ma'lumot va video (link yoki fayl) shu yerda bo'ladi.\n\n"
        "Qazo hisoblashni boshlash uchun quyidagi tugmani bosing."
    )
    await call.message.edit_text(text, reply_markup=qazo_hisoblash_start_kb())
    await call.answer()

@router.callback_query(F.data == "hisoblash_boshlash")
async def hisoblash_boshlash_callback(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("Necha yil qazo namozingiz bor? (Faqat son kiriting, masalan: 3)")
    await state.set_state(QazoHisoblashState.waiting_for_years)

@router.message(QazoHisoblashState.waiting_for_years)
async def hisoblash_years_handler(message: Message, state: FSMContext):
    try:
        years = int(message.text)
        if years < 1 or years > 100:
            raise ValueError
    except ValueError:
        await message.answer("Iltimos, faqat 1 dan 100 gacha butun son kiriting!")
        return
    # 1 yil = 365 kun, har bir namoz uchun
    for namoz in ["bomdod", "peshin", "asr", "shom", "xufton", "vitr"]:
        await update_qazo(message.from_user.id, namoz, years * 365)
    await message.answer(f"{years} yil uchun barcha namozlarga qazo qo‘shildi!")
    await state.clear()

@router.callback_query(F.data == "save_qazo")
async def save_qazo_handler(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    qazo_dict = data.get("qazo_dict")
    if not qazo_dict:
        await call.message.answer("Qazo ma'lumotlari topilmadi.")
        return
    await save_all_qazo(call.from_user.id, qazo_dict)
    await call.message.edit_text("Qazo namozlaringiz muvaffaqiyatli saqlandi!")
    await state.clear()

@router.callback_query(F.data.startswith("qazo_plus_"))
async def qazo_plus_handler(call: CallbackQuery):
    namoz = call.data.replace("qazo_plus_", "")
    await update_qazo(call.from_user.id, namoz, 1)
    qazo = await get_qazo(call.from_user.id)
    await call.message.edit_reply_markup(reply_markup=qazo_plus_kb(qazo))
    await call.answer(f"{namoz.capitalize()} uchun 1 ta qazo qo‘shildi.")

@router.callback_query(F.data.startswith("qazo_minus_"))
async def qazo_minus_handler(call: CallbackQuery):
    namoz = call.data.replace("qazo_minus_", "")
    await update_qazo(call.from_user.id, namoz, -1)
    qazo = await get_qazo(call.from_user.id)
    await call.message.edit_reply_markup(reply_markup=qazo_plus_kb(qazo))
    await call.answer(f"{namoz.capitalize()} uchun 1 ta qazo ayrildi.")

@router.callback_query(F.data.startswith("kunlik_"))
async def kunlik_namoz_handler(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    status_dict = data.get("kunlik_status", {})
    logging.info(status_dict)
    parts = call.data.split("_")
    if len(parts) == 3:
        namoz, status = parts[1], parts[2]
        status_dict[namoz] = status
        await state.update_data(kunlik_status=status_dict)
    await call.message.edit_reply_markup(reply_markup=kunlik_namoz_kb(status_dict))
    await call.answer()
@router.callback_query(F.data == "kun_save")
async def kunlik_namoz_save(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    status_dict = data.get("kunlik_status", {})
    logging.info("📤 Saqlanayotgan holat:", status_dict)

    if not status_dict:
        await call.answer("❗Avval biror namoz holatini belgilang", show_alert=True)
        return

    await increment_qazo_if_missed(call.from_user.id, status_dict)
    
    await call.message.edit_text("✅ Kunlik namoz holatingiz muvaffaqiyatli saqlandi!")
    await state.clear()

@router.callback_query(F.data == "main_menu")
async def main_menu_callback(call: CallbackQuery):
    await call.message.edit_text(
        "Assalomu alaykum! 😊\n\nBotimizga qaytganingizdan mamnunmiz! Quyidagi bo‘limlardan birini tanlang",
        reply_markup=main_menu_kb()
    )


def register_user_handlers(dp):
    dp.include_router(router)
