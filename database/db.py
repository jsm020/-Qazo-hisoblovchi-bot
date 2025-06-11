import aiosqlite
from config import DATABASE

async def init_db():
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
        await db.commit()

async def get_qazo(user_id):
    async with aiosqlite.connect(DATABASE) as db:
        cursor = await db.execute("SELECT bomdod, peshin, asr, shom, xufton, vitr FROM qazo WHERE user_id=?", (user_id,))
        row = await cursor.fetchone()
        if row:
            keys = ["bomdod", "peshin", "asr", "shom", "xufton", "vitr"]
            return dict(zip(keys, row))
        return {k: 0 for k in ["bomdod", "peshin", "asr", "shom", "xufton", "vitr"]}

async def update_qazo(user_id, namoz, delta):
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute(f"UPDATE qazo SET {namoz} = MAX({namoz} + ?, 0) WHERE user_id=?", (delta, user_id))
        await db.commit()

async def add_faq(question, answer):
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute("INSERT INTO faq (question, answer) VALUES (?, ?)", (question, answer))
        await db.commit()

async def get_all_faq():
    async with aiosqlite.connect(DATABASE) as db:
        cursor = await db.execute("SELECT id, question FROM faq")
        return await cursor.fetchall()

async def get_faq_answer(faq_id):
    async with aiosqlite.connect(DATABASE) as db:
        cursor = await db.execute("SELECT answer FROM faq WHERE id=?", (faq_id,))
        row = await cursor.fetchone()
        return row[0] if row else None

async def create_faq_table():
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

async def get_all_user_ids():
    async with aiosqlite.connect(DATABASE) as db:
        cursor = await db.execute("SELECT telegram_id FROM users")
        rows = await cursor.fetchall()
        return [row[0] for row in rows]
