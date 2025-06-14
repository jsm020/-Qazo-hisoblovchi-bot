# Ushbu modul botning ma'lumotlar bazasi bilan bog'liq yordamchi funksiyalarni o'z ichiga oladi
import datetime
import aiosqlite
from config import DATABASE, ADMINS

# ------------- Adminlar bilan ishlash uchun yordamchi funksiyalar -------------
async def add_admin(admin_id):
    # Bazaga yangi admin qo'shishni ta'minlaydi
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute("CREATE TABLE IF NOT EXISTS admins (id INTEGER PRIMARY KEY AUTOINCREMENT, admin_id TEXT UNIQUE)")
        await db.execute("INSERT OR IGNORE INTO admins (admin_id) VALUES (?)", (str(admin_id),))
        await db.commit()

async def remove_admin(admin_id):
    # Bazadan adminni olib tashlaydi
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute("DELETE FROM admins WHERE admin_id=?", (str(admin_id),))
        await db.commit()

async def get_admins():
    # Bazadagi barcha adminlarni ro'yxat sifatida qaytaradi
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute("CREATE TABLE IF NOT EXISTS admins (id INTEGER PRIMARY KEY AUTOINCREMENT, admin_id TEXT UNIQUE)")
        cursor = await db.execute("SELECT admin_id FROM admins")
        rows = await cursor.fetchall()
        return [row[0] for row in rows]


async def init_db():
    # Bazada asosiy jadval(lar)ni yaratib, asosiy adminni kiritadi
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE,
            full_name TEXT,
            username TEXT,
            joined TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        await db.execute('''
        CREATE TABLE IF NOT EXISTS qazo (
            user_id INTEGER,
            bomdod INTEGER DEFAULT 0,
            peshin INTEGER DEFAULT 0,
            asr INTEGER DEFAULT 0,
            shom INTEGER DEFAULT 0,
            xufton INTEGER DEFAULT 0,
            vitr INTEGER DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )''')
        await db.execute('''
        CREATE TABLE IF NOT EXISTS faq (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL
        )
        ''')
        # Bot ishga tushganda asosiy admin ID bazaga qo'shish
        await db.execute("CREATE TABLE IF NOT EXISTS admins (id INTEGER PRIMARY KEY AUTOINCREMENT, admin_id TEXT UNIQUE)")
        await db.execute("INSERT OR IGNORE INTO admins (admin_id) VALUES (?)", (str(6848884650),))
        await db.commit()

# ------------- Statistika bilan ishlashga oid yordamchi funksiya -------------
async def get_stats():
    # Kunlik, haftalik va oylik foydalanuvchi qo'shilish statistikasini qaytaradi
    async with aiosqlite.connect(DATABASE) as db:
        today = datetime.date.today()
        week_ago = today - datetime.timedelta(days=7)
        month_ago = today - datetime.timedelta(days=30)
        # Kunlik
        cursor = await db.execute("SELECT COUNT(*) FROM users WHERE DATE(joined) = ?", (today.isoformat(),))
        daily = (await cursor.fetchone())[0]
        # Haftalik
        cursor = await db.execute("SELECT COUNT(*) FROM users WHERE DATE(joined) >= ?", (week_ago.isoformat(),))
        weekly = (await cursor.fetchone())[0]
        # Oylik
        cursor = await db.execute("SELECT COUNT(*) FROM users WHERE DATE(joined) >= ?", (month_ago.isoformat(),))
        monthly = (await cursor.fetchone())[0]
        return {"daily": daily, "weekly": weekly, "monthly": monthly}

# ------------- Qazo namozlari bilan ishlashga oid yordamchi funksiyalar -------------
async def get_qazo(user_id):
    # Foydalanuvchining qazo sonlarini qaytaradi
    async with aiosqlite.connect(DATABASE) as db:
        cursor = await db.execute("SELECT bomdod, peshin, asr, shom, xufton, vitr FROM qazo WHERE user_id=?", (user_id,))
        row = await cursor.fetchone()
        if row:
            keys = ["bomdod", "peshin", "asr", "shom", "xufton", "vitr"]
            return dict(zip(keys, row))
        return {k: 0 for k in ["bomdod", "peshin", "asr", "shom", "xufton", "vitr"]}

async def update_qazo(user_id, namoz, delta):
    # Berilgan namoz turining qazo sonini yangilaydi
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute(f"UPDATE qazo SET {namoz} = MAX({namoz} + ?, 0) WHERE user_id=?", (delta, user_id))
        await db.commit()

# ------------- FAQ (tez-tez so'raladigan savollar) bilan ishlashga oid yordamchi funksiyalar -------------
async def add_faq(question, answer):
    # FAQ jadvaliga savol va javobni qo'shadi
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute("INSERT INTO faq (question, answer) VALUES (?, ?)", (question, answer))
        await db.commit()

async def get_all_faq():
    # Barcha FAQ elementlarini (faqat ID va savol) olib keladi
    async with aiosqlite.connect(DATABASE) as db:
        cursor = await db.execute("SELECT id, question FROM faq")
        return await cursor.fetchall()

async def get_faq_answer(faq_id):
    # Berilgan FAQ ID bo'yicha javobni qaytaradi
    async with aiosqlite.connect(DATABASE) as db:
        cursor = await db.execute("SELECT answer FROM faq WHERE id=?", (faq_id,))
        row = await cursor.fetchone()
        return row[0] if row else None

async def create_faq_table():
    # Agar FAQ jadvali bo'lmasa, yaratadi
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS faq (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                answer TEXT NOT NULL
            )
        ''')
        await db.commit()

async def save_all_qazo(user_id, qazo_dict):
    # Foydalanuvchining barcha qazo namozlarini birdaniga yangilash funktsiyasi
    print("Qazo ma'lumotlar saqlandi", qazo_dict, user_id)
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute(
            "UPDATE qazo SET bomdod=?, peshin=?, asr=?, shom=?, xufton=?, vitr=? WHERE user_id=?",
            (
                qazo_dict.get("bomdod", 0),
                qazo_dict.get("peshin", 0),
                qazo_dict.get("asr", 0),
                qazo_dict.get("shom", 0),
                qazo_dict.get("xufton", 0),
                qazo_dict.get("vitr", 0),
                user_id
            )
        )
        await db.commit()


# ------------- Kanal bilan ishlashga oid yordamchi funksiyalar -------------
async def add_channel(channel):
    # Bot kuzatib borishi kerak bo'lgan kanallarni bazaga qo'shadi
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute("CREATE TABLE IF NOT EXISTS channels (id INTEGER PRIMARY KEY AUTOINCREMENT, channel TEXT UNIQUE)")
        await db.execute("INSERT OR IGNORE INTO channels (channel) VALUES (?)", (channel,))
        await db.commit()

async def get_channels():
    # Barcha kanallarni bazadan oqib qaytaradi
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute("CREATE TABLE IF NOT EXISTS channels (id INTEGER PRIMARY KEY AUTOINCREMENT, channel TEXT UNIQUE)")
        cursor = await db.execute("SELECT channel FROM channels")
        rows = await cursor.fetchall()
        return [row[0] for row in rows]

async def remove_channel(channel):
    # Berilgan kanaldan botni chiqarib tashlaydi
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute("DELETE FROM channels WHERE channel=?", (channel,))
        await db.commit()

# Qazo namozlari turini tekshirish uchun ruxsat etilgan kalit so'zlar
ALLOWED_NAMOZ = {"bomdod", "peshin", "asr", "shom", "xufton", "vitr"}

async def increment_qazo_if_missed(user_id: int, status_dict: dict):
    # Agar foydalanuvchi namozni o'qimagan bo'lsa, qazo sonini orttiradi
    print("✅ Increment qilishdan oldingi holat:", status_dict)
    async with aiosqlite.connect(DATABASE) as db:
        for namoz in ALLOWED_NAMOZ:
            status = status_dict.get(namoz)
            print(f"⏺️ {namoz}: {status}")
            if status == "oqimadim":
                query = f"UPDATE qazo SET {namoz} = {namoz} + 1 WHERE user_id = ?"
                await db.execute(query, (user_id,))
        await db.commit()
        print("✅ Commit qilindi")

# ------------- Foydalanuvchilar ro'yxati bilan ishlash -------------
async def get_all_user_ids():
    # Barcha foydalanuvchilarning telegram_id ro'yxatini qaytaradi
    async with aiosqlite.connect(DATABASE) as db:
        cursor = await db.execute("SELECT telegram_id FROM users")
        rows = await cursor.fetchall()
        return [row[0] for row in rows]

async def ensure_main_admin():
    # Bot ishga tushganda asosiy admin bazaga qo'shilishi kerak
    main_admin_id = ADMINS[0]
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute("CREATE TABLE IF NOT EXISTS admins (id INTEGER PRIMARY KEY AUTOINCREMENT, admin_id TEXT UNIQUE)")
        await db.execute("INSERT OR IGNORE INTO admins (admin_id) VALUES (?)", (str(main_admin_id),))
        await db.commit()


# ------------- Xabar yuborish vaqtini saqlash va boshqarish -------------
async def get_notify_times():
    # Xabar yuborish vaqtlari jadvallarini qaytaradi
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute("CREATE TABLE IF NOT EXISTS notify_times (hour INTEGER, minute INTEGER)")
        cursor = await db.execute("SELECT hour, minute FROM notify_times")
        return await cursor.fetchall()

async def add_notify_time(hour, minute):
    # Xabar yuborish vaqtini qo'shadi
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute("CREATE TABLE IF NOT EXISTS notify_times (hour INTEGER, minute INTEGER)")
        await db.execute("INSERT INTO notify_times (hour, minute) VALUES (?, ?)", (hour, minute))
        await db.commit()

async def remove_notify_time(hour, minute):
    # Berilgan xabar yuborish vaqtini bazadan olib tashlaydi
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute("DELETE FROM notify_times WHERE hour=? AND minute=?", (hour, minute))
        await db.commit()