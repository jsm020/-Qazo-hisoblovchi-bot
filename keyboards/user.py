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
            InlineKeyboardButton(text="Qazo hisoblash", callback_data="main_hisoblash")
        ],
        [
            InlineKeyboardButton(text="Menda qazolar yo'q", callback_data="main_menda_qazolar_yok")
        ]
    ])
    return kb

def qazo_nima_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Qazo hisoblash", callback_data="main_hisoblash"),
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
        InlineKeyboardButton(text="Orqaga", callback_data="main_menu")
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
        InlineKeyboardButton(text="Orqaga", callback_data="main_menu")
    ])
    return kb

def kop_savollar_kb(savollar, page=0, per_page=5):
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    start = page * per_page
    end = start + per_page
    for idx, (savol_id, savol_text) in enumerate(savollar[start:end], start=1+start):
        kb.inline_keyboard.append([
            InlineKeyboardButton(text=f"{idx}. {savol_text}", callback_data=f"faq_{savol_id}")
        ])
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="⬅️ Oldingi", callback_data=f"faq_page_{page-1}"))
    if end < len(savollar):
        nav.append(InlineKeyboardButton(text="Keyingi ➡️", callback_data=f"faq_page_{page+1}"))
    if nav:
        kb.inline_keyboard.append(nav)
    kb.inline_keyboard.append([InlineKeyboardButton(text="Orqaga", callback_data="main_menu")])
    return kb

def qazo_hisoblash_start_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Hisoblashni boshlash", callback_data="hisoblash_boshlash")],
        [InlineKeyboardButton(text="Orqaga", callback_data="main_menu")]
    ])

def kunlik_namoz_kb(status_dict=None):
    if status_dict is None:
        status_dict = {}
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    for key, label in [
        ("bomdod", "Bomdod"),
        ("peshin", "Peshin"),
        ("asr", "Asr"),
        ("shom", "Shom"),
        ("xufton", "Xufton"),
        ("vitr", "Vitr namozi"),
    ]:
        status = status_dict.get(key, None)
        if status == "oqidim":
            btn_text = "✅ O'qidim"
            next_status = "oqimadim"
        else:
            btn_text = "❌ O'qiy olmadim"
            next_status = "oqidim"
        kb.inline_keyboard.append([
            InlineKeyboardButton(text=label, callback_data="none"),
            InlineKeyboardButton(text=btn_text, callback_data=f"kunlik_{key}_{next_status}")
        ])
    kb.inline_keyboard.append([
        InlineKeyboardButton(text="Saqlash", callback_data="kunlik_save")
    ])
    return kb