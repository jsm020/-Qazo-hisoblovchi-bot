from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def qazo_plus_kb(qazo_dict):
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    for key, label in [
        ("bomdod", "Bomdod"),
        ("peshin", "Peshin"),
        ("asr", "Asr"),
        ("shom", "Shom"),
        ("xufton", "Xufton"),
        ("vitr", "Vitr namozi"),
    ]:
        count = qazo_dict.get(key, 0)
        kb.inline_keyboard.append([
            InlineKeyboardButton(text="-", callback_data=f"qazo_minus_{key}"),
            InlineKeyboardButton(text=f"{label}: {count}", callback_data=f"qazo_count_{key}"),
            InlineKeyboardButton(text="+", callback_data=f"qazo_plus_{key}")
        ])
    kb.inline_keyboard.append([
        InlineKeyboardButton(text="Orqaga", callback_data="qazo_back")
    ])
    return kb


