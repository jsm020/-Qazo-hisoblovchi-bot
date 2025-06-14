import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMINS = os.getenv('ADMINS')
DATABASE = os.getenv('DATABASE', 'database/qazo.db')
