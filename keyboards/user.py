from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.db import get_all_faq
import asyncio

def main_menu_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Qazolarim", callback_data="main_qazolarim"),
            InlineKeyboardButton(text="Ko'p beriladigan savollar", callback_data="main_kop_beriladigan_savollar")
        ],
        [
            InlineKeyboardButton(text="Namoz vaqtlari", url="https://prayer-time-tafsoft.vercel.app/"),
            InlineKeyboardButton(text="Savollar", callback_data="main_faq")
        ]
    ])
    return kb

def start_2_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Qazo hisoblash", callback_data="main_hisoblash"),
            InlineKeyboardButton(text="Qazo nima?", callback_data="qazo_nima"),
        ],
        [
            InlineKeyboardButton(text="Menda qazolar yo'q", callback_data="main_menda_qazolar_yok")
        ]
    ])
    return kb

def kop_beriladigan_savollar_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Qazo nima?", callback_data="qazo_nima"),
            InlineKeyboardButton(text="Qazo hisoblash", callback_data="qazo_hisoblash")
        ],
        [
            InlineKeyboardButton(text="Menda qazolar yo'q", callback_data="main_menda_qazolar_yok")
        ]
    ])
    return kb

def qazo_nima_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Qazo hisoblash", callback_data="qazo_hisoblash"),
            InlineKeyboardButton(text="Menda qazolar yo'q", callback_data="main_menda_qazolar_yok")

        ],
    ])
    return kb

def kop_savollar_kb_sync():
    # asyncio.run faqat sync kontekstda ishlaydi, handlerda await get_all_faq ishlating
    savollar = asyncio.run(get_all_faq())
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    for idx, (savol_id, savol_text) in enumerate(savollar, 1):
        kb.inline_keyboard.append([
            InlineKeyboardButton(text=f"{idx}. {savol_text}", callback_data=f"faq_{savol_id}")
        ])
    kb.inline_keyboard.append([
        InlineKeyboardButton(text="Orqaga", callback_data="faq_back")
    ])
    return kb

async def kop_savollar_kb():
    savollar = await get_all_faq()
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    for idx, (savol_id, savol_text) in enumerate(savollar, 1):
        kb.inline_keyboard.append([
            InlineKeyboardButton(text=f"{idx}. {savol_text}", callback_data=f"faq_{savol_id}")
        ])
    kb.inline_keyboard.append([
        InlineKeyboardButton(text="Orqaga", callback_data="faq_back")
    ])
    return kb

def qazo_hisoblash_start_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Hisoblashni boshlash", callback_data="hisoblash_boshlash")],
        [InlineKeyboardButton(text="Orqaga", callback_data="main_menu")]
    ])