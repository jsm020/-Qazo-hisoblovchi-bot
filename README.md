# Qazo Hisoblovchi Bot

Telegram uchun qazo namoz hisoblovchi va foydalanuvchilarni boshqaruvchi bot.

## O‘rnatish va ishga tushirish

1. **Klonlash va kutubxonalarni o‘rnatish:**
   ```bash
   git clone <repo-url>
   cd -Qazo-hisoblovchi-bot
   pip install -r requirements.txt
   ```
2. **.env faylini sozlash:**
   - `.env.example` ni nusxa olib `.env` deb nomlang va o‘z ma’lumotlaringizni kiriting.

3. **Botni ishga tushirish:**
   ```bash
   python bot.py
   ```

## Oddiy foydalanuvchi uchun komandalar va funksiyalar

- **/start** yoki **/help** — Botni boshlash va asosiy menyu.
- **Qazolarim** — Qazo namozlaringizni ko‘rish va boshqarish.
- **Ko‘p beriladigan savollar** — FAQ bo‘limi.
- **Namoz vaqtlari** — Namoz vaqtlarini ko‘rish (tashqi saytga havola).
- **Savollar** — Yangi savol yuborish.
- **Qazo hisoblash** — Qazo namozlarni hisoblash.
- **Qazo nima?** — Qazo haqida ma’lumot.
- **Kunlik namoz** — Har kuni o‘qilgan/o‘qilmagan namozlarni belgilash va saqlash.

## Majburiy kanal aʼzolik
- Botdan foydalanish uchun admin tomonidan ulangan kanallarga aʼzo bo‘lish shart. Aʼzo bo‘lmagan foydalanuvchiga kanalga ulanish tugmasi chiqadi.

## Admin panel va komandalar
Faqat adminlar uchun (bazadan olinadi):

- **/stat** yoki **📊 Statistika** — Foydalanuvchilar statistikasi (kunlik, haftalik, oylik).
- **/addfaq** — FAQ bo‘limiga savol-javob qo‘shish.
- **/send_message** — Hammaga xabar yuborish (matn, rasm, audio, fayl, video).
- **/addchannel** — Majburiy kanal ulash.
- **/channels** — Ulangan kanallar ro‘yxati.
- **/removechannel** — Kanalni uzish.
- **/addadmin** — Yangi admin qo‘shish.
- **/removeadmin** — Admin o‘chirish.
- **/admins** — Adminlar ro‘yxati.
- **/addtime** — Xabar yuborish vaqti qo‘shish (HH:MM formatda).
- **/removetime** — Xabar yuborish vaqtini o‘chirish.
- **/times** — Barcha xabar yuborish vaqtlarini ko‘rish.

## Xabar yuborish vaqtlari
- Admin panel orqali istalgan vaqtda xabar yuborish vaqtlarini qo‘shish/o‘chirish mumkin.
- Har bir vaqt uchun bot avtomatik xabar yuboradi (kunlik namoz so‘rovi).

## Texnik ma’lumotlar
- Python 3.10+
- Aiogram 3.x
- APScheduler
- SQLite (default)
- python-dotenv

## Foydalanish bo‘yicha eslatmalar
- Botni to‘g‘ri ishlatish uchun .env faylini to‘ldiring va botni Telegram kanal(lar)ga admin qilib qo‘shing.
- Adminlar bazadan boshqariladi, dastlabki admin .env faylidan olinadi.
- Barcha asosiy funksiyalar uchun tugmalar va komandalar mavjud.

---

Agar savol yoki muammo bo‘lsa, admin paneldan yoki GitHub Issues orqali bog‘laning.