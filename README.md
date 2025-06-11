# Qazo Hisoblovchi Bot

Bu bot foydalanuvchilarga qazo namozlarini hisoblash va monitoring qilishda yordam beradi.

## Texnologiyalar
- Python
- aiogram
- sqlite3

## Ishga tushurish
1. `requirements.txt` faylidan kutubxonalarni o'rnating:
   ```bash
   pip install -r requirements.txt
   ```
2. `config.py` faylida `BOT_TOKEN` ni to'ldiring.
3. Botni ishga tushuring:
   ```bash
   python bot.py
   ```

## Tuzilma
- `bot.py` — asosiy bot kodi
- `handlers/` — handlerlar (user, admin)
- `keyboards/` — klaviaturalar
- `states/` — FSM uchun states
- `database/` — sqlite3 uchun kodlar
- `config.py` — konfiguratsiya